# Agrupación en intervalos y tratamiento de outliers

Este documento explica cómo se construyeron las tablas de distribución de frecuencias (TDF) y los histogramas
de las variables continuas, y qué se hizo con los valores atípicos. Los números salen de `R/03_continuas.R`;
las tablas completas están en `R/salidas/TDF_continuas.xlsx` y las gráficas en `R/salidas/`.

## 1. El problema: la agrupación "por defecto" no sirve en esta base

Las plantillas del curso calculan el número de intervalos con la regla de Sturges, k = 1 + 3,3 log n, y la
amplitud como a = R / k, donde R es el recorrido (máximo menos mínimo). Ese procedimiento funciona bien con
muestras chicas y homogéneas, como las de las prácticas. En esta base falla por dos razones.

**El recorrido está dominado por unos pocos valores extremos.** El cromo va de 0,002 a 295 000 ppm. Con
k = 16, cada intervalo mide 18 437 ppm y el primero se queda con el 99,9 % de los datos: el histograma es
una sola barra (`Cr_agrupacion.png`, panel izquierdo). Con la sílice el efecto es menor, pero el intervalo
más poblado concentra igual el 47,7 % de los análisis y se pierde la forma de la distribución.

**Las otras reglas del curso dan demasiados intervalos.** Con n = 57 031 análisis de SiO2, la raíz de n da
239 intervalos y 2·raíz de n da 478, demasiados para una tabla que alguien tenga que leer. Sturges (k = 17)
es la única razonable con muestras tan grandes, así que se mantiene, pero aplicada sobre el recorrido típico
y no sobre el recorrido completo.

## 2. ¿Los outliers son errores?

Con la regla intercuartílica (outlier si x < Q1 − 1,5·IR o x > Q3 + 1,5·IR) aparecen muchos outliers:

| Variable | n | Outliers | % | Qué rocas son |
|---|---|---|---|---|
| SiO2 (wt%) | 57 031 | 8 413 | 14,8 | sobre todo tefras (5 191) y rocas félsicas (1 397) |
| MgO (wt%) | 57 039 | 9 607 | 16,8 | sobre todo ultramáficas, como peridotitas (6 658) |
| Cr (ppm), en log10 | 37 911 | 2 973 | 7,8 | máficas e intermedias con poco Cr; cromititas en el extremo alto |

La plantilla de Al2O3 quita los outliers "porque son aislados y son pocos". Acá no se cumple ninguna de las
dos condiciones: son el 8–17 % de los datos y no son errores de medición, sino **otras rocas**. La base mezcla
basaltos (≈ 50 % de SiO2), peridotitas (≈ 40 % de MgO) y riolitas (> 65 % de SiO2). La regla intercuartílica
supone una sola población; cuando hay varias mezcladas, marca como "atípica" a la población minoritaria.
Quitarlos borraría, por ejemplo, a todas las rocas ácidas de la muestra, y en minería los extremos suelen ser
justamente lo interesante: los Cr de 29,5 % son cromititas, una mena.

Los errores verdaderos ya se quitaron en la limpieza (concentraciones negativas, coordenadas imposibles; ver
`openwiki/data-models/base-limpia.md`).

**Decisión: no se elimina ningún dato.** Los outliers se identifican, se informan y se cuentan en clases
abiertas.

## 3. La solución: rango típico + clases abiertas

La TDF corregida (función `tdf_continua(x, lim = ...)` en `R/funciones.R`) se arma así:

