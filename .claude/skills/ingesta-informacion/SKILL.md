---
name: ingesta-informacion
description: Ingesta la documentación nueva que se deja en la carpeta INGESTA del company brain y la ordena en las carpetas de departamento de la raíz del proyecto. Convierte PDFs, Word, PowerPoint, HTML y texto a Markdown con un archivo por sección, los reparte por departamento, mantiene imágenes, vídeos y excels en su formato, verifica que no se pierde texto y regenera los índices README. Usar cuando el usuario diga "/ingesta-informacion", "ingesta esto", "ordena INGESTA", "he subido documentos a INGESTA" o similar.
argument-hint: "[archivo o carpeta concreta dentro de INGESTA]"
---

# Ingesta de información

Objetivo: que todo lo que entre en `INGESTA/` acabe en formato `.md` dentro de las carpetas de departamento de la raíz del proyecto (`01-Direccion/`, `02-Finanzas/`...), con índices al día. Las imágenes, los vídeos y los excels se conservan tal cual. `INGESTA/` es solo la bandeja de entrada: al terminar debe quedar vacía.

Rutas (relativas a la raíz del proyecto):
- Bandeja de entrada: `INGESTA/` (aquí se dejan los documentos nuevos)
- Destino: carpetas `NN-Nombre/` en la raíz del proyecto, con el índice general en `README.md` de la raíz
- Scripts: `.claude/skills/ingesta-informacion/scripts/`
- Temporales: el scratchpad de la sesión, nunca dentro del proyecto

## Estructura de departamentos

| Carpeta | Qué va aquí |
|---|---|
| `01-Direccion` | Qué es la empresa, visión, problema y solución, público objetivo, diferencial, principios, metas |
| `02-Finanzas` | Plan de negocio, modelo financiero, escenarios, unit economics, costes, supuestos, riesgos |
| `03-Estrategia-y-Mercado` | Tamaño de mercado, competencia, landscape, benchmarks, fuentes de research |
| `04-Producto` | `producto-y-planificacion/` (visión de producto o servicio, alcance, roadmap, backlog, especificaciones) y `validacion-con-clientes/` (entrevistas, observaciones, síntesis) |
| `05-Marketing` | `estrategia-y-canales/` (estrategia, canales, contenidos, SEO, KPIs, partnerships) y una subcarpeta por plan de periodo (`plan-<mes>-<aaaa>/`) |
| `06-Ventas` | Precios, embudo, playbook comercial, demo, objeciones, outreach, CRM |
| `07-Marca-y-Diseno` | Historia de marca, logo, paleta, tipografía, voz y tono, taglines, aplicaciones visuales |
| `08-Operaciones-y-Equipo` | Equipo, rutinas, herramientas internas, registro de decisiones |

Antes de crear un documento, mira si su departamento tiene una plantilla en `_plantillas/` para ese tipo de documento. Si la hay, ordena el contenido con sus secciones, pero sin resumir ni reescribir el texto de la fuente.

Usa siempre estas carpetas. Crea una subcarpeta nueva (nombre en minúsculas con guiones) cuando un documento grande forme un bloque propio dentro de un departamento, como un plan de marketing de un mes concreto. Crea un departamento nuevo (`09-...`) solo si el contenido no encaja en ninguno, y díselo al usuario.

## Proceso

### 1. Detectar qué hay que ingestar

Si el usuario pasa un archivo o carpeta, usa eso. Si no, todo lo que haya dentro de `INGESTA/` (salvo `.DS_Store`), incluidas subcarpetas. Lista lo encontrado por tipo antes de empezar.

