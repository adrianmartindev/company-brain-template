"""Comprueba que el texto original ha llegado a los .md generados.

Uso: python check_coverage.py <texto_original.txt> <archivo.md | carpeta> [...]

Compara el recuento de palabras de 4+ letras. Una perdida por debajo del ~2% suele
ser cabeceras de tablas repetidas por salto de pagina (fusionadas a proposito).
Por encima, hay que revisar las palabras que faltan.
"""
import re, sys, pathlib, collections

raw = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
raw = re.sub(r"CAP[ÍI]TULO \d+", "", raw)  # la marca de capitulo se convierte en H1 a proposito
out = ""
for arg in sys.argv[2:]:
    p = pathlib.Path(arg)
    for f in ([p] if p.is_file() else sorted(p.rglob("*.md"))):
        out += f.read_text(encoding="utf-8") + "\n"

words = lambda t: collections.Counter(w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ]{4,}", t))
a, b = words(raw), words(out)
missing = {k: v - b[k] for k, v in a.items() if v > b[k]}
lost = sum(missing.values()) / max(sum(a.values()), 1) * 100
print(f"Palabras original: {sum(a.values())} · generadas: {sum(b.values())} · faltan: {sum(missing.values())} ({lost:.1f}%)")
print("Mas frecuentes que faltan:", sorted(missing.items(), key=lambda x: -x[1])[:30])
sys.exit(1 if lost > 3 else 0)
