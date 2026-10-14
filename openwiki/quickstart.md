# Quickstart — Geoquímica de rocas con estadística y machine learning

Proyecto semestral de **Estadística y Probabilidades** (FIGEMPA, Universidad Central del Ecuador; docente
Dr. Christian Mejía E.) de un equipo de Ingeniería en Minas. Toma 159 760 análisis químicos de roca total de
la base **EarthChem PetDB** y los usa como caso de estudio para las cuatro unidades del curso: estadística
descriptiva, inferencial, regresión y machine learning (ver `AGENTS.md`, sección "El curso manda la estructura").

El producto final es una **web en GitHub Pages** (`docs/`) que crece una sección por lección, más la base
limpia y los scripts que la generan.

- Web: https://dalemberv.github.io/geoquimica-earthchem-ml/
- Repo: https://github.com/DalemberV/geoquimica-earthchem-ml

## Cómo está organizado

| Carpeta | Qué hay | Detalle |
|---|---|---|
| `data/` | base limpia (`earthchem_limpio.csv.gz`), tabla de variables (`.xlsx`), capas GIS y proyecto QGIS | [Base de datos](data-models/base-limpia.md) |
| `scripts/` | un script por producto, todos en Python | [Regenerar y publicar](workflows/regenerar-y-publicar.md) |
| `docs/` | la web estática, el reporte PDF, datos agregados e imágenes | [La web](architecture/web.md) |
| `.claude/skills/` | skills de agentes (diseño web, openwiki, graphify, gflow-cli) | — |

Los datos crudos (~600 MB) **no están en el repo**: viven en `C:\Users\dalem\Downloads\quimica\` en la PC del
usuario, y la consulta para volver a descargarlos está en `data/raw/earthchem_export_oct13_26_142339.txt`.

## Empezar en 1 minuto

```python
import pandas as pd
df = pd.read_csv("data/earthchem_limpio.csv.gz", low_memory=False)   # 159 760 × 75
```

Antes de analizar, leer las trampas de los datos en `AGENTS.md` (falta TiO2, unidades mezcladas, hierro en
4 formas, ~65 % de filas sin los elementos mayores completos).

## Estado del proyecto (octubre de 2026)

| Lección | Entregable | Estado |
|---|---|---|
| L1–L2 | introducción, problema, objetivos, población/individuo/muestra | hecho (web) |
| L3 | mapa de ubicación QGIS + Python | hecho; falta el informe de muestreo estratificado |
| L4 | tabla de variables (tipo, subtipo, escala, instrumento, unidad, dominio) | hecho (web + Excel) |
| L5–L7 | TDF, gráficas, tabla de indicadores, conclusiones descriptivas | pendiente |
| U2–U4 | inferencia, regresión, red neuronal | pendiente |

La sección "Exploración preliminar" de la web es un adelanto, no la descriptiva formal de L5–L6.

## Páginas

- [Base de datos: origen, limpieza y variables](data-models/base-limpia.md)
- [Regenerar productos y publicar la web](workflows/regenerar-y-publicar.md)
- [La web: estructura, diseño y cómo agregar una sección](architecture/web.md)
