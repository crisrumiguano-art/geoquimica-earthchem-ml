# La web: estructura, diseño y cómo agregar una sección

HTML estático, una página por unidad, con `docs/assets/estilo.css` y `docs/assets/app.js` compartidos. Plotly y
fuentes por CDN. Sin framework ni compilación: GitHub Pages lo sirve tal cual.

| Página | Contenido |
|---|---|
| `docs/index.html` | portada, planteamiento (una redacción continua), mapa (QGIS / Python / interactivo, PDF A4 y A3, zip QGIS), objetivos (general + 3 con imagen), recorrido |
| `docs/descriptiva/` | 01 población y muestra · 02 tabla de variables · 03 cualitativas · 04 discretas · 05 continuas · 06 exploración · 07 cómo leer el código R |
| `docs/datos/` | origen, preparación, descargas (informes, mapas, base, QGIS) |
| `docs/equipo/` | 5 integrantes con contacto, docente |

El menú está **repetido en cada HTML**: al agregar una página, actualizarlo en todas (`<span class="pronto">` -> enlace).

## Datos que consume

| Archivo | Lo genera | Lo usa |
|---|---|---|
| `data/resumen.json` | `datos_dashboard.py` | cifras de portada, exploración, mapa interactivo |
| `data/variables.json` | `tabla_variables.py` | tarjetas de clases y tabla de variables (con «Nombre en español») |
| `data/tdf/*.csv`, `img/r/*.png` | scripts de `R/` | tablas y gráficas de `/descriptiva/` |
| `data/codigo_r.json` | `codigo_r.py` | panel «Código R» de cada gráfica y botón «Ver el código paso a paso» |

## Componentes de `app.js`

- **Aviso académico**: barra flotante inferior en todas las páginas, se cierra con × y vuelve al recargar.
- **Botón «Código R»**: un `MutationObserver` agrega el botón a cada `figure.grafica` con imagen de `img/r/`;
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
