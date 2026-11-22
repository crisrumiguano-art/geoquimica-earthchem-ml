# La web: estructura, diseño y cómo agregar una sección

HTML estático, una página por unidad, con `docs/assets/estilo.css` y `docs/assets/app.js` compartidos. Plotly y
fuentes por CDN. Sin framework ni compilación: GitHub Pages lo sirve tal cual.

| Página | Contenido |
|---|---|
| `docs/index.html` | **portada única**: aviso académico grande, título y cifras; 01 Introducción (origen y preparación de la base), 02 Planteamiento (una redacción), 03 Mapa (QGIS, Python, interactivo; PDF A4/A3 y zip), 04 Objetivos, 05 Recorrido, 06 Tecnologías, 07 Descargas |
| `docs/descriptiva/` | 01 población y muestra · 02 tabla de variables · 03 cualitativas · 04 discretas · 05 continuas · 06 exploración · 07 cómo leer el código R |
| `docs/inferencial/`, `regresion/`, `ml/` | Unidades 2, 3 y 4, con tabla resumen y enlace al documento R de cada modelo |
| `docs/conclusiones/` | objetivo general, objetivos 1–3 y limitaciones (texto fijo, última página del menú) |
| `docs/equipo/` | 5 integrantes y docente |
| `docs/datos/` | solo redirige a `/#introduccion` (enlaces viejos) |

El menú y el pie **se generan en `assets/app.js`** (`MENU` y `pie`): cada HTML solo trae `<nav id="nav">` (con el logo,
por si no hay JS) y `<footer data-nota="…">`. Para agregar o renombrar una página se edita solo `MENU`. En el celular el
menú se desliza de lado (borde derecho desvanecido) y lleva a la vista la página actual.

## Datos que consume

| Archivo | Lo genera | Lo usa |
|---|---|---|
| `data/resumen.json` | `datos_dashboard.py` | cifras de portada, exploración, mapa interactivo |
| `data/variables.json` | `tabla_variables.py` | tarjetas de clases y tabla de variables (con «Nombre en español») |
| `data/tdf/*.csv`, `img/r/*.png` | scripts de `R/` | tablas y gráficas de `/descriptiva/` |
| `data/codigo_r.json` | `codigo_r.py` | panel «Código R» de cada gráfica y botón «Ver el código paso a paso» |
| `rpubs/*.html` | `rpubs.py`, `inferencial.py`, `regresion.py` | copias locales de los documentos de RPubs, que abre el visor |
| `img/variables/*.jpg`, `creditos.json` | a mano (Wikimedia Commons) | fotos reales de las tarjetas de variable; autor y licencia al pie |

## Componentes de `app.js`

- **Aviso académico**: en grande (`.aviso-grande`, en el HTML) en la portada; en las demás páginas `app.js` agrega una franja
  compacta en `.hero-in`. Sin botón de cerrar (pedido del docente).
- **Visor de RPubs** (`abrirRPubs`): todo enlace a `rpubs.com/rosemeri/<slug>` abre la copia local `rpubs/<archivo>.html`
  en un `<dialog>` modal (`closedby="any"` con respaldo para Safari). Slug → archivo: se quita `desc-` y `-` pasa a `_`.
- **Tarjetas de variable** (`tarjeta()` en el script de `/descriptiva/`): foto real + tipo + botón al RPubs. Reemplazan
  las gráficas de R en cualitativas y discretas; en continuas encabezan el panel.
- **Botón «Código R»** (gráficas de R que siguen en la página): un `MutationObserver` lo agrega a cada `figure.grafica` de `img/r/`;
  `panelCodigo()` abre el código simple de ese PNG con botón Copiar. El JSON se pide con `cache: "no-cache"`.
- **`resaltarR()`**: resaltado de sintaxis R propio (un regex; clases `.r-c/s/k/b/n/f/o`, colores tipo VS Code);
  también colorea `<pre class="r-mini">` de la sección 07.
- `leerCSV()` + `tabla()` para las TDF; `base()`, `bar()`, `cfg` para Plotly; `pestanas()` para pestañas.

## Diseño

Tema oscuro "basalto": tokens en `:root` (`--page`, `--surface-1/2`, `--magma`, `--oro`, `--series-1..3`), Fraunces +
Instrument Sans + JetBrains Mono. Paleta de datos validada para daltonismo, la misma en `mapa.py` y `proyecto_qgis.py`;
máximo 3 colores categóricos. `.rev` aparece al hacer scroll; respeta `prefers-reduced-motion`.

## Al editar

- Una clase CSS nueva: buscar antes si ya existe (`.tres` existía y rompió la grilla de objetivos; se usa `.trio`).
- El panel de código va **dentro** de la figura: en `.bloque` un hermano nuevo desarma la grilla de 2 columnas.
- Imágenes `loading="lazy"` no salen en capturas de página completa. Fotos del equipo: reales, 400×400.