1. k por Sturges con el n total.
2. Amplitud calculada sobre el rango típico, entre los límites intercuartílicos, y redondeada a un valor
   legible (1, 2, 2,5 o 5 por una potencia de 10). Así los intervalos quedan como [48-50[ y no como
   [47,183-53,001[.
3. Los valores por debajo del primer límite van a una clase abierta "< Li"; los de arriba, a "≥ Ls".
4. El histograma y el polígono se dibujan con las clases cerradas; las abiertas se anotan debajo del gráfico.
   La ojiva y el diagrama de caja usan todos los datos.

Resultado para la sílice: 15 intervalos de 2 wt% entre 36 y 66, más "< 36" (1,56 %) y "≥ 66" (12,66 %). La
clase abierta superior es grande porque ahí están las rocas ácidas: es información, no ruido.

**La agrupación se comprueba con el error de agrupación** (Lección 6): la media y la desviación estándar
calculadas con las marcas de clase se comparan con las de los datos sin agrupar.

| Variable | Error en la media | Error en la desviación |
|---|---|---|
| SiO2, toda la muestra | 0,03 % | 0,31 % |
| MgO, toda la muestra | 1,90 % | 3,05 % |
| log10 Cr, toda la muestra | 0,02 % | 0,28 % |
| SiO2, rocas volcánicas máficas | 0,03 % | 0,53 % |

Todos los errores son menores al 5 %: los intervalos representan bien a los datos. Como referencia, una
prueba intermedia con intervalos de 10 wt% dio un error del 39 % en la desviación.

## 4. Elementos traza: escala logarítmica

Las concentraciones de elementos traza (Cr, Ni, La, Sr…) no se distribuyen como una campana, sino con una
cola larga hacia la derecha. La asimetría del cromo es 39,4 en la escala original y −0,84 en log10. Por eso
su TDF se arma sobre log10(Cr): intervalos de 0,2 unidades logarítmicas, que equivalen a multiplicar por 1,58
de una clase a la siguiente. En esa escala aparecen **dos poblaciones**: un pico en el intervalo
[2,4-2,6[ (unos 300 ppm, basaltos) y otro en [3,4-3,6[ (unos 3 000 ppm, rocas ultramáficas). Esto anticipa la Unidad 2: estas
variables se ajustarán mejor a un modelo log-normal que a uno normal.

## 5. Estratificar: analizar cada tipo de roca por separado

Como la mezcla de rocas es la causa de los outliers, el análisis también se repite dentro de un grupo
homogéneo: las **rocas volcánicas máficas** (basaltos y afines), el más numeroso. Ahí la distribución es
mucho más compacta.

| SiO2 (wt%) | Toda la muestra | Volcánicas máficas |
|---|---|---|
| Mediana | 50,00 | 49,60 |
| Rango intercuartílico | 7,27 | 2,47 |
| Coeficiente de variación | 19,6 % | 8,7 % |

Aun así, dentro de los basaltos queda un 8,5 % de outliers, porque esa categoría de PetDB también incluye
rocas transicionales y muestras alteradas. Por eso se usan clases abiertas también en el estrato.

Para la Unidad 2 esto tiene una consecuencia práctica: la inferencia debe hacerse por estratos (por tipo de
roca o por `Tectonic Group`), y no sobre la muestra mezclada.

## 6. Variables discretas y cualitativas

- **Año de publicación** (`R/02_discretas.R`): 75 valores distintos, agrupados en décadas por Sturges con
  amplitud redonda (1930–2030). Prácticamente sin outliers (40 de 159 760). Mediana 2004, moda 2015.
- **Número de analitos**: asimétrica a la derecha (asimetría 1,58), con un 6,4 % de outliers por encima de
  34,5. Aquí sí se dejan en la TDF porque no deforman los intervalos (amplitud 5).
- **Cualitativas** (`R/01_cualitativas.R`): las nominales llevan solo ni y hi; las ordinales (clase de SiO2,
  grado de alteración) llevan además las acumuladas, y su mediana es la categoría donde Hi alcanza el 50 %
  (clase de SiO2: básica; alteración: leve). En el tipo de roca, las categorías con menos del 1 % se agrupan
  en "otros".

## Cómo correrlo

Desde la raíz del repositorio, con R 4.6 y los paquetes `e1071` y `openxlsx`:

```
Rscript R/01_cualitativas.R
Rscript R/02_discretas.R
Rscript R/03_continuas.R
```

Para analizar otra variable continua, agregarla a la lista `VARIABLES` de `R/03_continuas.R` con
`log = TRUE` si es un elemento traza.
