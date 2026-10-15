# La web: estructura, diseño y cómo agregar una sección

La web son páginas HTML estáticas, una por unidad del curso, que comparten `docs/assets/estilo.css` y
`docs/assets/app.js`. Plotly y las fuentes vienen de CDN. No hay framework ni paso de compilación, a propósito:
GitHub Pages lo sirve tal cual y cualquier integrante del equipo puede editarlo.

| Página | Contenido |
|---|---|
| `docs/index.html` | portada, introducción, problema, mapa, objetivos, recorrido |
| `docs/descriptiva/` | Unidad 1: población y muestra, tabla de variables, TDF y gráficas de R, exploración |
| `docs/datos/` | origen, preparación, descargas |
| `docs/equipo/` | integrantes y docente |

El menú está **repetido en cada HTML**: al agregar una página, actualizarlo en todas. Las subpáginas usan rutas
relativas (`../assets/`, `../img/`, `../data/`). `app.js` marca la página actual con `<body data-pagina="…">`.

## Datos que consume

| Archivo | Lo genera | Lo usa |
|---|---|---|
| `docs/data/resumen.json` | `scripts/datos_dashboard.py` | cifras de la portada, gráficos de "Exploración", mapa interactivo |
| `docs/data/variables.json` | `scripts/tabla_variables.py` | tarjetas de clases y tabla filtrable de variables |
| `docs/data/tdf/*.csv`, `docs/img/r/*.png` | scripts de `R/` | tablas y gráficas de `/descriptiva/` (`leerCSV()` + `tabla()` de `app.js`) |
| `docs/img/*` | fotos reales, `mapa.py`, `proyecto_qgis.py`, Google Flow | imágenes |

`resumen.json` trae agregados (conteos, histograma, muestras de 6 000 puntos), no la base: así la web pesa
poco. Si un gráfico nuevo necesita otro agregado, agregarlo en `datos_dashboard.py`, no calcularlo en el navegador.

## Agregar una página o una sección

- **Página nueva** (p. ej. `/inferencial/`): copiar `docs/datos/index.html` como esqueleto, cambiar
  `data-pagina`, la cabecera y el contenido, y reemplazar el `<span class="pronto">` del menú por un enlace en
  todas las páginas. Agregar la tarjeta en "Recorrido del proyecto" de la portada.
- **Sección dentro de una página**: patrón `<section class="cap" id="..."><div class="cab rev"><span class="num">NN</span><h2>…</h2></div>…</section>`.
- **Gráfica de R + tabla**: en `/descriptiva/`, la función `bloque()` arma figura + tabla CSV + lectura.
- **Gráficos interactivos**: usar `base()`, `bar()` y `cfg` de `app.js` para heredar colores y tipografía.

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
