# Regenerar productos y publicar la web

Cada producto sale de un script. Todos leen la base limpia, así que el orden importa.

```bash
# Los CSV crudos se leen de data/raw/crudos (junction al respaldo en Google Drive); se puede pasar otra carpeta.
python -I scripts/limpiar.py                     # -> data/earthchem_limpio.csv.gz
python -I scripts/datos_dashboard.py             # -> docs/data/resumen.json
python scripts/tabla_variables.py                # -> data/tabla_variables.xlsx, docs/data/variables.json
python -I scripts/mapa.py                        # -> data/gis/mapa_ubicacion.gpkg, docs/img/mapa_ubicacion.png
"/c/Program Files/QGIS 3.44.8/bin/python-qgis-ltr.bat" scripts/proyecto_qgis.py   # -> shp/, .qgz (A4 y A3), PNG, PDF A4/A3, zip
                                                 # -> data/gis/mapa_ubicacion.qgz, docs/img/mapa_qgis.png
```

- `tabla_variables.py` e `informe.py` importan a sus vecinos (`limpiar`, `datos_dashboard`): correrlos
  **sin** `-I`, que quita la carpeta del script del `sys.path`.
- `tabla_variables.py` necesita los crudos porque saca el instrumento de las columnas `Method`.
- `mapa.py` descarga los países de Natural Earth (`PAISES_URL`) en cada corrida: necesita internet.

## Estadística en R

El docente exige la estadística en R. Desde la raíz, con R 4.6 y los paquetes `e1071` y `openxlsx`:

```bash
Rscript R/01_cualitativas.R    # TDF nominales y ordinales, barras y circular
Rscript R/02_discretas.R       # año de publicación y número de analitos
Rscript R/03_continuas.R       # SiO2, MgO, Cr: agrupación, outliers, estrato, error de agrupación
Rscript R/04_muestreo.R        # L3: muestras aleatoria, sistemática y estratificada (seed 2026) -> data/muestras/
# después: python scripts/informe_muestreo.py  -> docs/informe_muestreo.pdf
```

Cada script escribe tres cosas: PNG en `docs/img/r/`, CSV en `docs/data/tdf/` (las tablas que muestra
`/descriptiva/`) y un Excel en `R/salidas/`. Las funciones comunes están en `R/funciones.R`; `tdf_continua()` sin
argumentos reproduce la plantilla del curso y con `lim = limites_iqr(x)` arma la TDF con clases abiertas.

- `read.csv()` directo sobre el `.gz` se cae (segfault) con R 4.6 en Windows: usar `leer_base()`, que abre con
  `gzfile(..., encoding = "UTF-8")`.
- `Rscript -e` con código de varias líneas también falló: escribir el código en un archivo `.R`.
- Para agregar una variable continua: sumarla a `VARIABLES` en `03_continuas.R` (`log = TRUE` si es traza) y
  agregar su pestaña y su texto de lectura en `docs/descriptiva/index.html` (objeto `CONT`).

## Informe del proyecto

`python scripts/informe.py` (al final, después de R: usa sus gráficas) genera `docs/informe_proyecto.docx` con
python-docx y luego abre Word por COM (PowerShell) para actualizar el índice y exportar `docs/informe_proyecto.pdf`.
Sin Microsoft Word queda solo el .docx con el índice vacío. Tiene tres partes: la base de datos (cifras calculadas
de la base), la estadística descriptiva y la documentación técnica (texto fijo: actualizarlo si cambia el stack).

## El mapa y QGIS

`mapa.py` escribe un GeoPackage en WGS84 con cuatro capas para QGIS (`contorno`, `paises`, `graticula`,
`etiquetas_grilla`) más `muestras`, con nombres de campo cortos y sin espacios (`CAMPOS`), pensados para la
tabla de atributos de QGIS. Después dibuja el PNG con matplotlib en proyección Robinson (`ESRI:54030`).

`proyecto_qgis.py` corre con el Python de QGIS (PyQGIS), no con el Python normal. Arma el proyecto con la
misma simbología (colores en `GRUPOS`), una composición A4 (título, leyenda, escala, norte, coordenadas,
fuente) y la exporta a `docs/img/mapa_qgis.png`. Primero copia el GeoPackage a shapefiles (`data/gis/shp/`) con `gdal.VectorTranslate` y OGR SQL (`CAST` fija el
ancho de cada campo; con el dialecto SQLite por defecto se pierde la geometría y el .dbf pesa 100 MB). El proyecto
usa esos shapefiles y guarda rutas relativas: el `.qgz` viaja con `shp/` y `UCE.png`, y así va en
`docs/mapa_qgis_shapefiles.zip`. La clase `Lamina` arma la misma lámina en A4 y A3 (todo × raíz de 2).

Detalles que costaron:
- La composición sigue la plantilla del docente (`referencias_curso/QGIS/1.- Mapa de Ubicacion/Plantilla1.qpt`):
  cuadrícula con coordenadas en el borde, leyenda, norte, escala gráfica y membrete con el logo `data/gis/UCE.png`.
  Usa EPSG:4326 (no Robinson) porque en Robinson los meridianos no tocan el marco y la cuadrícula queda sin rótulos.
- La escala gráfica en un mapa en grados: no fijar elipsoide ni `setMapUnitsPerScaleBarUnit`; QGIS ya convierte
  grados a km sobre el ecuador.
- El aviso `ERROR 6: The PNG driver does not support update access` al exportar es inofensivo.

## Imágenes ilustrativas

`docs/img/hero.jpg`, `andes.jpg`, `barco.jpg` y `nucleos.jpg` se generaron con Google Flow mediante la skill
`gflow-cli` (`gflow image t2i "<prompt>" --model nano2 --aspect 16:9`) y se optimizaron a JPEG calidad 80.
Antes de generar, `gflow auth status` debe responder "Flow session verified". No correr dos generaciones en
paralelo con el mismo perfil.

## Publicar

GitHub Pages sirve `main:/docs`. Un `git push` que toque `docs/` actualiza la web en 1–3 minutos; el estado se
ve con `gh api repos/crisrumiguano-art/geoquimica-earthchem-ml/pages/builds/latest --jq .status`.

Para revisar localmente antes de publicar: `python -m http.server 8765 -d docs` y abrir `http://localhost:8765/`
(abrir `index.html` con doble clic no funciona: la página carga sus datos con `fetch`).

## Archivos pesados

GitHub rechaza archivos > 100 MB y advierte desde 50 MB. Los más grandes del repo son
`data/gis/mapa_ubicacion.gpkg` (~35 MB) y `data/earthchem_limpio.csv.gz` (~26 MB). No agregar los crudos.
