# Quickstart — Geoquímica de rocas con estadística y machine learning

Proyecto semestral de **Estadística y Probabilidades** (FIGEMPA, Universidad Central del Ecuador; docente
Dr. Christian Mejía E.) de un equipo de Ingeniería en Minas. Toma 159 760 análisis químicos de roca total de
la base **EarthChem PetDB** y los usa como caso de estudio para las cuatro unidades del curso: estadística
descriptiva, inferencial, regresión y machine learning (ver `AGENTS.md`, sección "El curso manda la estructura").

El producto final es una **web en GitHub Pages** (`docs/`) que crece una sección por lección, más la base
limpia y los scripts que la generan.

- Web: https://crisrumiguano-art.github.io/geoquimica-earthchem-ml/
- Repo: https://github.com/crisrumiguano-art/geoquimica-earthchem-ml

## Cómo está organizado

| Carpeta | Qué hay | Detalle |
|---|---|---|
| `data/` | base limpia (`earthchem_limpio.csv.gz`), tabla de variables (`.xlsx`), capas GIS y proyecto QGIS | [Base de datos](data-models/base-limpia.md) |
| `scripts/` | un script por producto, todos en Python | [Regenerar y publicar](workflows/regenerar-y-publicar.md) |
| `R/` | estadística descriptiva en R (exigencia del docente) | [Estadística en R](workflows/regenerar-y-publicar.md#estadística-en-r) |
| `docs/` | la web estática (una página por unidad), el reporte PDF, datos agregados e imágenes | [La web](architecture/web.md) |
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
| L5–L6 | TDF, gráficas, indicadores, outliers (R) | hecho para cualitativas, discretas y SiO2/MgO/Cr |
| L7 | conclusiones descriptivas, exposición | pendiente |
| U2–U4 | inferencia, regresión, red neuronal | pendiente |

Antes de tocar histogramas o outliers, leer `R/analisis_agrupacion_outliers.md`: la agrupación por defecto y la
eliminación de outliers de las plantillas del curso **no** sirven en esta base, y ahí está el porqué.

## Páginas

- [Base de datos: origen, limpieza y variables](data-models/base-limpia.md)
- [Regenerar productos y publicar la web](workflows/regenerar-y-publicar.md)
- [La web: estructura, diseño y cómo agregar una sección](architecture/web.md)
