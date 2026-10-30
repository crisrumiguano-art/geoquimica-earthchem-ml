# AGENTS.md — Geoquímica de rocas: estadística y machine learning

Guía para cualquier agente (Claude Code, Codex, Gemini/Antigravity) que trabaje en este repo.
Leela entera antes de tocar datos o código.

## Qué es el proyecto

Proyecto semestral de la asignatura **Estadística y Probabilidades** (FIGEMPA, Universidad Central del
Ecuador; docente Dr. Christian Mejía E.; paralelo Geología–Minas) sobre composiciones químicas de roca total
(elementos mayores, trazas y tierras raras) de la base **EarthChem / PetDB**.

Equipo (Ingeniería en Minas): Cristoffer Joel Rumiguano Chariguaman, Ana Gabriela Fernández Chuquimarca,
Evelyn Maritza Bustamante Armijos, Jessica Jaqueline Haro Simba, Jhonattan Sebastián Ligña Hernández.

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
| L3 | Muestreo probabilístico + QGIS | mapa de ubicación en QGIS y Python (hecho); muestreo aleatorio, sistemático y estratificado en `R/04_muestreo.R` + `docs/informe_muestreo.pdf` (hecho; n = 1 061, estratos = `Tectonic Group`; la estratificada es la que va a la Unidad 2) |
| L4 | Variable y escalas de medición | tabla de variables con el formato del curso: dominio (definición y conjunto) y rango (hecha) |
| L5 | TDF cualitativas, discretas, continuas | TDF + histograma, ojiva, barras en R (hecho, `/descriptiva/`) |
| L6 | Indicadores | indicadores, boxplots y error de agrupación en R (hecho para SiO2, MgO, Cr; ampliar a más variables) |
| L7 | Exposición etapa I | sitio con descriptiva completa |

El docente demuestra en R/RStudio, QGIS y Python/Colab. **La estadística se entrega en R** (exigencia del docente):
la carpeta `R/` sigue la estructura de sus plantillas (TDF con Li, Ls, MC, ni, hi, Ni/Hi ascendentes y descendentes;
histograma con `barplot(space = 0)`, polígono, ojiva, boxplot; `e1071` para asimetría y curtosis). Python queda
para limpieza, mapa y web.

## Enlaces del proyecto

- Web: https://crisrumiguano-art.github.io/geoquimica-earthchem-ml/
- Repo: https://github.com/crisrumiguano-art/geoquimica-earthchem-ml
- Base en Google Sheets que el equipo subió para revisarla en Excel: https://docs.google.com/spreadsheets/d/1i8tvb2M3Sn-HuON0TFsDOkX02NfImvWHGwTLIBfBLwc/edit?usp=sharing
  (copia de trabajo del equipo; la fuente de verdad es `data/earthchem_limpio.csv.gz`).
- Formatos del docente: plan del curso https://cimejia.github.io/proyectos-estadistica/Plan_20_Lecciones_Estadistica.html · galería de proyectos modelo https://cimejia.github.io/proyectos-estadistica/

## Requisitos del curso y cómo se cumplen

| Requisito | Estado |
|---|---|
| ≥ 10 000 filas | 159 760 filas (cada fila = un análisis de una muestra) |
| ≥ 30 columnas | 75 columnas |
| Variables nominales | `Sample Type`, `Sample SubType`, `Tectonic Setting`, `Geographic Features`, `Rock Texture`, `Expedition`, `Citation`, `Tectonic Group` (3 grupos + mixto); binaria: `Analyzed Material` |
| Variables ordinales | `SiO2 Class` (ultrabasica < basica < intermedia < acida), `Alteration Grade` (0 fresca … 5 totalmente alterada), `Geologic Age` (período), `Sample Alteration` (texto original) |
| Numéricas discretas | `Publication Year`, `N Analytes` (cuántos analitos se midieron en la muestra) |
| Numéricas continuas | 52 químicas (wt% y ppm), `Latitude`, `Longitude`, elevaciones, edades en Ma |

## Estructura

