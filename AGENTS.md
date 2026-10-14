# AGENTS.md — Geoquímica de rocas: estadística y machine learning

Guía para cualquier agente (Claude Code, Codex, Gemini/Antigravity) que trabaje en este repo.
Leela entera antes de tocar datos o código.

## Qué es el proyecto

Proyecto semestral de la asignatura **Estadística y Probabilidades** (FIGEMPA, Universidad Central del
Ecuador; docente Dr. Christian Mejía E.; paralelo Geología–Minas) sobre composiciones químicas de roca total
(elementos mayores, trazas y tierras raras) de la base **EarthChem / PetDB**.

Equipo (Ingeniería en Minas): Cristoffer Joel Rumiguano Chariguaman, Ana Gabriela Fernández Chuquimarca,
Evelyn Maritza Bustamante Armijos, Jessica Jaqueline Haro Simba.

### El curso manda la estructura

Plan del curso: https://cimejia.github.io/proyectos-estadistica/Plan_20_Lecciones_Estadistica.html
Galería de proyectos modelo: https://cimejia.github.io/proyectos-estadistica/ (ver los de Minas, p. ej.
"Geoquímica de minerales críticos"). Cada lección suma una sección a la web, en este orden:

Introducción → Planteamiento del problema → Mapa de ubicación → Objetivos →
Estadística descriptiva (población, individuo, muestra, tabla de variables, TDF, gráficas, tabla de indicadores) →
Estadística inferencial (modelos binomial, geométrico, Poisson, normal, log-normal, exponencial; IC) →
Regresión (lineal, exponencial, polinómica, potencial, logarítmica, múltiple) → Machine Learning (red neuronal).

| Lección | Tema | Evidencia que va a la web |
|---|---|---|
| L2 | Población, individuo, muestra | definición textual y simbólica (hecha) |
| L3 | Muestreo probabilístico + QGIS | mapa de ubicación en QGIS + informe de muestreo (**pendiente**) |
| L4 | Variable y escalas de medición | tabla de variables: tipo, subtipo, instrumento, unidad, dominio (hecha) |
| L5 | TDF cualitativas, discretas, continuas | TDF + histograma, ojiva, barras (pendiente) |
| L6 | Indicadores | tabla de indicadores + boxplots (pendiente) |
| L7 | Exposición etapa I | sitio con descriptiva completa |

El docente demuestra en R/RStudio, QGIS y Python/Colab.

## Requisitos del curso y cómo se cumplen

| Requisito | Estado |
|---|---|
| ≥ 10 000 filas | 159 760 filas (cada fila = un análisis de una muestra) |
| ≥ 30 columnas | 74 columnas |
| Variables nominales | `Sample Type`, `Sample SubType`, `Tectonic Setting`, `Geographic Features`, `Rock Texture`, `Geologic Age`, `Expedition`, `Citation`; binaria: `Analyzed Material` |
| Variables ordinales | `SiO2 Class` (ultrabasica < basica < intermedia < acida), `Alteration Grade` (0 fresca … 5 totalmente alterada) |
| Numéricas discretas | `Publication Year`, `N Analytes` (cuántos analitos se midieron en la muestra) |
| Numéricas continuas | 52 químicas (wt% y ppm), `Latitude`, `Longitude`, elevaciones, edades en Ma |

## Estructura

```
data/raw/earthchem_export_oct13_26_142339.txt   parámetros de la consulta + términos de uso
data/earthchem_limpio.csv.gz                    base limpia (pandas la lee directo)
scripts/limpiar.py                              crudo -> base limpia
scripts/datos_dashboard.py                      base limpia -> docs/data/resumen.json
scripts/reporte_pdf.py                          base limpia -> docs/reporte_base_datos.pdf
scripts/tabla_variables.py                      crudo + limpia -> data/tabla_variables.xlsx y docs/data/variables.json
docs/reporte_base_datos.pdf                     reporte de la base para el equipo
docs/index.html                                 la web (HTML + Plotly por CDN, sin build)
docs/data/resumen.json                          agregados que consume el dashboard
```

```python
import pandas as pd
df = pd.read_csv("data/earthchem_limpio.csv.gz", low_memory=False)
```

## Datos crudos (no están en el repo)

