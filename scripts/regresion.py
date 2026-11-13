"""Unidad 3 (L13–L16): un R Markdown por modelo de regresión, con la estructura del proyecto modelo del docente
(carga, asignación de variables, tabla de pares, dispersión, conjetura, test de aprobación, restricciones,
pronósticos, conclusión) y el código de su plantilla Regresiones.R (lm sobre las variables transformadas).
Más la regresión múltiple (L15) y la serie de tiempo (L16).

Cada par de variables se eligió probando los cinco modelos en 28 pares (prueba y error): el modelo de cada documento
es el que mejor ajusta ese par, y cada documento muestra la comparación.

Uso: python scripts/regresion.py [nombre ...]
Salidas: R/regresion/*.Rmd, docs/rpubs/reg_*.html, docs/img/regresion/*.png, docs/data/regresion.json
"""
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

from inferencial import URL
from rpubs import AUTORES, RSCRIPT

RAIZ = Path(__file__).resolve().parent.parent
RMD = RAIZ / "R" / "regresion"
HTML = RAIZ / "docs" / "rpubs"
IMG = RAIZ / "docs" / "img" / "regresion"
RESUMEN = RAIZ / "docs" / "data" / "regresion"

CABECERA = '''---
title: "{titulo}"
subtitle: "Unidad 3 · Regresión · Geoquímica de rocas con datos de EarthChem PetDB"
author: "{autores}"
date: "Noviembre de 2026"
output:
  html_document:
    toc: true
    toc_float: true
    theme: flatly
    highlight: tango
---

> Proyecto estrictamente académico (Estadística y Probabilidades, FIGEMPA – UCE). Datos: EarthChem PetDB (CC BY 4.0),
> descargados el 13/10/2026. Web del proyecto: https://crisrumiguano-art.github.io/geoquimica-earthchem-ml/

## 1. Carga de datos

Se usa la base completa (159 760 análisis). Para cada par se toman solo las filas que tienen **los dos** datos: no se
inventa ningún valor que falte.

```{{r carga}}
knitr::opts_chunk$set(echo = TRUE, message = FALSE, warning = FALSE, fig.align = "center")
if (!file.exists("data/earthchem_limpio.csv.gz")) {{
  dir.create("data", showWarnings = FALSE)
  download.file("{url}data/earthchem_limpio.csv.gz", "data/earthchem_limpio.csv.gz", mode = "wb")
}}
base <- read.csv(gzfile("data/earthchem_limpio.csv.gz", encoding = "UTF-8"), check.names = FALSE)
dim(base)
```
'''

