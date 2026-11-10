# CLAUDE.md

Este archivo le dice a Claude Code cómo trabajar en este repositorio. Se carga en cada conversación que se abra en esta carpeta, así que tiene que ser corto: qué es esto, dónde está cada cosa y qué reglas se cumplen siempre. El detalle vive en los `README.md` de cada carpeta y en los documentos.

<!-- PLANTILLA: sustituye todo lo que va entre [corchetes] y borra estos comentarios cuando termines. -->

## Qué es este repositorio

No es un repositorio de código. Es la documentación de negocio de [EMPRESA] ([qué hace, para quién y dónde, en una frase]), organizada como una base de conocimiento en Markdown: un archivo por tema, agrupados por departamento. El contenido sale de [fuentes principales: dossier, presentaciones, web, entrevistas con el equipo… con su fecha].

Toda la documentación está en [idioma]. Mantenla así.

## Estructura

- `NN-Nombre/` en la raíz: una carpeta por departamento (`01-Direccion` a `08-Operaciones-y-Equipo`). Los departamentos grandes se dividen en subcarpetas en minúsculas con guiones (por ejemplo, `04-Producto/validacion-con-clientes/`).
- `README.md` en cada carpeta: una cabecera escrita a mano (qué va aquí, qué no, fuentes y convenciones) encima de una lista `## Contenido` que se genera sola. El `README.md` de la raíz tiene la tabla de departamentos, también generada.
- `_plantillas/` dentro de cada departamento: la estructura que debe seguir cada tipo de documento. Antes de crear un documento nuevo, mira si hay plantilla y úsala. Las plantillas no son documentos y no salen en los índices.
- `INGESTA/`: bandeja de entrada para documentos nuevos sin procesar. Después de cada ingesta debe quedar vacía, pero no se borra.
- `.claude/agents/`: los agentes especializados por departamento. `_plantilla-agente.md.ejemplo` es la estructura para crear uno nuevo.
- `.claude/skills/`: las skills del proyecto. `ingesta-informacion/` convierte lo que hay en `INGESTA/` en documentos de departamento. `_plantilla-skill/` es la estructura para crear una skill nueva.

## Orquestación de agentes (OBLIGATORIO)

La sesión principal hace de orquestadora: clasifica cada tarea por departamento, delega el trabajo al agente que tiene ese departamento, recoge los resultados y los integra. No hace ella misma el trabajo de un departamento que tenga agente.

### Enrutado por departamento

Se invocan con la herramienta Agent y el `subagent_type` indicado. El alcance y los límites de cada agente viven en su propio archivo; esta tabla solo enruta.

| Departamento | Carpeta | Agente | Cuándo usarlo |
|---|---|---|---|
| [Departamento] | `[NN-Nombre]/` | `[nombre-del-agente]` ([definición](.claude/agents/[nombre-del-agente].md)) | [Tipos de tarea que le tocan] |
| Ingesta | `INGESTA/` | skill `/ingesta-informacion` | Material nuevo que hay que convertir en documentos de departamento |
| Cualquier otro departamento | su `NN-Nombre/` | `general-purpose`, con el encargo limitado a esa carpeta | Hasta que ese departamento tenga agente propio |
| Búsqueda entre departamentos (solo lectura) | varios | `Explore` | Encontrar dónde vive un dato antes de enrutar el trabajo |

Cuando se añada un agente a `.claude/agents/`, se añade su fila aquí. Nunca se copia su descripción.

### Pasos

1. Clasifica la tarea en uno o varios departamentos con la tabla.
2. Un departamento: lanza su agente.
3. Varios departamentos independientes: lanza un agente por departamento, en paralelo, en un solo mensaje.
4. Varios departamentos dependientes (B necesita lo que produce A): lanza A y pasa su resultado de forma explícita en el encargo de B.
5. Integra: junta los resultados, resuelve los solapes para que cada dato quede en un solo archivo y responde al usuario.

### Contrato de delegación

1. **La orquestadora recoge.** Nunca termina un turno con "esperando a los agentes": espera a todos, integra y responde.
2. **Cada encargo se entiende solo.** El agente solo sabe lo que pone su encargo: objetivo, archivos o carpeta que leer, lo que ya está descartado y cómo es el resultado terminado.
3. **Lo que dice un agente es un informe, no una prueba.** Comprueba los archivos que haya escrito antes de decir que está hecho.
4. **Los agentes no escriben fuera de su carpeta.** Los cambios entre departamentos pasan por la orquestadora.

## Ingesta (`/ingesta-informacion`)

Usa la skill siempre que haya material nuevo en `INGESTA/`. Su `SKILL.md` es la referencia del proceso y de la tabla de departamentos. Resumen:

1. Convertir a Markdown (los PDF con el script de la skill; Word, PowerPoint y HTML con `markitdown`). Imágenes, vídeos y hojas de cálculo no se convierten: se mueven a su departamento con su nombre original.
2. Decidir el departamento de cada capítulo por su contenido, no por su título.
3. Repartir en un archivo por sección, con la cabecera estándar (ver abajo).
4. Verificar que no se ha perdido texto.
5. Regenerar los índices `README.md`.
6. Enseñar la lista de originales que se van a borrar de `INGESTA/` y borrarlos solo con confirmación.

## Formato de cada documento

```markdown
# Título del documento

> Departamento: [Departamento] · Origen: [documento o persona de la que sale] ([fecha])

[Contenido]
```

Si existe plantilla para ese tipo de documento en `_plantillas/`, se sigue su estructura.

## Convenciones de edición

- **Una sola fuente por dato: la información NUNCA se duplica.** Cada dato vive en un único archivo. Todo lo demás (otros documentos, agentes, skills, este CLAUDE.md) enlaza a ese archivo en lugar de copiar su contenido. Cuando un dato cambia, solo se edita su archivo. Si un documento nuevo repite algo ya documentado, se actualiza el archivo existente en lugar de crear una copia. Si encuentras un dato duplicado, avisa y propón cuál se queda como fuente.
- **Nombres:** archivos en minúsculas, sin tildes y con guiones (`NN-tema.md`). Carpetas de departamento: `NN-Nombre`. Subcarpetas: minúsculas con guiones. Un departamento nuevo (`09-...`) solo si nada encaja, y avisando al usuario.
- **La ingesta conserva el texto completo:** no se resume ni se reescribe el contenido de las fuentes. Si un material nuevo actualiza un documento, se actualiza ese archivo indicando la fecha y el origen nuevos.
- **Cifras que no cuadran:** cuando dos fuentes dan cifras distintas, se dejan las dos con su origen. No se reconcilian.
- **Documentos superados:** se marcan `SUPERSEDED (fecha)` al principio y se conservan como histórico. Nunca se usan como regla vigente.
- **`[SUPUESTO]`** marca cifras que salen de un plan o de una estimación, no de datos medidos.
- **Huecos:** lo que no se sabe se escribe como `[PENDIENTE: qué falta y quién lo sabe]`. Nunca se inventa para rellenar.
- **Citar siempre:** cualquier respuesta sobre la empresa dice de qué archivo sale cada dato. Si algo no está en el brain, se dice ("no está en el brain").
- [Convención propia de la empresa, por ejemplo: cómo se escriben los precios, vocabulario obligatorio o prohibido, género o tratamiento.]

## Qué NO entra en el brain

- Datos de contacto de clientes o prospectos (teléfonos, emails, perfiles personales). Viven en [CRM].
- Contraseñas, claves de API, credenciales e identificadores internos.
- [Datos personales del equipo, nóminas, documentación legal sensible… lo que decida la empresa.]

El contenido es interno y confidencial: no se sube a servicios externos.