```
data/raw/earthchem_export_oct13_26_142339.txt   parámetros de la consulta + términos de uso
data/earthchem_limpio.csv.gz                    base limpia (pandas la lee directo)
scripts/limpiar.py                              crudo -> base limpia
scripts/datos_dashboard.py                      base limpia -> docs/data/resumen.json
scripts/informe.py                              informe del proyecto -> docs/informe_proyecto.docx + .pdf (vía Word)
scripts/informe_muestreo.py                     informe de muestreo (L3) -> docs/informe_muestreo.docx + .pdf (después de R/04)
scripts/codigo_r.py                             R/*.R -> docs/data/codigo_r.json (botón «Código R» de cada gráfica; correr tras R)
scripts/tabla_variables.py                      crudo + limpia -> data/tabla_variables.xlsx y docs/data/variables.json
scripts/mapa.py                                 limpia -> data/gis/mapa_ubicacion.gpkg + docs/img/mapa_ubicacion.png
scripts/proyecto_qgis.py                        gpkg -> data/gis/shp/*.shp + mapa_ubicacion.qgz (composiciones A4 y A3) +
                                                docs/img/mapa_qgis.png, docs/mapa_ubicacion_A4.pdf / _A3.pdf y
                                                docs/mapa_qgis_shapefiles.zip (qgz + shp + logo, para el equipo)
data/gis/                                       capas GIS (WGS84) y proyecto QGIS con composición A4
docs/informe_proyecto.docx / .pdf               informe: base de datos, estadística y documentación técnica
R/funciones.R + 01/02/03_*.R                    estadística descriptiva (TDF, gráficas, outliers, indicadores)
R/04_muestreo.R                                 muestreo (L3) -> data/muestras/*.csv, R/salidas/Muestreo.xlsx
docs/mapa_ubicacion_A4.pdf / _A3.pdf            mapa QGIS en PDF vectorial para imprimir a escala (100 %, sin ajustar):
                                                A4 1:150 000 000, A3 1:110 000 000 (fijadas en PAPELES de proyecto_qgis.py;
                                                el ancho del marco se calcula; 1:100 M no entra en A3)
R/analisis_agrupacion_outliers.md               por qué y cómo se agrupó y se trataron los outliers
R/salidas/                                      Excel con todas las TDF
docs/index.html, descriptiva/, datos/, equipo/  la web: una página por unidad (HTML + CSS + Plotly, sin build)
docs/assets/                                    estilo.css y app.js compartidos por todas las páginas
docs/data/                                      resumen.json, variables.json y tdf/*.csv (tablas que exporta R)
docs/img/r/                                     gráficas PNG que genera R
docs/img/                                       fotos del equipo, mapas e imágenes generadas con Google Flow
openwiki/                                       documentación explicativa (ver sección OpenWiki)
.claude/skills/                                 skills de agentes: diseño web, openwiki, graphify, gflow-cli
```

```python
import pandas as pd
df = pd.read_csv("data/earthchem_limpio.csv.gz", low_memory=False)
```

## Datos crudos (no están en el repo)