SIMPLE = '''
## 2. Asignación de variables

**x = {nx}** (variable independiente) e **y = {ny}** (variable dependiente). {porque}

```{{r variables}}
x <- base[["{cx}"]]
y <- base[["{cy}"]]
completos <- !is.na(x) & !is.na(y) & x > 0 & y > 0    # filas con los dos datos
x <- x[completos]
y <- y[completos]{filtro}
length(x)                                              # número de pares
```

## 3. Tabla de pares de valores

```{{r tabla}}
knitr::kable(head(data.frame(x, y), 10), caption = "Tabla N° 1: primeros 10 pares de valores ({nx}, {ny})")
knitr::kable(data.frame(variable = c("{nx}", "{ny}"), minimo = c(min(x), min(y)), media = c(mean(x), mean(y)),
                        maximo = c(max(x), max(y))), digits = 2, caption = "Tabla N° 2: resumen de los pares")
```

## 4. Diagrama de dispersión

```{{r dispersion, fig.width = 8, fig.height = 5.5}}
plot(x, y, pch = 16, cex = 0.4, col = rgb(0.22, 0.53, 0.9, 0.25), las = 1{logejes}{zoom},
     main = "Gráfica N° 1: Diagrama de dispersión", xlab = "{nx}", ylab = "{ny}")
```

{lectura_dispersion}

## 5. Conjetura del modelo

{conjetura} Antes de elegir se probaron los cinco modelos con este par (prueba y error): el coeficiente de
correlación de cada uno sale de la recta ajustada a las variables transformadas.

```{{r prueba}}
r_modelos <- c(lineal = cor(x, y),                     # y = a + b·x
               potencial = cor(log(x), log(y)),        # y = a·x^b      -> log y = log a + b·log x
               exponencial = cor(x, log(y)),           # y = a·e^(b·x)  -> log y = log a + b·x
               logaritmico = cor(log(x), y),           # y = a + b·ln x
               polinomico = sqrt(summary(lm(y ~ x + I(x^2) + I(x^3)))$r.squared))  # y = a + b·x + c·x² + d·x³
knitr::kable(data.frame(modelo = names(r_modelos), r = round(r_modelos, 3), r2_porcentaje = round(r_modelos^2 * 100, 1)),
             row.names = FALSE, caption = "Tabla N° 3: correlación de cada modelo con este par")
```

```{{r conjetura, fig.width = 8, fig.height = 5.5}}
{ajuste}
plot(x, y, pch = 16, cex = 0.4, col = rgb(0.22, 0.53, 0.9, 0.25), las = 1{logejes}{zoom},
     main = "Gráfica N° 2: Regresión {modelo}", xlab = "{nx}", ylab = "{ny}")
curve({curva}, from = min(x), to = max(x), add = TRUE, col = "#d95926", lwd = 3)
legend("{leyenda}", c("datos", "{ecuacion_leyenda}"), col = c(rgb(0.22, 0.53, 0.9), "#d95926"),
       pch = c(16, NA), lwd = c(NA, 3), bty = "n")
```
{manual}
## 6. Test de aprobación

El coeficiente de correlación de Pearson (r) mide qué tan fuerte es la relación: |r| cerca de 1 es fuerte. El
coeficiente de determinación (r² en %) dice qué parte de la variación de y explica el modelo.

```{{r test}}
r <- {r}
r2 <- r^2 * 100
knitr::kable(data.frame(modelo = "{modelo}", r = round(r, 4), r2_porcentaje = round(r2, 2),
                        fuerza = ifelse(abs(r) >= 0.7, "fuerte", ifelse(abs(r) >= 0.4, "moderada", "débil"))),
             caption = "Tabla N° 4: test de aprobación")
```

```{{r residuos, fig.width = 8, fig.height = 4.5}}
residuo <- {residuo}                                   # lo que el modelo no explica
plot(x, residuo, pch = 16, cex = 0.4, col = rgb(0.22, 0.53, 0.9, 0.25), las = 1{log_res}{zoom_x},
     ylim = quantile(residuo, c(0.0025, 0.9975)),           # sin el 0,5 % más extremo, para que se vea
     main = "Gráfica N° 3: Residuos del modelo", xlab = "{nx}", ylab = "{eje_res}")
abline(h = 0, col = "#d95926", lwd = 2)
```

## 7. Restricciones

{restricciones}

```{{r restricciones}}
{restriccion_codigo}
```

## 8. Estimación de pronósticos

**{pregunta}**

```{{r pronostico}}
x0 <- {x0}
y0 <- {prediccion_x0}
y0
```

## 9. Conclusión

Entre {nx} e {ny} existe una relación que se representa con un **modelo {modelo}**: {ecuacion_texto}, donde x es {nx}
e y es {ny}. La correlación es `r ifelse(abs(r) >= 0.7, "fuerte", ifelse(abs(r) >= 0.4, "moderada", "débil"))`
(r = `r round(r, 3)`): {ny} depende de {nx} en un `r round(r2, 1)` % y el `r round(100 - r2, 1)` % restante se debe a
otros factores que este modelo no considera. Si {nx} vale `r x0`, se espera {ny} ≈ `r round(y0, 2)`. {conclusion}

```{{r guardar, include = FALSE}}
if (dir.exists("docs/data")) {{
  dir.create("docs/data/regresion", showWarnings = FALSE)
  write.csv(data.frame(documento = "{nombre}", modelo = "{modelo}", x = "{nx}", y = "{ny}", n = length(x),
                       ecuacion = {ecuacion_r}, r = r, r2 = r2, pronostico = paste0("x = ", x0, " -> y = ", round(y0, 2))),
            "docs/data/regresion/{nombre}.csv", row.names = FALSE, fileEncoding = "UTF-8")
}}
```
'''

MANUAL_LINEAL = '''
**Mínimos cuadrados a mano.** La recta que hace mínima la suma de los residuos al cuadrado tiene pendiente
b = Sxy / Sxx e intercepto a = ȳ − b·x̄. Da lo mismo que `lm()`:

```{r manual}
Sxy <- sum((x - mean(x)) * (y - mean(y)))              # suma de productos cruzados
Sxx <- sum((x - mean(x))^2)                            # suma de cuadrados de x
b_manual <- Sxy / Sxx
a_manual <- mean(y) - b_manual * mean(x)
covarianza <- Sxy / (length(x) - 1)
c(a_manual = a_manual, b_manual = b_manual, a_lm = a, b_lm = b, covarianza = covarianza)
```
'''

