# Geoquímica de rocas: estadística y machine learning

Análisis estadístico y de machine learning sobre 159 760 análisis químicos de roca total (EarthChem / PetDB).

- **Web y dashboard:** https://crisrumiguano-art.github.io/geoquimica-earthchem-ml/
- **Base limpia:** [`data/earthchem_limpio.csv.gz`](data/earthchem_limpio.csv.gz) (75 columnas)
- **Informe del proyecto** (base de datos, estadística y documentación técnica): [PDF](docs/informe_proyecto.pdf) · [Word](docs/informe_proyecto.docx)
- **Estadística descriptiva en R:** [`R/`](R/) · por qué así: [`R/analisis_agrupacion_outliers.md`](R/analisis_agrupacion_outliers.md)
- **Mapa de ubicación:** proyecto QGIS [`data/gis/mapa_ubicacion.qgz`](data/gis/mapa_ubicacion.qgz)
- **Documentación:** [openwiki/quickstart.md](openwiki/quickstart.md) · reglas para agentes en [AGENTS.md](AGENTS.md)

```bash
pip install -r requirements.txt
python scripts/limpiar.py <carpeta_con_csv_crudos>   # regenera la base limpia
python scripts/datos_dashboard.py                    # regenera los datos del dashboard
```

Orden completo y comandos de QGIS en [openwiki/workflows/regenerar-y-publicar.md](openwiki/workflows/regenerar-y-publicar.md).

Datos: Astromaterials Data Synthesis / EarthChem PetDB, descargados el 13-oct-2026, CC BY 4.0.