Pesan ~600 MB (GitHub no acepta archivos > 100 MB). Respaldados en Google Drive del usuario:
`G:\Mi unidad\2.- Archivos\Geología\Estadística y probabilidades\TRABAJOS ESTADISTICA\10-26 GDRIVE GEOQUIMICA ROCAS\datos_crudos_earthchem\`. En la PC del usuario, `data/raw/crudos` es una **junction** a esa carpeta
(ignorada por git) y `limpiar.py` / `tabla_variables.py` la usan por defecto (sin argumentos). Las junctions se crean con
PowerShell (`New-Item -ItemType Junction`) desde un .ps1 guardado en UTF-8 **con BOM** (si no, rompe los acentos de la
ruta); los symlinks piden permisos de administrador. Los archivos son:

- `earthchem_export_oct13_26_142339.csv` — 159 760 filas × 2 318 columnas. Cada elemento trae 4
  columnas: valor, `Method`, `Method (comment)`, `Lab`.
- `earthchem_export_oct13_26_142339_sample_metadata.csv` — misma cantidad de filas y **mismo orden**;
  trae ubicación, ambiente tectónico, textura, alteración, edad.

Para regenerar todo, en este orden: `limpiar.py` → `datos_dashboard.py` → `tabla_variables.py` →
`mapa.py` → `proyecto_qgis.py` (con el Python de QGIS) → scripts de `R/` → `informe.py`. Comandos exactos en
[openwiki/workflows/regenerar-y-publicar.md](openwiki/workflows/regenerar-y-publicar.md). Para re-descargar,
la URL de la consulta está en `data/raw/*.txt`.

Material de referencia del curso (plantillas de R de otros años, `BD_LITOGEOQUIMICA.xlsx` con el **formato de la tabla
de variables** en la hoja `Hoja1`, material de QGIS): respaldado en `…\10-26 GDRIVE GEOQUIMICA ROCAS\plantillas_curso_proyecto2\`
y enlazado en el repo como `referencias_curso/` (junction, ignorada por git).

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
- `Tectonic Setting` tiene 59 valores, algunos combinados ("FRACTURE ZONE,SPREADING CENTER"). Para ML y
  mapas usar `Tectonic Group` (`GRUPO_TECTONICO` en `limpiar.py`): combinaciones con grupos distintos = "mixto".

## Web (GitHub Pages)

- Se publica desde la rama `main`, carpeta `/docs`. Cualquier push a `docs/` actualiza la web en ~1 min.
- Repo público: GitHub Pages gratis no funciona en repos privados.
- Una página por unidad: `/` (problema, mapa, objetivos), `/descriptiva/` (U1), `/datos/`, `/equipo/`.
  Inferencial, regresión y ML figuran como "pronto" en el menú: al crearlas, copiar el `<nav>` y cambiar el
  `<span class="pronto">` por un enlace en **todas** las páginas (el menú está repetido en cada HTML).
- La tabla de variables se dibuja desde `docs/data/variables.json`: para cambiar descripciones, editar
  `OTRAS`/`NOMBRES` en `scripts/tabla_variables.py`.
- Agrupación y outliers: **no eliminar outliers**; son otras rocas, no errores. TDF = intervalos de Sturges sobre el
  rango IQR con amplitud redonda + clases abiertas; trazas en log10; repetir por estrato. Ver `R/analisis_agrupacion_outliers.md`.
- Repo y web pertenecen a **crisrumiguano-art** (Cristoffer) desde el 15/10/2026. Desde el 18/10/2026 los cambios se
  hacen con la cuenta **rosemeri1492-lgtm** (Write); DalemberV ya no es colaborador y su autoría se reescribió en el
  historial. En la PC del usuario, este repo hace push con el token de `.env` (`GH_ROSEMERI_TOKEN`, ignorado por git)
  mediante un `credential.helper` local, y firma los commits como rosemeri (`git config` local).
  URLs: https://crisrumiguano-art.github.io/geoquimica-earthchem-ml/ · https://github.com/crisrumiguano-art/geoquimica-earthchem-ml
  Cristoffer usa Jules (agente de Google) y solo GitHub en el celular: revisar sus PR antes de asumir que algo cambió
  (el PR #1 cambió el título al revés de lo pedido; se corrigió a "La geoquímica de la Tierra").
- Regresiones (Unidad 3): alcanzan los datos (p. ej. La–Ce 31 690 pares, MgO–Ni 9 379, 6 óxidos completos 46 308),
  pero usar log10 en trazas (Zr–Hf r = 0,15 lineal vs 0,97 en log), filas completas por par (sin imputar) y
  estratificar por roca o `Tectonic Group`. Tabla en la sección 10 del informe.
- Correcciones del docente (21/10/2026): sin sección de introducción; el planteamiento no lleva pregunta sino
  **importancia, uso de la estadística y caso de estudio**; objetivo general corto; **3 objetivos específicos** que
  cubren todo el proyecto, cada uno con imagen; aviso de proyecto **estrictamente académico** en el pie de todas las
  páginas; mapa QGIS con **cuadrícula con coordenadas y membrete** (formato de `referencias_curso/QGIS/1.- Mapa de
  Ubicacion/Plantilla1.qpt`, logo `data/gis/UCE.png`).
- Mapa QGIS en **EPSG:4087** (equidistante cilíndrica WGS84, metros): 1° = 111,32 km en todo el mapa, así la escala,
  la barra en km y la cuadrícula coinciden (el docente objetó que en EPSG:4326 no cuadraban, 29/10/2026). Cuadrícula
  y rótulos **en metros** cada 2 500 000 m (`PASO`), como la plantilla UTM: mezclar rótulos en grados con un mapa en
  metros también fue objetado. Barra con punto de miles (`QgsBasicNumericFormat`).
- Cada gráfica de R en la web tiene un botón **Código R** (pedido del docente): muestra el script y las funciones exactas
  que la generaron, desde `docs/data/codigo_r.json` (`scripts/codigo_r.py`), con resaltado de sintaxis propio
  (`resaltarR` en `app.js`, colores tipo VS Code en `.codigo-r .r-*`). Los comentarios didácticos viven en los `.R`. Si se agrega un PNG en `docs/img/r/`
  con un prefijo nuevo, sumarlo a `SCRIPTS` en ese archivo.
- El proyecto QGIS usa **shapefiles** (`data/gis/shp/`, 9 campos en muestras, anchos fijos con CAST en OGR SQL e índice
  `.qix`), no el GeoPackage: el equipo trabaja QGIS "de forma tradicional" y el gpkg de 35 MB le colgaba QGIS. El
  planteamiento del problema es **una sola redacción continua**, sin subtítulos ni columnas (cubre importancia, uso de
  la estadística y caso de estudio), pedido del docente (23/10/2026).
- Población/individuo/muestra: la muestra es la compilación PetDB (n = 159 760), **no probabilística**; la
  web dice que la inferencia usará submuestras aleatorias estratificadas por ambiente tectónico (L3).
- Diseño "basalto": tema oscuro editorial, acento magma `#ff6b2c`, Fraunces (títulos) + Instrument Sans
  (texto) + JetBrains Mono (cifras). Tokens en `:root` de `docs/assets/estilo.css`; no meter colores sueltos.
- Colores de datos: paleta validada (azul/naranja/aqua para ≤ 3 series, rampa azul para ordinales). Los mismos
  en la web, `mapa.py` y `proyecto_qgis.py`. No más de 3 colores categóricos por gráfico; el resto, "mixto"/"Otros".
- Imágenes ilustrativas (`hero`, `andes`, `barco`, `nucleos`) generadas con `gflow image t2i` (skill
  `gflow-cli`); la web lo aclara en los pies. Las fotos del equipo son reales: no regenerarlas con IA.

## Convenciones

- Código y comentarios en español; nombres de columnas originales de PetDB en inglés.
- Python 3.13, pandas, numpy, scikit-learn (`requirements.txt`).
- Leer los CSV con `python -I` si vienen de una descarga nueva. Los scripts que importan a sus vecinos
  (`tabla_variables.py`, `informe.py`) se corren sin `-I`.
- El informe se edita en `scripts/informe.py` (python-docx), no en el .docx: el .docx y el .pdf se regeneran. La
  parte técnica (sección 12, librerías y versiones) hay que actualizarla a mano si cambia el stack.
- La licencia de los datos es CC BY 4.0: citar EarthChem/PetDB y la fecha de descarga en cualquier gráfico o informe.

## OpenWiki

This repository has documentation located in the /openwiki directory.

Start here:
- [OpenWiki quickstart](openwiki/quickstart.md)

OpenWiki includes repository overview, architecture notes, workflows, domain concepts, operations, integrations, testing guidance, and source maps.

When working in this repository, read the OpenWiki quickstart first, then follow its links to the relevant architecture, workflow, domain, operation, and testing notes.