REGRESIONES = [
    dict(nombre="reg_01_lineal_La_Ce", modelo="lineal", cx="La (ppm)", cy="Ce (ppm)", nx="La (ppm)", ny="Ce (ppm)",
         titulo="Regresión lineal: lantano y cerio",
         porque="Son tierras raras vecinas en la tabla periódica, con radio iónico y carga casi iguales: entran y salen "
                "juntas de los minerales, así que su proporción casi no cambia (Ce ≈ 2·La). Unos pocos análisis tienen "
                "La cercano a 1 000 ppm con apenas 26 ppm de Ce, una razón imposible en rocas naturales (errores de "
                "carga o anomalías de Ce extremas): tienen una distancia de Cook enorme y tiran la recta hacia abajo. Se "
                "ajusta con las rocas de razón Ce/La entre 0,5 y 5.",
         logejes="", lectura_dispersion="Los puntos forman una franja recta que sale del origen: a más La, más Ce.",
         conjetura="La nube es recta: se conjetura un **modelo lineal**, y = a + b·x.",
         ajuste='modelo <- lm(y ~ x)\na <- coef(modelo)[[1]]                              # intercepto\n'
                'b <- coef(modelo)[[2]]                              # pendiente\nc(a = a, b = b)',
         curva="a + b * x", leyenda="topleft", ecuacion_leyenda="y = a + b·x", manual=MANUAL_LINEAL,
         r="cor(x, y)", prediccion_y="a + b * x", x_residuo="x",
         restricciones="Se ajusta con rocas de razón Ce/La entre 0,5 y 5 (el 97 % de los pares). Una concentración no "
                       "puede ser negativa: y > 0 exige x > −a/b. El modelo solo vale dentro del rango medido de La; "
                       "fuera de él es extrapolar.",
         restriccion_codigo='c(x_minimo_valido = max(0, -a / b), x_min_datos = min(x), x_max_datos = max(x))',
         pregunta="Si un basalto tiene 20 ppm de La, ¿cuánto Ce se espera?", x0="20", prediccion_x0="a + b * x0",
         ecuacion_texto="y = `r round(a, 3)` + `r round(b, 3)`·x", ecuacion_r='paste0("y = ", round(a, 3), " + ", round(b, 3), "x")',
         conclusion="El Ce es casi el doble del La en las rocas, como se espera de dos tierras raras livianas."),
    dict(nombre="reg_02_potencial_Zr_Hf", modelo="potencial", cx="Zr (ppm)", cy="Hf (ppm)", nx="Zr (ppm)", ny="Hf (ppm)",
         titulo="Regresión potencial: circonio y hafnio",
         porque="El hafnio es el «gemelo» del circonio: los dos se alojan en el circón y casi nunca se separan.",
         logejes=', log = "xy"', lectura_dispersion="Con ejes logarítmicos los puntos forman una recta. En escala normal "
                "la correlación lineal es de apenas 0,15, porque unos pocos valores extremos (más de 10 000 ppm) dominan; en "
                "logaritmos todos los órdenes de magnitud pesan igual.",
         conjetura="Una recta en ejes log-log es un **modelo potencial**, y = a·x^b: log y = log a + b·log x.",
         ajuste='modelo <- lm(log(y) ~ log(x))\na <- exp(coef(modelo)[[1]])                         # a = e^(intercepto)\n'
                'b <- coef(modelo)[[2]]                               # exponente\nc(a = a, b = b)',
         curva="a * x^b", leyenda="topleft", ecuacion_leyenda="y = a·x^b", manual="",
         r="cor(log(x), log(y))", prediccion_y="a * x^b", x_residuo="x",
         restricciones="El modelo exige x > 0 (no existe el logaritmo de cero ni de un negativo) y da siempre y > 0. Se "
                       "aplica dentro del rango medido.",
         restriccion_codigo='c(x_debe_ser_mayor_que = 0, x_min_datos = min(x), x_max_datos = max(x))',
         pregunta="Si una roca tiene 150 ppm de Zr, ¿cuánto Hf se espera?", x0="150", prediccion_x0="a * x0^b",
         ecuacion_texto="y = `r round(a, 4)`·x^`r round(b, 3)`", ecuacion_r='paste0("y = ", round(a, 4), " x^", round(b, 3))',
         conclusion="La razón Zr/Hf es casi constante (alrededor de 40) en las rocas de la Tierra."),
    dict(nombre="reg_03_exponencial_SiO2_MgO", modelo="exponencial", cx="SiO2 (wt%)", cy="MgO (wt%)", nx="SiO2 (wt%)",
         ny="MgO (wt%)", titulo="Regresión exponencial: sílice y magnesio",
         porque="Cuando un magma se enfría, primero cristalizan el olivino y el piroxeno, ricos en magnesio: el líquido que "
                "queda tiene cada vez más sílice y menos magnesio (diferenciación magmática).",
         logejes="", lectura_dispersion="El MgO cae rápido al principio y después cada vez más lento: una curva que se "
                "aplana, no una recta.",
         conjetura="Una caída que se aplana es la forma de un **modelo exponencial**, y = a·e^(b·x), con b negativo: "
                   "log y = log a + b·x.",
         ajuste='modelo <- lm(log(y) ~ x)\na <- exp(coef(modelo)[[1]])\nb <- coef(modelo)[[2]]\nc(a = a, b = b)',
         curva="a * exp(b * x)", leyenda="topright", ecuacion_leyenda="y = a·e^(b·x)", manual="",
         r="cor(x, log(y))", prediccion_y="a * exp(b * x)", x_residuo="x",
         restricciones="El modelo se ajustó solo con rocas silicatadas (SiO2 entre 35 y 80 %): por debajo hay carbonatitas, "
                       "sulfuros o análisis parciales, que no siguen esta tendencia. Da siempre y > 0, pero fuera de ese "
                       "rango no vale: con SiO2 = 0 daría miles de % de MgO.",
         restriccion_codigo='c(x_min_datos = min(x), x_max_datos = max(x), y_en_x_100 = a * exp(b * 100))',
         pregunta="Si una roca tiene 60 % de SiO2 (una andesita), ¿cuánto MgO se espera?", x0="60",
         prediccion_x0="a * exp(b * x0)", ecuacion_texto="y = `r round(a, 2)`·e^(`r round(b, 4)`·x)",
         ecuacion_r='paste0("y = ", round(a, 2), " e^(", round(b, 4), "x)")',
         conclusion="A más sílice, menos magnesio: es la huella de la diferenciación magmática."),
    dict(nombre="reg_04_logaritmica_MgO_SiO2", modelo="logarítmico", cx="MgO (wt%)", cy="SiO2 (wt%)", nx="MgO (wt%)",
         ny="SiO2 (wt%)", titulo="Regresión logarítmica: magnesio y sílice",
         porque="Es la misma diferenciación magmática vista desde el otro lado (como en la plantilla del curso): las rocas con "
                "poco magnesio son las más evolucionadas y ricas en sílice.",
         logejes="", lectura_dispersion="La sílice baja muy rápido cuando el MgO sube de 0 a 10 % y después casi se "
                "estabiliza: una curva que se aplana.",
         conjetura="Una subida o bajada rápida que después se aplana es la forma del **modelo logarítmico**, y = a + b·ln x.",
         ajuste='modelo <- lm(y ~ log(x))\na <- coef(modelo)[[1]]\nb <- coef(modelo)[[2]]\nc(a = a, b = b)',
         curva="a + b * log(x)", leyenda="topright", ecuacion_leyenda="y = a + b·ln x", manual="",
         r="cor(log(x), y)", prediccion_y="a + b * log(x)", x_residuo="x",
         restricciones="Se usan solo rocas silicatadas (SiO2 entre 35 y 80 %). El logaritmo exige x > 0. Además y debe "
                       "ser positivo: con b negativo, y > 0 solo si x < e^(−a/b). Fuera de ese valor el modelo daría "
                       "sílice negativa, imposible.",
         restriccion_codigo='c(x_debe_ser_mayor_que = 0, x_maximo_valido = exp(-a / b), x_max_datos = max(x))',
         pregunta="Si una roca tiene 3 % de MgO, ¿cuánta sílice se espera?", x0="3", prediccion_x0="a + b * log(x0)",
         ecuacion_texto="y = `r round(a, 3)` + (`r round(b, 3)`)·ln x", ecuacion_r='paste0("y = ", round(a, 3), " + ", round(b, 3), " ln(x)")',
         conclusion="El MgO sirve para estimar qué tan evolucionada está una roca."),
    dict(nombre="reg_05_polinomica_MgO_CaO", modelo="polinómico", cx="MgO (wt%)", cy="CaO (wt%)", nx="MgO (wt%)",
         ny="CaO (wt%)", titulo="Regresión polinómica: magnesio y calcio",
         porque="El calcio sube con el magnesio en los basaltos (plagioclasa y clinopiroxeno) y vuelve a bajar en las "
                "peridotitas, donde domina el olivino, que casi no lleva calcio.",
         logejes="", lectura_dispersion="El CaO sube hasta un máximo cerca de 14 % de MgO y después baja: una curva con "
                "joroba. Una recta no puede seguirla (r lineal = −0,28).",
         conjetura="Una curva que sube y baja es la forma de un **modelo polinómico**, aquí de grado 3: "
                   "y = a + b·x + c·x² + d·x³.",
         ajuste='modelo <- lm(y ~ x + I(x^2) + I(x^3))\na <- coef(modelo)[[1]]\nb <- coef(modelo)[[2]]\n'
                'c <- coef(modelo)[[3]]\nd <- coef(modelo)[[4]]\nc(a = a, b = b, c = c, d = d)',
         curva="a + b * x + c * x^2 + d * x^3", leyenda="topright", ecuacion_leyenda="y = a + b·x + c·x² + d·x³", manual="",
         r="sqrt(summary(modelo)$r.squared)", prediccion_y="a + b * x + c * x^2 + d * x^3", x_residuo="x",
         restricciones="Un polinomio se dispara fuera del rango de los datos (riesgo de sobreajuste si se sube el grado). "
                       "Además el CaO debe ser positivo: se busca dónde la curva baja de cero.",
         restriccion_codigo='xs <- seq(min(x), max(x), length.out = 2000)\nys <- a + b * xs + c * xs^2 + d * xs^3\n'
                            'c(x_min_datos = min(x), x_max_datos = max(x),\n'
                            '  primer_x_con_y_negativo = if (any(ys < 0)) xs[which(ys < 0)[1]] else NA,\n'
                            '  x_del_maximo = xs[which.max(ys)])',
         pregunta="Si un basalto tiene 8 % de MgO, ¿cuánto CaO se espera?", x0="8",
         prediccion_x0="a + b * x0 + c * x0^2 + d * x0^3",
         ecuacion_texto="y = `r round(a, 3)` + `r round(b, 3)`·x + (`r round(c, 4)`)·x² + `r signif(d, 3)`·x³",
         ecuacion_r='paste0("y = ", round(a, 3), " + ", round(b, 3), "x + ", round(c, 4), "x² + ", signif(d, 3), "x³")',
         conclusion="Una sola curva describe dos tipos de roca distintos: basaltos a la izquierda del máximo y peridotitas a la derecha."),
]

