"""Convierte un PDF a Markdown limpio.

Uso: python pdf_to_md.py <entrada.pdf> <salida.md>

Pasos: extraccion con pymupdf4llm (conserva tablas y encabezados), reparacion de
ligaduras "fi"/"fl" perdidas, eliminacion de numeros de pagina, union de lineas
partidas, deteccion de listas, normalizacion de encabezados y fusion de tablas
cortadas por salto de pagina.
"""
import re, sys
import pymupdf, pymupdf4llm

SRC, DST = sys.argv[1], sys.argv[2]

text = pymupdf4llm.to_markdown(SRC)
raw = "\n".join(page.get_text() for page in pymupdf.open(SRC))

# --- 1. Ligaduras perdidas: reconstruir desde el texto plano de PyMuPDF ---
raw_words = set(re.findall(r"[\wÀ-ÿ]+", raw))
fix = {}
for w in raw_words:
    for lig, rep in (("fi", "f"), ("fl", "f"), ("ffi", "f"), ("ff", "f")):
        if lig in w:
            broken = w.replace(lig, rep)
            if broken != w and broken not in raw_words:
                fix.setdefault(broken, w)
if fix:
    pat = re.compile(r"(?<![\wÀ-ÿ])(" + "|".join(sorted(map(re.escape, fix), key=len, reverse=True)) + r")(?![\wÀ-ÿ])")
    text = pat.sub(lambda m: fix[m.group(1)], text)

# --- 2. Quitar numeros de pagina ---
lines = [l for l in text.split("\n") if not re.fullmatch(r"\s*\d{1,3}\s*", l)]

# --- 3. Bloques: separados por >=2 lineas en blanco; items dentro del bloque por 1 ---
def kind(l):
    s = l.strip()
    if s.startswith("|"): return "table"
    if re.match(r"#{1,6} ", s) or re.match(r"\*\*CAP[ÍI]TULO \d+\*\*", s): return "heading"
    if s.startswith("#"): return "cont"  # hashtags al inicio de linea = continuacion
    return "text"

blocks, cur, blank, in_code = [], [], 0, False
for l in lines:
    if l.strip().startswith("```"):
        in_code = not in_code
        cur.append(("raw", l)); blank = 0; continue
    if in_code:
        cur.append(("raw", l)); continue
    if not l.strip():
        blank += 1; continue
    k = kind(l)
    if cur and blank >= 2 and k == "text" and cur[-1][0] == "text" and re.match(r"[a-záéíóúñü]", l.strip()):
        pass  # salto de pagina en mitad de un parrafo
    elif cur and blank >= 2:
        blocks.append(cur); cur = []
    elif cur and blank == 1:
        cur.append(("sep", ""))
    cur.append((k, l.rstrip()))
    blank = 0
if cur: blocks.append(cur)

def render(block):
    items, last_raw = [], ""
    for k, l in block:
        if k == "sep": continue
        s = l.strip()
        if k == "raw":
            items.append(["raw", l]); continue
        if k == "table":
            if items and items[-1][0] == "table":
                items[-1][1] += "\n" + s
            else:
                items.append(["table", s])
            continue
        if k == "heading":
            items.append(["heading", s]); continue
        last = items[-1] if items else None
        if last and last[0] == "text":
            plain = re.sub(r"[*_`]", "", last_raw)
            if (k == "cont" or re.match(r"[a-záéíóúñü(,;.)]", s)
                    or len(plain) >= 95 or (len(plain) >= 78 and not plain.endswith((":", ".")))):
                last[1] += " " + s; last_raw = s; continue
        items.append(["text", s]); last_raw = s
    texts = [v for t, v in items if t == "text"]
    listify = (len(texts) >= 2 and not any(re.match(r"(\d+[.)]|[-*•]) ", v) for v in texts)
               and not any(t in ("table", "raw") for t, _ in items))
    chunks, buf = [], []
    for t, v in items:
        if t == "text":
            v = re.sub(r"\s{2,}", " ", v).replace("** **", " ").replace("_ _", " ")
            if listify:
                buf.append("- " + v); continue
        if buf: chunks.append("\n".join(buf)); buf = []
        chunks.append(v)
    if buf: chunks.append("\n".join(buf))
    return "\n\n".join(chunks)

body = "\n\n".join(render(b) for b in blocks)

# --- 4. Encabezados: capitulo -> H1, seccion -> H2, subseccion -> H3 ---
body = re.sub(r"\*\*CAP[ÍI]TULO (\d+)\*\*\s*\n+#+ (.+)",
              lambda m: f"# {m.group(2).replace('**', '').strip()}\n\n_Capítulo {m.group(1)}._", body)
body = re.sub(r"(?m)^#### \*\*(.+?)\*\*\s*$", lambda m: "## " + m.group(1).replace("** **", " ").strip(), body)
body = re.sub(r"(?m)^##### \*\*(.+?)\*\*\s*$", r"### \1", body)
body = re.sub(r"(?m)^(#+ .*)$", lambda m: m.group(1).replace("**", "").replace("  ", " "), body)
body = re.sub(r"(?m)^(\d+\. .+)\n\n(?=\d+\. )", r"\1\n", body)
body = re.sub(r"(?m)^(\d+\. .+)\n\n(?=\d+\. )", r"\1\n", body)

# --- 5. Tablas partidas por salto de pagina: quitar la cabecera repetida ---
pat = re.compile(r"(\n(\|[^\n]*\|)\n(\|(?:---\|)+)\n(?:\|[^\n]*\|\n)*?)\n+\2\n\3\n")
while (new := pat.sub(lambda m: m.group(1), body)) != body:
    body = new
body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"

open(DST, "w", encoding="utf-8").write(body)
open(DST + ".raw.txt", "w", encoding="utf-8").write(raw)  # para check_coverage.py
print(f"{DST}: {body.count(chr(10))} lineas, {len(re.findall(r'(?m)^# ', body))} H1, {len(re.findall(r'(?m)^## ', body))} H2")