Pesan ~600 MB (GitHub no acepta archivos > 100 MB). Están en la PC del usuario en
`C:\Users\dalem\Downloads\quimica\`:

- `earthchem_export_oct13_26_142339.csv` — 159 760 filas × 2 318 columnas. Cada elemento trae 4
  columnas: valor, `Method`, `Method (comment)`, `Lab`.
- `earthchem_export_oct13_26_142339_sample_metadata.csv` — misma cantidad de filas y **mismo orden**;
  trae ubicación, ambiente tectónico, textura, alteración, edad.

Para regenerar: `python scripts/limpiar.py "C:\Users\dalem\Downloads\quimica"` y luego
`python scripts/datos_dashboard.py`, `python scripts/tabla_variables.py "C:\Users\dalem\Downloads\quimica"`
y `python scripts/reporte_pdf.py`. Para re-descargar, la URL de la consulta está en `data/raw/*.txt`.

## Decisiones de limpieza (no deshacer sin motivo)

- Se descartan columnas químicas con dato en < 5 % de las filas. Ahí caen los **isótopos**
  (Sr87/Sr86 ~2 700 valores, Nd143/Nd144 ~2 400). Si el análisis los necesita, bajar `MIN_LLENADO`.
- Vacío = "no medido", **nunca cero**. Una celda química que no era un número limpio queda vacía.
- Algunas filas aparecen como varias líneas en `wc -l` porque hay celdas con saltos de línea: contar
  filas siempre con un parser CSV.
- `Alteration Grade`: PetDB usa el texto completo o su inicial (F, S, M, E, A, T). `N` y `N/A` son
  ambiguos y quedan vacíos.
- `SiO2 Class` usa SiO2 tal como viene, sin recalcular a base anhidra.
- Concentraciones negativas (lecturas bajo el límite de detección, ~50 celdas) quedan vacías. Excepción:
  `LOI` puede ser negativa de verdad (la roca gana peso al oxidarse el Fe) y se conserva.
- 5 muestras de la dorsal de Gakkel (Ártico) vienen en PetDB con latitud y longitud invertidas
  (99.85°N, 84.9°E); `lat_lon()` las intercambia cuando |lat| > 90.

## Trampas conocidas de los datos

- **Falta TiO2 (wt%)**: la exportación prácticamente no lo trae (4 valores). Es un mayor clave para
  basaltos; si hace falta, re-exportar desde EarthChem marcándolo.
- Mismo elemento en dos unidades: `Ni/Co/Cu/Zn (wt%)` y `(ppm)`. 1 wt% = 10 000 ppm. No mezclar sin convertir.
- El hierro viene de 4 formas: `FeO`, `Fe2O3`, `FeOT`, `Fe2O3T`. Para comparar, unificar a FeOT
  (FeOT = FeO + 0.8998·Fe2O3).
- Solo ~35 % de las filas tiene los mayores completos: filtrar filas completas por análisis, no imputar a ciegas.
- Datos de miles de papers desde 1932: hay sesgo por publicación y por método analítico.
- `Tectonic Setting` tiene 60 valores, algunos combinados ("FRACTURE ZONE,SPREADING CENTER"):
  agrupar antes de usarlo como clase en ML.

## Web (GitHub Pages)

- Se publica desde la rama `main`, carpeta `/docs`. Cualquier push a `docs/` actualiza la web en ~1 min.
- Repo público: GitHub Pages gratis no funciona en repos privados.
- Secciones de `docs/index.html` en el orden del curso (ver arriba). La tabla de variables se dibuja desde
  `docs/data/variables.json`: para cambiar descripciones, editar `OTRAS`/`NOMBRES` en `scripts/tabla_variables.py`.
- Población/individuo/muestra: la muestra es la compilación PetDB (n = 159 760), **no probabilística**; la
  web dice que la inferencia usará submuestras aleatorias estratificadas por ambiente tectónico (L3).
- Colores del dashboard: paleta validada (azul/naranja/aqua para ≤ 3 series, rampa azul para ordinales).
  No agregar más de 3 colores categóricos en un mismo gráfico; si hace falta más, agrupar en "Otros".

## Convenciones

- Código y comentarios en español; nombres de columnas originales de PetDB en inglés.
- Python 3.13, pandas, numpy, scikit-learn (`requirements.txt`).
- Leer los CSV con `python -I` si vienen de una descarga nueva.
- La licencia de los datos es CC BY 4.0: citar EarthChem/PetDB y la fecha de descarga en cualquier gráfico o informe.