MULTIPLE = '''
## 2. Asignación de variables

**y = Nd (ppm)**, explicada por **x1 = La (ppm)** y **x2 = Sm (ppm)**: el neodimio está entre el lantano y el samario
en la serie de las tierras raras, así que debería poder estimarse con sus dos vecinos. Además se agrega una variable
cualitativa, el ambiente tectónico, como **variable ficticia (dummy)**.

```{r variables}
datos <- data.frame(Nd = base[["Nd (ppm)"]], La = base[["La (ppm)"]], Sm = base[["Sm (ppm)"]],
                    grupo = base[["Tectonic Group"]])
datos <- na.omit(datos)                                # filas con todo completo
datos <- datos[datos$Nd > 0 & datos$La > 0 & datos$Sm > 0 & datos$grupo != "mixto", ]
nrow(datos)
```

## 3. Tabla de valores

```{r tabla}
knitr::kable(head(datos, 10), caption = "Tabla N° 1: primeras 10 filas")
```

## 4. Diagrama de dispersión y matriz de correlación

```{r dispersion, fig.width = 8, fig.height = 7}
set.seed(2026)
dibujo <- datos[sample(nrow(datos), 3000), c("Nd", "La", "Sm")]   # 3000 puntos para que se vea
dibujo <- dibujo[dibujo$Nd < quantile(datos$Nd, 0.995), ]          # sin el 0,5 % más extremo
pairs(dibujo, pch = 16, cex = 0.4, col = rgb(0.22, 0.53, 0.9, 0.3), main = "Gráfica N° 1: Dispersión por pares")
R <- cor(datos[, c("Nd", "La", "Sm")])
knitr::kable(round(R, 3), caption = "Tabla N° 2: matriz de correlación")
```

Las dos explicativas están muy correlacionadas entre sí (La–Sm r = `r round(R["La", "Sm"], 2)`): es
**multicolinealidad**. No impide predecir, pero hace que los coeficientes por separado sean menos estables.

```{r vif}
r2_La_Sm <- summary(lm(La ~ Sm, data = datos))$r.squared
VIF <- 1 / (1 - r2_La_Sm)                              # factor de inflación de la varianza
VIF                                                    # más de 10 = multicolinealidad fuerte
```

## 5. Conjetura del modelo

Modelo lineal múltiple: y = a + b1·x1 + b2·x2. En forma matricial, β = (XᵀX)⁻¹·Xᵀy; `lm()` hace ese cálculo.

```{r conjetura}
modelo <- lm(Nd ~ La + Sm, data = datos)
coef(modelo)
# El mismo cálculo con matrices:
X <- cbind(1, datos$La, datos$Sm)
beta <- solve(t(X) %*% X) %*% t(X) %*% datos$Nd
round(t(beta), 4)
```

```{r plano, fig.width = 8, fig.height = 5.5}
predicho <- predict(modelo)
plot(predicho, datos$Nd, pch = 16, cex = 0.4, col = rgb(0.22, 0.53, 0.9, 0.25), las = 1,
     xlim = c(0, quantile(datos$Nd, 0.995)), ylim = c(0, quantile(datos$Nd, 0.995)),   # zoom al 99,5 %
     main = "Gráfica N° 2: Nd real vs Nd del modelo", xlab = "Nd del modelo (ppm)", ylab = "Nd real (ppm)")
abline(a = 0, b = 1, col = "#d95926", lwd = 3)
```

**Con variable ficticia.** El ambiente tectónico entra como dos columnas 0/1 (la tercera categoría es la referencia).

```{r dummy}
modelo_dummy <- lm(Nd ~ La + Sm + grupo, data = datos)
round(coef(modelo_dummy), 4)
c(R2_sin_dummy = summary(modelo)$r.squared, R2_con_dummy = summary(modelo_dummy)$r.squared)
```

## 6. Test de aprobación

```{r test}
R2 <- summary(modelo)$r.squared * 100
r <- sqrt(R2 / 100)                                    # correlación múltiple
knitr::kable(data.frame(modelo = "múltiple", R = round(r, 4), R2_porcentaje = round(R2, 2)),
             caption = "Tabla N° 3: test de aprobación")
```

```{r residuos, fig.width = 8, fig.height = 4.5}
plot(predicho, residuals(modelo), pch = 16, cex = 0.4, col = rgb(0.22, 0.53, 0.9, 0.25), las = 1,
     xlim = c(0, quantile(datos$Nd, 0.995)), ylim = quantile(residuals(modelo), c(0.0025, 0.9975)),
     main = "Gráfica N° 3: Residuos", xlab = "Nd del modelo (ppm)", ylab = "Residuo (ppm)")
abline(h = 0, col = "#d95926", lwd = 2)
```

## 7. Restricciones

Las concentraciones son positivas: el modelo vale dentro del rango medido de La y Sm, y para combinaciones
que existen en la naturaleza (La y Sm suben juntos; un La muy alto con Sm muy bajo no se da).

```{r restricciones}
sapply(datos[, c("La", "Sm")], range)
```

## 8. Estimación de pronósticos

**Si una roca tiene 20 ppm de La y 5 ppm de Sm, ¿cuánto Nd se espera?**

```{r pronostico}
nuevo <- data.frame(La = 20, Sm = 5)
y0 <- predict(modelo, nuevo)
y0
```

## 9. Conclusión

El Nd se representa con un **modelo lineal múltiple**: y = `r round(coef(modelo)[1], 3)` + `r round(coef(modelo)[2], 3)`·x1 +
`r round(coef(modelo)[3], 3)`·x2, donde x1 es La y x2 es Sm. El modelo explica el `r round(R2, 1)` % de la variación del
Nd. Para La = 20 ppm y Sm = 5 ppm se espera Nd ≈ `r round(y0, 2)` ppm. Agregar el ambiente tectónico como variable
ficticia casi no mejora el ajuste: las tierras raras se mueven juntas en cualquier ambiente.

```{r guardar, include = FALSE}
if (dir.exists("docs/data")) {
  dir.create("docs/data/regresion", showWarnings = FALSE)
  write.csv(data.frame(documento = "reg_06_multiple_Nd", modelo = "múltiple", x = "La (ppm), Sm (ppm)", y = "Nd (ppm)",
                       n = nrow(datos), ecuacion = paste0("y = ", round(coef(modelo)[1], 3), " + ", round(coef(modelo)[2], 3),
                       "x1 + ", round(coef(modelo)[3], 3), "x2"), r = r, r2 = R2,
                       pronostico = paste0("La = 20, Sm = 5 -> Nd = ", round(y0, 2))),
            "docs/data/regresion/reg_06_multiple_Nd.csv", row.names = FALSE, fileEncoding = "UTF-8")
}
```
'''

