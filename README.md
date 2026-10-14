# Geoquímica de rocas: estadística y machine learning

Análisis estadístico y de machine learning sobre 159 760 análisis químicos de roca total (EarthChem / PetDB).

- **Web y dashboard:** https://dalemberv.github.io/geoquimica-earthchem-ml/
- **Base limpia:** [`data/earthchem_limpio.csv.gz`](data/earthchem_limpio.csv.gz) (74 columnas)
- **Reporte de la base (PDF):** [`docs/reporte_base_datos.pdf`](docs/reporte_base_datos.pdf)
- **Detalles, decisiones y trampas de los datos:** [AGENTS.md](AGENTS.md)

```bash
pip install -r requirements.txt
python scripts/limpiar.py <carpeta_con_csv_crudos>   # regenera la base limpia
python scripts/datos_dashboard.py                    # regenera los datos del dashboard
```

Datos: Astromaterials Data Synthesis / EarthChem PetDB, descargados el 13-oct-2026, CC BY 4.0.
