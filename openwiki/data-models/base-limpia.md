# Base de datos: origen, limpieza y variables

## Origen

Exportación de **EarthChem PetDB** (vía Astromaterials Data Synthesis) del 13 de octubre de 2026, con un único
filtro: material analizado = roca total (incluye "unspecified rock material as whole rock or glass"). Se
pidieron todas las familias de variables (mayores, trazas, tierras raras, edades, end-members, moda, gases
nobles, volátiles). La URL exacta y los términos de uso están en `data/raw/earthchem_export_oct13_26_142339.txt`.
Licencia **CC BY 4.0**: citar la fuente y la fecha en todo gráfico o informe.

PetDB no mide: transcribe datos de artículos revisados por pares. Por eso la base hereda sesgos de publicación
(dos tercios de las muestras son oceánicas, por los programas DSDP/ODP/IODP) y de método analítico.

## Los dos archivos crudos

- `earthchem_export_oct13_26_142339.csv`: 159 760 filas × 2 318 columnas. Cada analito trae cuatro columnas:
  valor, `Method`, `Method (comment)`, `Lab`. Los nombres de muestra vienen como fórmula de Excel (`="FS-42"`).
- `earthchem_export_oct13_26_142339_sample_metadata.csv`: mismas filas **en el mismo orden**, con ubicación,
  ambiente tectónico, textura, alteración, edad y expedición.

`wc -l` cuenta más líneas que filas porque hay celdas con saltos de línea: contar siempre con un parser CSV.

## Qué hace `scripts/limpiar.py`

Dos pasadas por el CSV crudo (no cabe cómodo en memoria con 2 318 columnas):

1. **Pasada 1** cuenta cuántos valores numéricos tiene cada columna química y verifica, fila por fila, que el
   nombre de la muestra coincida con el del archivo de metadatos (un `assert` corta si el orden se rompe).
2. **Pasada 2** escribe `data/earthchem_limpio.csv.gz` con las columnas elegidas.

Reglas, cada una en su función:

| Regla | Función | Por qué |
|---|---|---|
| Solo químicas con dato en ≥ 5 % de filas | `MIN_LLENADO` | deja 52; caen los isótopos (< 2 %) |
| Celda no numérica → vacía | `es_numero` | vacío = no medido, nunca cero |
| Concentración negativa → vacía, salvo LOI | `valor_quimico` | negativos = bajo el límite de detección; LOI puede ser negativa de verdad |
| Coordenadas `39.244°N` → decimales con signo | `coordenada` | S y O negativos |
| Latitud > 90 → intercambiar con longitud | `lat_lon` | 5 muestras de la dorsal de Gakkel vienen invertidas en PetDB |
| Año desde la cita `(2011)` | `anio` | variable discreta |
| Clase por SiO2 | `clase_sio2` | ordinal: ultrabásica < 45 ≤ básica < 52 ≤ intermedia < 63 ≤ ácida |
| Grado de alteración 0–5 | `ALTERACION` | ordinal; acepta texto o inicial (F, S, M, E, A, T); `N` y `N/A` quedan vacíos |
| Grupo tectónico | `grupo_tectonico` | 59 ambientes → dorsal y corteza oceánica / margen convergente / intraplaca y rift / mixto |
| Número de analitos medidos (analito = cada óxido o elemento medido) | `N Analytes` | discreta, 0–75 |

El bloque `if __name__ == "__main__"` tiene `assert`s de autoverificación de estas funciones: correr el script
sin argumentos los ejecuta y muestra el uso.

## La base limpia

`data/earthchem_limpio.csv.gz`: 159 760 filas × 75 columnas, UTF-8, punto decimal. La clasificación completa de
las 75 variables (tipo, subtipo, escala, instrumento, unidad, dominio, % con dato) está en
`data/tabla_variables.xlsx` y se genera con `scripts/tabla_variables.py`, que toma el **método analítico más
frecuente** de cada variable desde las columnas `Method` del crudo.

| Tipo | Cuántas | Ejemplos |
|---|---|---|
| Nominal | 11 (una binaria; 2 identificadoras) | `Sample Type`, `Tectonic Setting`, `Tectonic Group`, `Analyzed Material`, `Sample Name`, `Sample URL` |
| Ordinal | 4 | `SiO2 Class`, `Alteration Grade`, `Geologic Age`, `Sample Alteration` |
| Discreta | 2 | `Publication Year`, `N Analytes` |
| Continua | 58 | 52 químicas (wt% y ppm), coordenadas, elevaciones, edades en Ma |

Desde el 07/11/2026 la tabla tiene la columna «Nombre en español» (`ESPANOL` en el script) y los
identificadores (`Sample Name`, `Sample URL`) figuran como cualitativas nominales, a pedido del docente.

La tabla sigue el formato de la plantilla del curso (`referencias_curso/Litogeoquímica del Perú/BD_LITOGEOQUIMICA.xlsx`,
hoja `Hoja1`): nombre, descripción, tipo, subtipo, **dominio** en dos versiones (definición, p. ej.
`D={x/x es concentración ^ x ∈ R}`, y conjunto, p. ej. `D={x/x ∈ R+ ∪ {0}}`), **rango** observado
(`R={y/ min ≤ y ≤ max}` o `R={y/y ∈ categorías}`), instrumento, unidad y escala. Dominio = valores posibles en teoría;
rango = valores que aparecen en la muestra.

Las descripciones viven en `OTRAS` y `NOMBRES`, y los dominios en `DOMINIOS` y `ENUMERADOS`, dentro de
`scripts/tabla_variables.py`: si una variable nueva entra a la base, agregarla ahí o el script falla con `KeyError`.

## Población, individuo y muestra (marco del curso)

La muestra probabilística para inferir (L3) es `data/muestras/muestra_estratificada.csv` (n = 1 061, estratos =
`Tectonic Group`, afijación proporcional, seed 2026; `R/04_muestreo.R`).


- Población U: todas las porciones de roca total de la corteza y el manto superior (infinita).
- Individuo Xᵢ: cada porción de roca analizada.
- Muestra M ⊂ U: los 159 760 análisis de PetDB. **No es probabilística**; la inferencia (Unidad 2) debe
  usar submuestras aleatorias estratificadas por `Tectonic Group`.

## Al cambiar la limpieza

- Correr de nuevo toda la cadena (ver [Regenerar y publicar](../workflows/regenerar-y-publicar.md)): la tabla
  de variables, el dashboard, el PDF y el mapa leen la base limpia.
- Los textos fijos de la web y del README mencionan "75 columnas" y "159.760": actualizarlos si cambian.