SERIE = '''
## 2. La serie

Cantidad de análisis de la base publicados cada año, de 1965 a 2024 (2025 está incompleto porque la base se descargó
en octubre de 2026 y las publicaciones tardan en cargarse).

```{r serie}
anio <- base[["Publication Year"]]
conteo <- table(factor(anio, levels = 1965:2024))
serie <- ts(as.vector(conteo), start = 1965)           # serie de tiempo anual
knitr::kable(data.frame(anio = 1965:2024, analisis = as.vector(conteo))[seq(1, 60, by = 5), ], row.names = FALSE,
             caption = "Tabla N° 1: análisis publicados (cada 5 años)")
plot(serie, lwd = 2, col = "#3987e5", las = 1, main = "Gráfica N° 1: Análisis publicados por año",
     xlab = "Año", ylab = "Análisis")
```

## 3. Componentes

- **Tendencia**: la serie crece de largo plazo (más laboratorios y técnicas más rápidas, como el ICP-MS desde 1990).
- **Ciclo**: subidas y bajadas de varios años, ligadas a grandes campañas de perforación oceánica (DSDP, ODP, IODP).
- **Aleatoriedad**: picos de un solo año por trabajos que publican miles de análisis juntos.
- **Estacionalidad**: no se puede ver, porque el dato es anual (la estacionalidad se repite dentro del año).

Por eso se usa un **modelo aditivo**: serie = tendencia + ciclo + aleatoriedad.

## 4. Tendencia por regresión

```{r tendencia}
t <- 1:length(serie)
lineal <- lm(as.vector(serie) ~ t)
cuadratica <- lm(as.vector(serie) ~ t + I(t^2))
c(R2_lineal = summary(lineal)$r.squared, R2_cuadratica = summary(cuadratica)$r.squared)
plot(serie, lwd = 2, col = "gray60", las = 1, main = "Gráfica N° 2: Tendencia", xlab = "Año", ylab = "Análisis")
lines(1965:2024, fitted(lineal), col = "#3987e5", lwd = 2)
lines(1965:2024, fitted(cuadratica), col = "#d95926", lwd = 2)
legend("topleft", c("serie", "tendencia lineal", "tendencia cuadrática"), col = c("gray60", "#3987e5", "#d95926"),
       lwd = 2, bty = "n")
```

## 5. Medias móviles

Cada valor se reemplaza por el promedio de los 5 años centrados en él: se borra la aleatoriedad y queda la tendencia
con el ciclo.

```{r moviles}
movil <- stats::filter(serie, rep(1 / 5, 5), sides = 2)    # media móvil de 5 años
plot(serie, lwd = 1, col = "gray60", las = 1, main = "Gráfica N° 3: Media móvil de 5 años", xlab = "Año", ylab = "Análisis")
lines(movil, col = "#3987e5", lwd = 3)
```

## 6. Suavización exponencial

Cada pronóstico mezcla el último dato con el pronóstico anterior; `HoltWinters()` elige el peso (α) y, con tendencia,
también β (método de Holt).

```{r suavizacion}
holt <- HoltWinters(serie, gamma = FALSE)              # sin estacionalidad
c(alfa = holt$alpha, beta = holt$beta)
plot(holt, las = 1, main = "Gráfica N° 4: Suavización exponencial (Holt)", xlab = "Año", ylab = "Análisis")
```

## 7. Pronóstico 2025–2029

```{r pronostico}
futuro <- 2025:2029
p_lineal <- predict(lineal, data.frame(t = length(serie) + 1:5))
p_cuad <- predict(cuadratica, data.frame(t = length(serie) + 1:5))
p_movil <- rep(mean(tail(serie, 5)), 5)                # media de los últimos 5 años
p_holt <- predict(holt, n.ahead = 5)
pron <- data.frame(anio = futuro, tendencia_lineal = round(p_lineal), tendencia_cuadratica = round(p_cuad),
                   media_movil = round(p_movil), holt = round(as.vector(p_holt)))
knitr::kable(pron, caption = "Tabla N° 2: pronóstico con las tres técnicas")
plot(serie, xlim = c(1965, 2029), ylim = range(0, serie, pron[, -1]), lwd = 2, col = "gray60", las = 1,
     main = "Gráfica N° 5: Pronóstico", xlab = "Año", ylab = "Análisis")
lines(futuro, pron$tendencia_cuadratica, col = "#d95926", lwd = 2, type = "b", pch = 16)
lines(futuro, pron$media_movil, col = "#3987e5", lwd = 2, type = "b", pch = 17)
lines(futuro, pron$holt, col = "#1baa9b", lwd = 2, type = "b", pch = 15)
legend("topleft", c("serie", "tendencia cuadrática", "media móvil", "Holt"), col = c("gray60", "#d95926", "#3987e5", "#1baa9b"),
       lwd = 2, bty = "n")
```

## 8. Conclusión

La cantidad de análisis publicados por año crece de largo plazo, con ciclos y picos de un año. La tendencia cuadrática
explica el `r round(summary(cuadratica)$r.squared * 100, 1)` % de la variación. Los tres métodos dan pronósticos
distintos: la tendencia sigue subiendo, mientras que la media móvil y Holt se quedan cerca del nivel de los últimos años.
Con datos de publicaciones, que dependen de campañas y de cuántos autores cargan sus datos a PetDB, el pronóstico más
prudente es el de los métodos que siguen el nivel reciente.
'''


