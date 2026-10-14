# La web: estructura, diseño y cómo agregar una sección

`docs/index.html` es un único archivo HTML estático: CSS en `<style>`, JS en `<script>`, Plotly desde CDN y
las fuentes desde Google Fonts. No hay framework ni paso de compilación, a propósito: GitHub Pages lo sirve
tal cual y cualquier integrante del equipo puede editarlo.

## Datos que consume

| Archivo | Lo genera | Lo usa |
|---|---|---|
| `docs/data/resumen.json` | `scripts/datos_dashboard.py` | cifras de la portada, gráficos de "Exploración", mapa interactivo |
| `docs/data/variables.json` | `scripts/tabla_variables.py` | tarjetas de clases y tabla filtrable de variables |
| `docs/img/*` | fotos reales, `mapa.py`, `proyecto_qgis.py`, Google Flow | imágenes |

`resumen.json` trae agregados (conteos, histograma, muestras de 6 000 puntos), no la base: así la web pesa
poco. Si un gráfico nuevo necesita otro agregado, agregarlo en `datos_dashboard.py`, no calcularlo en el navegador.

## Secciones (orden del curso)

`#inicio` (portada) → `01 #introduccion` → `02 #problema` → `03 #mapa` → `04 #objetivos` → `05 #poblacion`
→ `06 #variables` → `07 #exploracion` → `08 #datos` → `09 #equipo`. El orden replica la estructura que pide
el docente (ver `AGENTS.md`).

Para agregar una sección (por ejemplo, las TDF de la lección 5):

1. Copiar el patrón `<section class="cap" id="..."><div class="cab rev"><span class="num">NN</span><h2>…</h2></div>…</section>`
   y ubicarla en el orden del curso; renumerar los `num` siguientes.
2. Agregar el enlace en `<nav>` con el mismo número.
3. Si tiene gráficos, usar `base()`, `bar()` y `cfg` del script para heredar colores y tipografía.

## Sistema de diseño

Dirección: editorial de revista científica sobre un tema oscuro "basalto". Todo color sale de los tokens de
`:root`:

- Superficies `--page`, `--surface-1`, `--surface-2`; tinta `--text-primary/secondary`, `--muted`.
- Acento `--magma` (botones, números de capítulo, letras capitulares) y `--oro` (rótulos en mono).
- Series de datos `--series-1..3` y la `rampa` azul para ordinales: es la paleta validada para daltonismo,
  compartida con `mapa.py` y `proyecto_qgis.py`. Máximo 3 colores categóricos por gráfico.
- Tipografía: Fraunces (títulos), Instrument Sans (texto), JetBrains Mono (cifras, fórmulas, rótulos).

Comportamiento: las clases `.rev` aparecen al hacer scroll (`IntersectionObserver`), las cifras de portada
cuentan hacia arriba, y todo respeta `prefers-reduced-motion`. Debajo de 1100 px se oculta el menú de
capítulos y debajo de 900 px las grillas pasan a una o dos columnas.

## Al editar

- Revisar en local con `python -m http.server` (ver [Regenerar y publicar](../workflows/regenerar-y-publicar.md)).
- Las imágenes con `loading="lazy"` no aparecen en capturas de página completa: no es un error.
- Las fotos del equipo son 400×400 recortadas de originales del usuario; las ilustrativas llevan la nota
  "generada con IA" en el pie o en el footer.
