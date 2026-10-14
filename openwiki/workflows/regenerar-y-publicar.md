# Regenerar productos y publicar la web

Cada producto sale de un script. Todos leen la base limpia, así que el orden importa.

```bash
CRUDA="C:/Users/dalem/Downloads/quimica"          # CSV crudos de EarthChem (no están en el repo)

python -I scripts/limpiar.py "$CRUDA"            # -> data/earthchem_limpio.csv.gz
python -I scripts/datos_dashboard.py             # -> docs/data/resumen.json
python scripts/tabla_variables.py "$CRUDA"       # -> data/tabla_variables.xlsx, docs/data/variables.json
python scripts/reporte_pdf.py                    # -> docs/reporte_base_datos.pdf
python -I scripts/mapa.py                        # -> data/gis/mapa_ubicacion.gpkg, docs/img/mapa_ubicacion.png
"/c/Program Files/QGIS 3.44.8/bin/python-qgis-ltr.bat" scripts/proyecto_qgis.py
                                                 # -> data/gis/mapa_ubicacion.qgz, docs/img/mapa_qgis.png
```

- `tabla_variables.py` y `reporte_pdf.py` importan a sus vecinos (`limpiar`, `datos_dashboard`): correrlos
  **sin** `-I`, que quita la carpeta del script del `sys.path`.
- `tabla_variables.py` necesita los crudos porque saca el instrumento de las columnas `Method`.
- `reporte_pdf.py` usa las fuentes Arial de `C:/Windows/Fonts`: solo corre en Windows tal como está.
- `mapa.py` descarga los países de Natural Earth (`PAISES_URL`) en cada corrida: necesita internet.

## El mapa y QGIS

`mapa.py` escribe un GeoPackage en WGS84 con cuatro capas para QGIS (`contorno`, `paises`, `graticula`,
`etiquetas_grilla`) más `muestras`, con nombres de campo cortos y sin espacios (`CAMPOS`), pensados para la
tabla de atributos de QGIS. Después dibuja el PNG con matplotlib en proyección Robinson (`ESRI:54030`).

`proyecto_qgis.py` corre con el Python de QGIS (PyQGIS), no con el Python normal. Arma el proyecto con la
misma simbología (colores en `GRUPOS`), una composición A4 (título, leyenda, escala, norte, coordenadas,
fuente) y la exporta a `docs/img/mapa_qgis.png`. Guarda rutas relativas: el `.qgz` debe viajar junto al `.gpkg`.

Detalles que costaron:
- QGIS no logra colocar etiquetas junto a los polos en Robinson; por eso las longitudes se rotulan sobre el
  ecuador (`cuad = 8` en `etiquetas_grilla`).
- El aviso `ERROR 6: The PNG driver does not support update access` al exportar es inofensivo.

## Imágenes ilustrativas

`docs/img/hero.jpg`, `andes.jpg`, `barco.jpg` y `nucleos.jpg` se generaron con Google Flow mediante la skill
`gflow-cli` (`gflow image t2i "<prompt>" --model nano2 --aspect 16:9`) y se optimizaron a JPEG calidad 80.
Antes de generar, `gflow auth status` debe responder "Flow session verified". No correr dos generaciones en
paralelo con el mismo perfil.

## Publicar

GitHub Pages sirve `main:/docs`. Un `git push` que toque `docs/` actualiza la web en 1–3 minutos; el estado se
ve con `gh api repos/DalemberV/geoquimica-earthchem-ml/pages/builds/latest --jq .status`.

Para revisar localmente antes de publicar: `python -m http.server 8765 -d docs` y abrir `http://localhost:8765/`
(abrir `index.html` con doble clic no funciona: la página carga sus datos con `fetch`).

## Archivos pesados

GitHub rechaza archivos > 100 MB y advierte desde 50 MB. Los más grandes del repo son
`data/gis/mapa_ubicacion.gpkg` (~35 MB) y `data/earthchem_limpio.csv.gz` (~26 MB). No agregar los crudos.