CE_LA = """
# Influencia: la distancia de Cook mide cuánto cambia la recta si se quita cada punto
todos <- lm(y ~ x)
cook <- cooks.distance(todos)
head(data.frame(La = x, Ce = y, cook = round(cook, 2))[order(-cook), ], 5)   # los 5 puntos más influyentes
razon <- y / x                                         # Ce/La: en rocas naturales está entre 0,5 y 5
natural <- razon >= 0.5 & razon <= 5
c(pares = length(x), fuera_de_0.5_a_5 = sum(!natural), porcentaje = round(mean(!natural) * 100, 1))
c(pendiente_con_todos = coef(todos)[[2]], pendiente_sin_esos = coef(lm(y[natural] ~ x[natural]))[[2]])
x <- x[natural]                                        # el modelo se ajusta sin ellos (no se borran de la base)
y <- y[natural]"""
COMUN = dict(filtro="", zoom="", zoom_x="", log_res="", eje_res="Residuo (y real - y del modelo)")
ZOOM = ", xlim = c(0, quantile(x, 0.995)), ylim = c(0, quantile(y, 0.995))"  # zoom al 99,5 %; el modelo usa todos
SILICATADAS = ("\nsilicatada <- {v} >= 35 & {v} <= 80                    # rocas silicatadas (restricción del dominio)\n"
               "x <- x[silicatada]\ny <- y[silicatada]")
