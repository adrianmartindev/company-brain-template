"""Reparte un Markdown en archivos por seccion dentro de las carpetas de departamento.

Uso: python split_sections.py <doc.md> <raiz del proyecto> <mapa.json> "<origen>"

mapa.json asigna cada capitulo (H1, numerado por orden de aparicion desde 1) a una
carpeta de departamento relativa a la raiz del proyecto, p. ej. {"1": "01-Direccion", "2": "04-Producto/roadmap"}.
Con la clave "*" se asigna todo el documento a una carpeta. Los capitulos sin
asignar se ignoran y se listan al final.

Cada H2 de un capitulo pasa a ser un archivo NN-slug.md (H2 -> H1, H3 -> H2). Un
capitulo sin H2 se guarda como un unico archivo. La numeracion continua a partir
del prefijo mas alto que ya exista en la carpeta, y nunca se sobrescribe un archivo.
El texto previo al primer H2 (fuentes, contexto) se guarda en <carpeta>/README.md
si este aun no existe.
"""
import json, re, sys, pathlib, unicodedata

DOC, ROOT, MAP, ORIGIN = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), json.loads(pathlib.Path(sys.argv[3]).read_text()), sys.argv[4]
body = DOC.read_text(encoding="utf-8")

def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60].rstrip("-") or "documento"

def next_num(folder):
    nums = [int(m.group(1)) for p in folder.glob("*.md") if (m := re.match(r"(\d+)-", p.name))]
    return max(nums, default=0) + 1

def dept_label(rel):
    return re.sub(r"^\d+-", "", rel.split("/")[0]).replace("-", " ")

# capitulos = bloques que empiezan por H1; si no hay H1, el documento entero es un capitulo
parts = re.split(r"(?m)^(?=# )", body)
chapters = [p for p in parts if p.startswith("# ")] or [f"# {DOC.stem}\n\n{body}"]
written, skipped = [], []
for idx, ch in enumerate(chapters, 1):
    title = ch.split("\n", 1)[0][2:].strip()
    rel = MAP.get(str(idx), MAP.get("*"))
    if not rel:
        skipped.append(f"{idx}. {title}"); continue
    folder = ROOT / rel
    folder.mkdir(parents=True, exist_ok=True)
    rest = re.sub(r"^_Capítulo \d+\._\s*", "", ch.split("\n", 1)[1].strip() if "\n" in ch else "")
    secs = re.split(r"(?m)^(?=## )", rest)
    intro, secs = secs[0].strip(), [s for s in secs[1:] if s.strip()]
    if not secs:
        secs, intro = [f"## {title}\n\n{intro}"], ""
    if not (folder / "README.md").exists():
        extra = f"\n{intro}\n" if intro else ""
        (folder / "README.md").write_text(f"# {title}\n\nOrigen: {ORIGIN}.\n{extra}", encoding="utf-8")
    n = next_num(folder)
    for sec in secs:
        head, _, content = sec.partition("\n")
        stitle = head[3:].strip()
        clean_title = re.sub(r"^\d+(\.\d+)*\.?\s+", "", stitle)
        path = folder / f"{n:02d}-{slug(clean_title)}.md"
        while path.exists():
            n += 1; path = folder / f"{n:02d}-{slug(clean_title)}.md"
        content = re.sub(r"(?m)^### ", "## ", content.strip())
        ref = f"\"{title}\", sección {stitle.split(' ')[0]}" if re.match(r"\d", stitle) else f"\"{title}\""
        path.write_text(f"# {clean_title}\n\n> Departamento: {dept_label(rel)} · Origen: {ORIGIN}, {ref}.\n\n{content}\n", encoding="utf-8")
        written.append(str(path.relative_to(ROOT))); n += 1

print("Escritos:", *written, sep="\n  ")
if skipped:
    print("Capitulos sin carpeta asignada (no escritos):", *skipped, sep="\n  ")
