# Cómo usar esta plantilla

Esta carpeta es la estructura de un company brain: la base de conocimiento de una empresa en Markdown, preparada para que Claude Code la lea antes de hacer cualquier trabajo. No tiene datos de ninguna empresa. Todo lo que va entre `[corchetes]` es un hueco que hay que rellenar.

## Qué hay dentro

| Pieza | Para qué sirve |
|---|---|
| `CLAUDE.md` | Reglas que Claude cumple siempre en esta carpeta: qué es la empresa, el mapa del brain, cómo se reparte el trabajo entre agentes y cómo se escribe cada documento |
| `README.md` | Índice general por departamento (se regenera solo) |
| `NN-Departamento/README.md` | Qué va en cada departamento, qué no y de dónde sale |
| `NN-Departamento/_plantillas/` | Cómo se guarda cada tipo de documento de ese departamento |
| `INGESTA/` | Bandeja de entrada: aquí se dejan los documentos nuevos |
| `.claude/skills/ingesta-informacion/` | Skill que convierte lo que hay en `INGESTA/` en documentos de departamento |
| `.claude/skills/_plantilla-skill/` | Estructura para crear una skill nueva |
| `.claude/agents/_plantilla-agente.md.ejemplo` | Estructura para crear un agente especializado por departamento |

## Cómo se usa

1. Copia esta carpeta entera y cámbiale el nombre: `brain-[tu-empresa]`.
2. Ábrela en la pestaña **Code** de la app de Claude.
3. Pega el prompt de abajo.
4. Cuando tengas documentos de la empresa (presentaciones, web en PDF, propuestas), déjalos en `INGESTA/` y escribe `/ingesta-informacion`.

## Prompt de arranque

```
Esta carpeta es una plantilla de company brain. Úsala como referencia para montar el de mi empresa, sin cambiar su estructura.
1. Lee primero COMO-USAR-ESTA-PLANTILLA.md, CLAUDE.md, el README.md de cada departamento y sus _plantillas/.
2. Entrevístame haciéndome UNA pregunta cada vez y espera mi respuesta antes de seguir. Cubre lo que piden las plantillas de 01-Direccion, 06-Ventas y 07-Marca-y-Diseno, y lo básico de 08-Operaciones-y-Equipo. Si respondo "no lo sé", apúntalo como [PENDIENTE] y sigue.
3. Con mis respuestas, crea los documentos en su departamento siguiendo la plantilla que les corresponde: mismo nombre de archivo (NN-tema.md), misma cabecera y mismas secciones. No inventes nada para rellenar un hueco.
4. Rellena el CLAUDE.md y los README.md de departamento con los datos de mi empresa y borra los comentarios de plantilla. No toques las carpetas _plantillas.
5. Regenera los índices con el script de la skill de ingesta.
6. Termina con una tabla: documento creado, departamento y huecos [PENDIENTE] que han quedado.
Antes de crear nada, dime tu plan.
```

## Reglas que conviene no romper

- **No cambies la estructura de carpetas ni la numeración.** Así todos los brains se parecen y los agentes y skills funcionan igual en todos.
- **Un dato, un archivo.** Si algo ya está escrito, se enlaza; no se copia.
- **Lo que no se sabe se marca como `[PENDIENTE]`.** Un brain con huecos marcados es mejor que uno con datos inventados.
- **Nada de datos de contacto de clientes, contraseñas ni credenciales.** Ver "Qué NO entra en el brain" en `CLAUDE.md`.

## Notas técnicas

- El script de conversión de PDF y el de índices necesitan Python y [`uv`](https://docs.astral.sh/uv/). Si no los tienes, Claude puede convertir los documentos sin scripts y actualizar los índices a mano; díselo.
- Las plantillas de agente y de skill acaban en `.ejemplo` a propósito: con extensión `.md` Claude Code las cargaría como si fueran un agente o una skill de verdad. Para crear uno, cópialas con el nombre definitivo (`.claude/agents/[nombre].md` o `.claude/skills/[nombre]/SKILL.md`).