EXTRA = {
    "reg_01_lineal_La_Ce": dict(zoom=ZOOM, zoom_x=", xlim = c(0, quantile(x, 0.995))", residuo="y - (a + b * x)",
                                filtro=CE_LA),
    "reg_02_potencial_Zr_Hf": dict(residuo="log(y) - log(a * x^b)", log_res=', log = "x"',
                                   eje_res="Residuo en logaritmo (ln y real - ln y del modelo)"),
    "reg_03_exponencial_SiO2_MgO": dict(filtro=SILICATADAS.format(v="x"), residuo="log(y) - log(a * exp(b * x))",
                                        eje_res="Residuo en logaritmo (ln y real - ln y del modelo)"),
    "reg_04_logaritmica_MgO_SiO2": dict(filtro=SILICATADAS.format(v="y"), residuo="y - (a + b * log(x))"),
    "reg_05_polinomica_MgO_CaO": dict(residuo="y - (a + b * x + c * x^2 + d * x^3)"),
}


def main():
    for d in (RMD, HTML, IMG, RESUMEN):
        d.mkdir(parents=True, exist_ok=True)
    docs = {c["nombre"]: CABECERA.format(titulo=c["titulo"], autores=AUTORES, url=URL)
            + SIMPLE.format(**(COMUN | c | EXTRA[c["nombre"]]))
            for c in REGRESIONES}
    docs["reg_06_multiple_Nd"] = CABECERA.format(titulo="Regresión lineal múltiple: neodimio, lantano y samario",
                                                 autores=AUTORES, url=URL) + MULTIPLE
    docs["reg_07_serie_de_tiempo"] = CABECERA.format(titulo="Serie de tiempo: análisis publicados por año",
                                                     autores=AUTORES, url=URL) + SERIE
    for nombre, texto in docs.items():
        (RMD / f"{nombre}.Rmd").write_text(texto, encoding="utf-8")
    solo = sys.argv[1:] or list(docs)
    codigo = ("for (f in commandArgs(TRUE)) rmarkdown::render(file.path('R/regresion', paste0(f, '.Rmd')), "
              "output_dir = 'docs/rpubs', knit_root_dir = getwd(), quiet = TRUE, envir = new.env(), clean = FALSE)")
    script = RMD / "_render.R"
    script.write_text(codigo, encoding="utf-8")
    try:
        subprocess.run([RSCRIPT, str(script), *solo], cwd=RAIZ, check=True)
    finally:
        script.unlink()
    for nombre in solo:  # figuras para la web (clean = FALSE las deja en docs/rpubs/<nombre>_files/)
        for png in (HTML / f"{nombre}_files" / "figure-html").glob("*.png"):
            shutil.copy(png, IMG / f"{nombre}-{png.name.replace('-1.png', '.png')}")
        shutil.rmtree(HTML / f"{nombre}_files", ignore_errors=True)
        for resto in [*RMD.glob(f"{nombre}.*"), *HTML.glob(f"{nombre}.*")]:
            if resto.suffix not in (".Rmd", ".html"):
                resto.unlink()
    filas = []
    for archivo in sorted(RESUMEN.glob("*.csv")):
        filas += list(csv.DictReader(archivo.read_text(encoding="utf-8").splitlines()))
    (RAIZ / "docs" / "data" / "regresion.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(solo)} documentos -> {HTML}; figuras -> {IMG}")


if __name__ == "__main__":
    main()