| Tipo | Tratamiento |
|---|---|
| `.pdf` | Convertir con `pdf_to_md.py` |
| `.docx`, `.pptx`, `.html`, `.htm`, `.epub`, `.rtf`, `.odt` | Convertir con `markitdown <archivo> > salida.md`. Si `markitdown` no está instalado, instálalo con `uv tool install markitdown` o, si no hay `uv`, lee el documento y pásalo a Markdown a mano |
| `.txt`, `.md` | Leer directamente y darles formato Markdown |
| Imágenes (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`, `.heic`), vídeos (`.mp4`, `.mov`, `.avi`, `.webm`, `.mkv`) y excels (`.xlsx`, `.xls`, `.xlsm`, `.csv`, `.numbers`) | NO convertir. Mirar el contenido (ver la imagen, las pestañas del excel o el nombre y contexto del vídeo) para decidir el departamento y moverlos desde `INGESTA/` a esa carpeta de departamento con el nombre original |

Si un PDF o un Word trae imágenes dentro que aportan información (diagramas, capturas), extráelas a la misma carpeta de departamento y enlázalas desde el `.md`.

### 2. Convertir a Markdown

```bash
PY=$(bash .claude/skills/ingesta-informacion/scripts/setup_env.sh)
"$PY" .claude/skills/ingesta-informacion/scripts/pdf_to_md.py INGESTA/<archivo>.pdf <scratchpad>/<archivo>.md
```

Si no hay Python o `uv` y no se pueden instalar, lee el PDF directamente y pásalo a Markdown a mano, respetando los mismos encabezados (H1 por capítulo, H2 por sección). En ese caso, sigue los pasos 4 a 6 a mano: un archivo por sección con la cabecera estándar, comparar a ojo que no falta texto y actualizar las listas `## Contenido`.

El script deja también `<archivo>.md.raw.txt` con el texto plano original, que se usa en la verificación. Imprime cuántos H1 y H2 detecta: cada H1 es un capítulo y cada H2 una sección.

Revisa el resultado antes de seguir: lee el principio de cada capítulo y alguna tabla. Si los encabezados no salen como `#` / `##` (por ejemplo, el PDF no tiene marcas de capítulo), arréglalos en el `.md` temporal para que cada bloque temático sea un H1 y cada apartado un H2. Corrige a mano lo que el script no resuelva (palabras partidas, listas mal detectadas).

### 3. Decidir departamentos

Lee el contenido de cada capítulo (o del documento entero si es corto) y asigna una carpeta según la tabla de arriba. Clasifica por el contenido, no por el título. Escribe el mapa en el scratchpad:

```json
{"1": "01-Direccion", "2": "02-Finanzas", "4": "04-Producto/validacion-con-clientes"}
```

Las claves son el número de orden del H1 (empezando en 1) y las rutas son relativas a la raíz del proyecto. Usa `{"*": "<carpeta>"}` si todo el documento va a un único sitio. Si un documento no tiene un departamento claro, pregunta al usuario antes de colocarlo.

### 4. Repartir por secciones

```bash
"$PY" .claude/skills/ingesta-informacion/scripts/split_sections.py <scratchpad>/<archivo>.md . <scratchpad>/mapa.json "<origen, p. ej. presentación inversores (12/11/2026)>"
```

Cada H2 se convierte en `NN-slug.md`, con su título como H1 y una línea `> Departamento · Origen` debajo. La numeración sigue al último número que ya haya en la carpeta y nunca sobrescribe archivos. Si el script avisa de capítulos sin carpeta, complétalos en el mapa y vuelve a lanzarlo solo para esos.

Si el contenido nuevo duplica o actualiza un documento que ya existe, no lo dupliques: actualiza el archivo existente indicando la nueva fecha y el origen, y avisa al usuario.

### 5. Verificar

```bash
"$PY" .claude/skills/ingesta-informacion/scripts/check_coverage.py <scratchpad>/<archivo>.md.raw.txt <archivos o carpetas generados>
```

Una pérdida por debajo del ~2% suele ser normal (cabeceras de tabla repetidas por salto de página que se fusionan a propósito). Si pasa del 3%, el script sale con error: revisa las palabras que faltan y recupera el contenido antes de seguir. Para archivos convertidos con markitdown, guarda antes su texto plano (`markitdown` sin limpiar) y compáralo igual.

### 6. Regenerar índices

```bash
"$PY" .claude/skills/ingesta-informacion/scripts/build_index.py .
```

Solo toca las carpetas `NN-Nombre` de la raíz. Reescribe la sección `## Contenido` de cada `README.md` (lo que hay encima se conserva) y la tabla `## Índice` del `README.md` raíz. Ignora las carpetas que empiezan por `_`.

### 7. Limpiar los originales

Los originales convertidos a `.md` (PDF, Word, etc.) no se quedan en `INGESTA/`: el usuario quiere toda la información en `.md`. Una vez superada la verificación, enséñale la lista de originales que se van a borrar y bórralos cuando lo confirme. No se van a la papelera, así que pide la confirmación siempre. Las imágenes, los vídeos y los excels nunca se borran (ya se habrán movido a su departamento). Deja la carpeta `INGESTA/` vacía pero no la borres.

### 8. Resumen al usuario

Termina con una tabla: archivo original, tipo, departamento y carpeta de destino, nº de `.md` generados y % de cobertura. Añade las decisiones de clasificación que se puedan discutir y lo que haya que revisar a mano.

## Reglas

- Todo en español, igual que el resto de la documentación.
- Nombres de archivo en minúsculas, sin tildes y con guiones (`NN-slug.md`); las carpetas de departamento siguen el patrón `NN-Nombre`.
- No resumas ni reescribas el contenido: la ingesta conserva el texto completo, solo cambia el formato y el orden.
- Los datos de la documentación son internos y confidenciales: no los subas a ningún servicio externo.
