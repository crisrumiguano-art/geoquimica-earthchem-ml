# Regenerar productos y publicar la web

Todo lee la base limpia: el orden importa.

```bash
python -I scripts/limpiar.py            # crudos (data/raw/crudos) -> data/earthchem_limpio.csv.gz
python -I scripts/datos_dashboard.py    # -> docs/data/resumen.json
python scripts/tabla_variables.py       # -> data/tabla_variables.xlsx, docs/data/variables.json (lee crudos: Method)
python -I scripts/mapa.py               # -> data/gis/mapa_ubicacion.gpkg, docs/img/mapa_ubicacion.png (internet: Natural Earth)
"/c/Program Files/QGIS 3.44.8/bin/python-qgis-ltr.bat" scripts/proyecto_qgis.py   # shp, .qgz A4+A3, PNG, PDF, zip
# R (ver abajo), y al final:
python scripts/codigo_r.py              # -> docs/data/codigo_r.json + R/graficos/*.R
python scripts/rpubs.py                 # -> R/rpubs/*.Rmd + docs/rpubs/*.html (rmarkdown + pandoc, ~3 min)
python scripts/inferencial.py           # U2 -> R/inferencial, docs/rpubs/inf_*, docs/img/inferencial, inferencial.json
python scripts/regresion.py             # U3 -> R/regresion, docs/rpubs/reg_*, docs/img/regresion, regresion.json
/c/Users/dalem/venv-geoml/Scripts/python.exe scripts/notebooks.py   # U4: escribe y ejecuta notebooks/*.ipynb
python scripts/informe_muestreo.py      # -> docs/informe_muestreo.docx/.pdf (tras R/04)
python scripts/informe.py               # -> docs/informe_proyecto.docx/.pdf (Word por COM)
```

`tabla_variables.py`, `informe*.py` y `codigo_r.py` importan a sus vecinos: correrlos **sin** `-I`.

## Estadística en R

R 4.6 + `e1071` y `openxlsx`. Ejecutable: `"/c/Program Files/R/R-4.6.1/bin/Rscript.exe"` (no está en el PATH).

| Archivo | Rol |
|---|---|
| `R/funciones.R` + `01_cualitativas.R`, `02_discretas.R`, `03_continuas.R` | regeneran **todo** en bucle: PNG en `docs/img/r/`, CSV en `docs/data/tdf/`, Excel en `R/salidas/` |
| `R/04_muestreo.R` | L3, simple y sin funciones (seed 2026, n = 1 061) -> `data/muestras/`, `Muestreo.xlsx` |
| `R/05_paso_a_paso.R` | SiO2 y ambiente tectónico al estilo de la plantilla; comprueba que da lo mismo que `funciones.R` |
| `R/graficos/NN_*.R` | **generados**: un script simple por gráfico, sin funciones propias (lo que se muestra y explica) |
| `R/rpubs/NN_*.Rmd` | **generados** desde `R/graficos/`: un R Markdown por variable (formato RPubs del proyecto modelo) |

El código simple sale de las plantillas de `scripts/codigo_simple.py`. Cada plantilla debe producir el **mismo PNG
byte a byte** que el bucle: al tocarlas, extraer los 15 scripts a una carpeta vacía con `data/`, correrlos y comparar
con `cmp`. Las amplitudes redondas se leen de `docs/data/tdf/`.

`rpubs.py` parte cada script por sus marcas `# ---- N. Título ----`: no cambiarlas en `codigo_simple.py` sin
revisar `TEXTOS` y `DOCUMENTOS`. Necesita `rmarkdown`, `knitr` y pandoc (instalado por winget).

Los generadores de U2/U3 renderizan con `clean = FALSE` para copiar las figuras de `docs/rpubs/<doc>_files/` a
`docs/img/...` y luego borran esa carpeta. Cada documento guarda un CSV resumen (chunk oculto `guardar`) que se junta
en `docs/data/inferencial.json` / `regresion.json` para la tabla de la web. Antes de publicar, armar una hoja de
contactos con PIL y mirar todas las figuras (ejes cortados, curvas fuera de escala, puntos extremos que aplastan).

Trampas: `read.csv()` sobre el `.gz` se cae en Windows (usar `gzfile(..., encoding = "UTF-8")`); `Rscript -e` multilínea
falla (escribir un `.R`). Comentarios didácticos: estilo `# QUÉ HACE / RECIBE / DEVUELVE` y notas cortas por línea; al
cambiar solo comentarios, verificar con `parse(keep.source = FALSE)` que el código quedó idéntico.

Variable continua nueva: sumarla a `VARIABLES` en `03_continuas.R`, a `CONT` en `codigo_simple.py` y a `ORDEN` en
`codigo_r.py`, y su pestaña en `docs/descriptiva/index.html`.

## El mapa y QGIS

`proyecto_qgis.py` (PyQGIS) copia el GeoPackage a shapefiles (`gdal.VectorTranslate`, dialecto OGR SQL con `CAST` de
anchos; SQLite pierde la geometría y engorda el .dbf) y arma la lámina con la clase `Lamina` en A4 y A3 (× √2).

- SRC del mapa **EPSG:4087** (equidistante cilíndrica, metros): escala, barra y cuadrícula coinciden. En EPSG:4326 la
  escala usa el grado de latitud y no cuadra (objetado por el docente).
- Cuadrícula y rótulos **en metros** cada 2 500 000 m (`PASO`), como la plantilla UTM; barra con punto de miles.
- Escalas redondas en `PAPELES`: A4 1:150 M, A3 1:110 M; el ancho del marco se calcula y se calibra con `mapa.scale()`.
  1:100 M no entra en A3.
- Membrete: plantilla `Plantilla1.qpt` del docente, logos `UCE.png` y `MINAS.png` (PR #5 de Jules), sin el docente.
- Rutas relativas: el `.qgz` viaja con `shp/` y los logos en `docs/mapa_qgis_shapefiles.zip`.
- `ERROR 6: The PNG driver does not support update access` al exportar: inofensivo.

## Publicar

GitHub Pages sirve `main:/docs`; un push actualiza en 1–3 min. Estado:
`gh api repos/crisrumiguano-art/geoquimica-earthchem-ml/pages/builds/latest --jq .status`. Esperar con un bucle
`until` sobre ese comando (no `sleep` encadenados). Pages cachea 10 min: el usuario debe recargar con Ctrl + F5.

Local: `python -m http.server 8765 -d docs` (doble clic en `index.html` no funciona: usa `fetch`).

## Archivos pesados

Límite de GitHub 100 MB. Los mayores: `data/gis/mapa_ubicacion.gpkg` (~35 MB), `data/earthchem_limpio.csv.gz`
(~26 MB), shapefiles (~28 MB). `data/earthchem_limpio.csv` (descomprimido, 90 MB) está en `.gitignore`.
