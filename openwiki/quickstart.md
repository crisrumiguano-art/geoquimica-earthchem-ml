# Quickstart — Geoquímica de rocas con estadística y machine learning

Proyecto semestral de **Estadística y Probabilidades** (FIGEMPA-UCE; docente Dr. Christian Mejía E.) de un equipo de
Ingeniería en Minas: 159 760 análisis químicos de roca total de **EarthChem PetDB** como caso de estudio para las
cuatro unidades del curso (descriptiva, inferencial, regresión, machine learning). Producto: una **web en GitHub
Pages** (`docs/`) que crece una sección por lección, más la base limpia y los scripts. Reglas y decisiones: `AGENTS.md`.

- Web: https://crisrumiguano-art.github.io/geoquimica-earthchem-ml/ · Repo: https://github.com/crisrumiguano-art/geoquimica-earthchem-ml
- Plan del curso: https://cimejia.github.io/proyectos-estadistica/Plan_20_Lecciones_Estadistica.html
- Proyecto modelo que mostró el docente: https://geoquimicaglobal.framer.website/ (tabla de variables y código R en RPubs)
- Copia del equipo en Google Sheets: https://docs.google.com/spreadsheets/d/1i8tvb2M3Sn-HuON0TFsDOkX02NfImvWHGwTLIBfBLwc/edit?usp=sharing

| Carpeta | Qué hay | Detalle |
|---|---|---|
| `data/` | base limpia, tabla de variables, muestras (L3), capas GIS (shapefiles) y proyecto QGIS | [Base de datos](data-models/base-limpia.md) |
| `scripts/` | Python: limpieza, web, mapa, informes, código R para la web | [Regenerar y publicar](workflows/regenerar-y-publicar.md) |
| `R/` | la estadística (exigencia del docente); `R/graficos/` = un script simple por gráfico | [Estadística en R](workflows/regenerar-y-publicar.md#estadística-en-r) |
| `docs/` | la web, PDF (informes y mapas A4/A3), datos agregados e imágenes | [La web](architecture/web.md) |

Crudos (~600 MB) fuera del repo: Google Drive del usuario, enlazado como `data/raw/crudos` (junction).

```python
import pandas as pd
df = pd.read_csv("data/earthchem_limpio.csv.gz", low_memory=False)   # 159 760 × 75
```

## Estado (noviembre de 2026)

| Lección | Entregable | Estado |
|---|---|---|
| L1–L2 | problema (una redacción), objetivos (general + 3), población/individuo/muestra | hecho |
| L3 | mapa QGIS (EPSG:4087, A4 1:150 M y A3 1:110 M) + muestreo aleatorio, sistemático y estratificado | hecho (`informe_muestreo.pdf`) |
| L4 | tabla de variables con el formato del docente (nombre corto, un dominio, rango, variable de interés e individuo) | hecho (corregida 11/2026) |
| L5–L6 | TDF, gráficas, indicadores, outliers, error de agrupación, con código R por gráfico y un R Markdown por variable (RPubs) | hecho (SiO2, MgO, Cr; ampliar) |
| L7 | exposición etapa I | pendiente |
| L8–L12 | inferencial: 7 modelos (binomial, geométrico, Poisson, normal, log-normal, exponencial, beta) con chi-cuadrado e IC (muestra aleatoria de L3) | hecho (`/inferencial/`) |
| L13–L17 | regresión: 5 simples, múltiple, logística, serie de tiempo, PCA y k-means | hecho (`/regresion/`) |
| L18–L20 | red neuronal de regresión (Ni) y de clasificación (ambiente tectónico), Colab | `/ml/` |

Antes de tocar histogramas u outliers: `R/analisis_agrupacion_outliers.md` (no se borran outliers; TDF con clases abiertas).

## Glosario mínimo

- **Analito**: cada sustancia que se mide en un análisis químico (un óxido como SiO2 o un elemento como Cr).
  `N Analytes` = cuántos analitos se midieron en esa muestra (variable discreta, 0 a 75).
- **wt%** = porcentaje en peso (elementos mayores); **ppm** = partes por millón (trazas; 1 wt% = 10 000 ppm).
- **TDF** = tabla de distribución de frecuencias; **clase abierta** = intervalo «< Li» o «≥ Ls» donde se cuentan
  los outliers sin borrarlos.

## Páginas

- [Base de datos: origen, limpieza y variables](data-models/base-limpia.md)
- [Regenerar productos y publicar la web](workflows/regenerar-y-publicar.md)
- [La web: estructura, diseño y cómo agregar una sección](architecture/web.md)
