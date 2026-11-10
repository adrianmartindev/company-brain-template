"""Regenera los indices README.md de las carpetas de departamento a partir de lo que hay en disco.

Uso: python build_index.py <raiz del proyecto>

- Solo trata como departamentos las carpetas de la raiz con patron NN-Nombre
  (INGESTA, .claude y el resto se ignoran).
- En cada carpeta con contenido conserva el texto del README por encima de
  "## Contenido" (titulo, fuentes, contexto) y reescribe la lista debajo.
- En el README raiz conserva el texto por encima de "## Índice" y reescribe la tabla
  por departamento y subcarpeta.
- Las carpetas que empiezan por "_" (como _plantillas) se ignoran.
- Los archivos que no son .md (imagenes, videos, excels) tambien se listan.
"""
import re, sys, pathlib

ROOT = pathlib.Path(sys.argv[1])
SKIP = {".DS_Store", "README.md"}

def h1(p):
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "): return line[2:].strip()
    return p.stem

def label(name):
    return re.sub(r"^\d+-", "", name).replace("-", " ").capitalize()

def files(d):
    return sorted(p for p in d.iterdir() if p.is_file() and p.name not in SKIP and not p.name.startswith("."))

def subdirs(d):
    return sorted(p for p in d.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))

def count(d):
    # Las carpetas que empiezan por "_" (p. ej. _plantillas) no cuentan como documentos
    return sum(1 for p in d.rglob("*") if p.is_file() and p.name not in SKIP and not p.name.startswith(".")
               and not any(part.startswith("_") for part in p.relative_to(d).parts))

def docs(n):
    return f"{n} documento" if n == 1 else f"{n} documentos"

def write_readme(d):
    readme = d / "README.md"
    head = f"# {label(d.name)}\n"
    if readme.exists():
        old = readme.read_text(encoding="utf-8")
        head = old.split("\n## Contenido", 1)[0].rstrip() + "\n"
        if not re.search(r"(?m)^# ", head):
            head = f"# {label(d.name)}\n\n" + head
    for s in subdirs(d):
        write_readme(s)
    items = [f"- [{h1(s / 'README.md')}]({s.name}/README.md) ({docs(count(s))})" for s in subdirs(d)]
    for p in files(d):
        items.append(f"- [{h1(p)}]({p.name})" if p.suffix == ".md" else f"- [{p.name}]({p.name}) (archivo original)")
    readme.write_text(f"{head}\n## Contenido\n\n" + "\n".join(items) + "\n", encoding="utf-8")

rows = []
for dept in (d for d in subdirs(ROOT) if re.match(r"\d{2}-", d.name)):
    write_readme(dept)
    if files(dept):
        rows.append(f"| [{dept.name}]({dept.name}/README.md) | {h1(dept / 'README.md')} | {len(files(dept))} |")
    for s in subdirs(dept):
        rows.append(f"| [{dept.name}]({dept.name}/{s.name}/README.md) | {h1(s / 'README.md')} | {count(s)} |")

# El README raiz conserva todo lo que hay por encima de "## Indice" y reescribe la tabla
root_readme = ROOT / "README.md"
root_head = "# Company brain\n\nDocumentacion de empresa organizada por departamento, en Markdown y con un archivo por seccion.\n"
if root_readme.exists():
    root_head = root_readme.read_text(encoding="utf-8").split("\n## Índice", 1)[0].rstrip() + "\n"
root_readme.write_text(
    f"{root_head}\n## Índice\n\n"
    "| Departamento | Contenido | Documentos |\n|---|---|---|\n" + "\n".join(rows) + "\n",
    encoding="utf-8")
print(f"Indices regenerados: {len(rows)} entradas en {ROOT / 'README.md'}")
