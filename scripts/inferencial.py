"""Unidad 2 (L8–L11): un R Markdown por modelo probabilístico, con la estructura del proyecto modelo del docente
(carga, tabla, gráfica, conjetura del modelo, test de aprobación, probabilidades, intervalos de confianza,
conclusión) y el código de su plantilla Distribuciones.R (fitdistr, curva sobre el histograma, chi-cuadrado).

La inferencia usa la muestra aleatoria simple de la Lección 3 (data/muestras/muestra_aleatoria.csv, n = 1 061):
con los 159 760 análisis el chi-cuadrado rechaza cualquier modelo por diferencias mínimas. Las variables y
modelos se eligieron probando (ver openwiki/workflows): cada uno pasa el chi-cuadrado al 95 %.

Uso: python scripts/inferencial.py [nombre ...]
Salidas: R/inferencial/*.Rmd, docs/rpubs/inf_*.html, docs/img/inferencial/*.png, docs/data/inferencial.json
"""
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

from rpubs import AUTORES, RSCRIPT

RAIZ = Path(__file__).resolve().parent.parent
RMD = RAIZ / "R" / "inferencial"
HTML = RAIZ / "docs" / "rpubs"
IMG = RAIZ / "docs" / "img" / "inferencial"
RESUMEN = RAIZ / "docs" / "data" / "inferencial"
URL = "https://github.com/crisrumiguano-art/geoquimica-earthchem-ml/raw/main/"

CABECERA = '''---
title: "{titulo}"
subtitle: "Unidad 2 · Estadística inferencial · Geoquímica de rocas con datos de EarthChem PetDB"
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

La inferencia se hace con la **muestra aleatoria simple** de la Lección 3: 1 061 análisis sorteados de los 159 760 de
la base (semilla 2026). Con la base entera, el test de chi-cuadrado rechaza cualquier modelo por diferencias mínimas;
con una muestra aleatoria mide lo que importa. La base completa se usa al final para comprobar el intervalo de confianza.

```{{r carga}}
knitr::opts_chunk$set(echo = TRUE, message = FALSE, warning = FALSE, fig.align = "center")
library(MASS)          # fitdistr(): estima los parámetros del modelo (viene con R)
dir.create("data/muestras", recursive = TRUE, showWarnings = FALSE)
if (!file.exists("data/muestras/muestra_aleatoria.csv")) {{
  download.file("{url}data/muestras/muestra_aleatoria.csv", "data/muestras/muestra_aleatoria.csv", mode = "wb")
}}
muestra <- read.csv("data/muestras/muestra_aleatoria.csv", check.names = FALSE)
dim(muestra)           # filas y columnas
```
'''

# Al final de cada documento: guarda el resumen para la página web (no se muestra en el documento).
GUARDAR = '''
```{{r guardar, include = FALSE}}
if (dir.exists("docs/data")) {{
  dir.create("docs/data/inferencial", showWarnings = FALSE)
  write.csv(data.frame(documento = "{nombre}", variable = "{etiqueta}", tipo = "{tipo}", modelo = "{modelo}",
                       parametros = {parametros}, n = {n_resumen}, chi2 = x2, umbral = umbral, pearson = pearson,
                       ic = {ic_texto}, real = {real}),
            "docs/data/inferencial/{nombre}.csv", row.names = FALSE, fileEncoding = "UTF-8")
}}
```
'''

CONTINUA = '''
## 2. Tabla de distribución de cantidad

Se toma {etiqueta} de las **rocas volcánicas máficas** (basaltos y afines) de la muestra. Mezclar todos los tipos de
roca da una distribución con varios picos que ningún modelo simple describe. Como en la plantilla del curso, los
valores atípicos (regla de la caja) quedan fuera del ajuste: el modelo describe a los basaltos típicos. No se borran de
la base y se informan aquí.

```{{r tabla}}
{calc_muestra}
tipo <- muestra[["Sample Type"]]
x <- x[tipo == "igneous:volcanic:mafic" & !is.na(x) & x > 0]   # basaltos con dato
caja <- boxplot(x, plot = FALSE)                       # límites de la caja (bigotes)
atipicos <- x[x < caja$stats[1] | x > caja$stats[5]]
x <- x[x >= caja$stats[1] & x <= caja$stats[5]]        # datos para el modelo
c(basaltos_con_dato = length(x) + length(atipicos), atipicos = length(atipicos), para_el_modelo = length(x))

h <- hist(x, plot = FALSE)                             # intervalos de Sturges (como hist() en la plantilla)
Li <- h$breaks[-length(h$breaks)]                      # límites inferiores
Ls <- h$breaks[-1]                                     # límites superiores
ni <- h$counts                                         # frecuencia absoluta
hi <- round(ni / sum(ni) * 100, 2)                     # frecuencia relativa (%)
TDF <- data.frame(Li, Ls, MC = h$mids, ni, hi)
knitr::kable(TDF, caption = "Tabla N° 1: distribución de {etiqueta} en basaltos (muestra aleatoria)")
```

## 3. Gráfica de distribución de cantidad

```{{r grafica, fig.width = 8, fig.height = 4.8}}
hist(x, breaks = h$breaks, col = "#86b6ef", border = "white", las = 1,
     main = "Gráfica N° 1: Distribución de {etiqueta} en basaltos", xlab = "{eje}", ylab = "Cantidad (ni)")
```

{forma}

## 4. Conjetura del modelo

Por la forma del histograma se conjetura un **modelo {modelo}**. `fitdistr()` estima sus parámetros con los datos
(máxima verosimilitud).

```{{r conjetura, fig.width = 8, fig.height = 4.8}}
ajuste <- fitdistr(x, {fit})
ajuste                                                 # parámetros estimados y su error estándar
{param}
techo <- max(h$density, {d_grid}) * 1.1                # alto del gráfico: que entren barras y curva
hist(x, breaks = h$breaks, freq = FALSE, col = "#86b6ef", border = "white", las = 1, ylim = c(0, techo),
     main = "Gráfica N° 2: Histograma y modelo {modelo} de {etiqueta}", xlab = "{eje}", ylab = "Densidad de probabilidad")
curve({d_curva}, add = TRUE, col = "#d95926", lwd = 3)   # curva del modelo
legend("topright", c("datos", "modelo {modelo}"), col = c("#86b6ef", "#d95926"), pch = c(15, NA),
       pt.cex = 2, lwd = c(NA, 3), bty = "n")

# Frecuencias observadas (Fo, los datos) y esperadas (Fe, lo que diría el modelo) en cada intervalo
Fo <- ni
P <- {p_Ls} - {p_Li}                                   # probabilidad de cada intervalo según el modelo
Fe <- P * sum(Fo)
knitr::kable(data.frame(Li, Ls, Fo, Fe = round(Fe, 2)), caption = "Tabla N° 2: frecuencias observadas y esperadas")
```

## 5. Test de aprobación

Dos pruebas, como en la plantilla: la **correlación de Pearson** entre Fo y Fe (si el modelo es bueno, los puntos caen
sobre la recta y = x) y el **chi-cuadrado**, que se compara con el umbral de la tabla al 95 % de confianza.

```{{r test, fig.width = 6, fig.height = 5}}
lim <- range(0, Fo / sum(Fo) * 100, Fe / sum(Fo) * 100)   # mismos ejes en x e y
plot(Fo / sum(Fo) * 100, Fe / sum(Fo) * 100, pch = 19, col = "#3987e5", las = 1, xlim = lim, ylim = lim,
     main = "Gráfica N° 3: Frecuencia observada vs esperada", xlab = "Observada (%)", ylab = "Esperada (%)")
abline(a = 0, b = 1, col = "#d95926", lwd = 2)         # recta y = x: ajuste perfecto

pearson <- cor(Fo, Fe) * 100                           # en %
gl <- length(Fo) - 1                                   # grados de libertad
x2 <- sum((Fo - Fe)^2 / Fe)                            # chi-cuadrado calculado
umbral <- qchisq(0.95, gl)                             # valor crítico (95 %)
resultado <- ifelse(x2 < umbral, "se acepta el modelo", "se rechaza el modelo")
knitr::kable(data.frame(Variable = "{etiqueta}", Pearson = round(pearson, 2), Chi_cuadrado = round(x2, 2),
                        Umbral = round(umbral, 2), Resultado = resultado),
             caption = "Tabla N° 3: pruebas de bondad de ajuste")
```

El chi-cuadrado (`r round(x2, 2)`) es `r ifelse(x2 < umbral, "menor", "mayor")` que el umbral (`r round(umbral, 2)`):
`r resultado`. La correlación entre lo observado y lo esperado es de `r round(pearson, 1)` %.

## 6. Estimación de probabilidades

**{pregunta1}**

```{{r prob1, fig.width = 8, fig.height = 4.8}}
p1 <- {p1}
p1 * 100                                               # en %
xs <- seq(min(x), max(x), length.out = 400)
plot(xs, {d_xs}, type = "l", lwd = 2, las = 1, main = "Gráfica N° 4: {titulo_p1}",
     xlab = "{eje}", ylab = "Densidad de probabilidad")
zona <- xs[{zona1}]                                    # parte de la curva que se pinta
polygon(c(zona[1], zona, zona[length(zona)]), c(0, {d_zona}, 0), col = rgb(0.85, 0.35, 0.15, 0.5), border = NA)
legend("topright", paste0("P = ", round(p1 * 100, 2), " %"), bty = "n", cex = 1.1)
```

**{pregunta2}**

```{{r prob2}}
p2 <- {p2}
c(probabilidad = p2 * 100, basaltos_esperados_de_50 = p2 * 50)
```

## 7. Intervalos de confianza

Intervalo de confianza para la **media poblacional** de {etiqueta} en basaltos, con todos los basaltos de la muestra
(también los atípicos: aquí no se ajusta un modelo, se estima la media). Por el Teorema del Límite Central, la media de
una muestra grande se distribuye normal con error estándar σ/√n; se toma σ = la desviación de la muestra (n grande).

```{{r ic}}
todos <- c(x, atipicos)                                # todos los basaltos con dato
n <- length(todos)
media_m <- mean(todos)
sigma <- sd(todos)
z <- qnorm(0.975)                                      # 1,96 para el 95 %
E <- z * sigma / sqrt(n)                               # error máximo de estimación
IC <- c(inferior = media_m - E, media = media_m, superior = media_m + E)
round(IC, 3)
n_necesario <- ceiling((z * sigma / (E / 2))^2)        # tamaño para un error la mitad de grande
n_necesario
```

**Comprobación con la base completa.** La población real se conoce: ¿el intervalo contiene la media de todos los
basaltos de la base?

```{{r comprobacion, fig.width = 8, fig.height = 3.2}}
if (!file.exists("data/earthchem_limpio.csv.gz")) {{
  download.file("{url}data/earthchem_limpio.csv.gz", "data/earthchem_limpio.csv.gz", mode = "wb")
}}
base <- read.csv(gzfile("data/earthchem_limpio.csv.gz", encoding = "UTF-8"), check.names = FALSE)
{calc_base}
poblacion <- poblacion[base[["Sample Type"]] == "igneous:volcanic:mafic"]
poblacion <- poblacion[!is.na(poblacion) & poblacion > 0]
media_real <- mean(poblacion)
c(media_real = media_real, dentro_del_intervalo = media_real >= IC[["inferior"]] & media_real <= IC[["superior"]])
plot(IC, c(1, 1, 1), type = "b", pch = c(91, 19, 93), cex = 2, yaxt = "n", ylab = "", xlab = "{eje}",
     xlim = range(c(IC, media_real)) + c(-E, E), main = "Gráfica N° 5: Intervalo del 95 % y media real")
abline(v = media_real, col = "#d95926", lwd = 2, lty = 2)
legend("topright", c("intervalo (muestra)", "media real (base)"), col = c("black", "#d95926"),
       lty = c(1, 2), lwd = 2, bty = "n")
```
{tlc}
## 8. Conclusión

El comportamiento de {etiqueta} en los basaltos se representa con un **modelo {modelo}** de parámetros {param_texto}
(chi-cuadrado `r round(x2, 2)` < umbral `r round(umbral, 2)`; Pearson `r round(pearson, 1)` %). {conclusion} Con el
95 % de confianza, la media poblacional está entre `r round(IC[["inferior"]], 2)` y `r round(IC[["superior"]], 2)`
{unidad}, y la media real de la base (`r round(media_real, 2)`) `r ifelse(media_real >= IC[["inferior"]] & media_real <= IC[["superior"]], "cae dentro", "queda fuera")`
del intervalo.
'''

TLC = '''
**Teorema del Límite Central.** Si se sacan muchas muestras de 30 basaltos de la base y se calcula la media de cada
una, esas medias forman una campana normal centrada en la media real, con desviación σ/√30, aunque los datos
originales no sean normales.

```{r tlc, fig.width = 8, fig.height = 4.8}
set.seed(2026)
medias <- replicate(1000, mean(sample(poblacion, 30)))  # 1000 muestras de 30
hist(medias, breaks = 30, freq = FALSE, col = "#86b6ef", border = "white", las = 1,
     main = "Gráfica N° 6: Medias de 1000 muestras de 30 basaltos", xlab = "Media de la muestra", ylab = "Densidad")
curve(dnorm(x, mean(poblacion), sd(poblacion) / sqrt(30)), add = TRUE, col = "#d95926", lwd = 3)
c(desviacion_de_las_medias = sd(medias), sigma_sobre_raiz_n = sd(poblacion) / sqrt(30))
```
'''

MODELOS = {  # parámetros, densidad y acumulada de cada modelo continuo (Q = valor)
    "normal": dict(fit='"normal"', param='media <- ajuste$estimate[["mean"]]\ndesv <- ajuste$estimate[["sd"]]',
                   d="dnorm(Q, media, desv)", p="pnorm(Q, media, desv)", parametros='paste0("media = ", round(media, 3), "; desviación = ", round(desv, 3))',
                   texto="media = `r round(media, 2)` y desviación = `r round(desv, 2)`"),
    "log-normal": dict(fit='"lognormal"', param='media_log <- ajuste$estimate[["meanlog"]]\ndesv_log <- ajuste$estimate[["sdlog"]]',
                       d="dlnorm(Q, media_log, desv_log)", p="plnorm(Q, media_log, desv_log)",
                       parametros='paste0("media log = ", round(media_log, 3), "; desviación log = ", round(desv_log, 3))',
                       texto="media logarítmica = `r round(media_log, 3)` y desviación logarítmica = `r round(desv_log, 3)`"),
    "exponencial": dict(fit='"exponential"', param='lambda <- ajuste$estimate[["rate"]]   # tasa',
                        d="dexp(Q, lambda)", p="pexp(Q, lambda)", parametros='paste0("lambda = ", round(lambda, 3))',
                        texto="λ = `r round(lambda, 3)` (media 1/λ = `r round(1 / lambda, 2)`)"),
}

MODELOS["beta"] = dict(
    fit='"beta", start = list(shape1 = 2, shape2 = 2)',   # la beta necesita valores de partida
    param='a <- ajuste$estimate[["shape1"]]\nb <- ajuste$estimate[["shape2"]]',
    d="dbeta(Q, a, b)", p="pbeta(Q, a, b)", parametros='paste0("a = ", round(a, 2), "; b = ", round(b, 2))',
    texto="forma a = `r round(a, 2)` y forma b = `r round(b, 2)` (media a/(a+b) = `r round(a / (a + b), 3)`)")

# Número de magnesio: Mg# = Mg / (Mg + Fe) en moles. Es una proporción (0 a 1): la variable natural para la beta.
MG_NUMERO = """VAR <- DF[["FeOT (wt%)"]]                             # hierro total como FeO
otra <- DF[["FeO (wt%)"]] + 0.8998 * DF[["Fe2O3 (wt%)"]]   # si falta, se calcula: FeOT = FeO + 0,8998·Fe2O3
VAR[is.na(VAR)] <- otra[is.na(VAR)]
otra <- 0.8998 * DF[["Fe2O3T (wt%)"]]
VAR[is.na(VAR)] <- otra[is.na(VAR)]
mg <- DF[["MgO (wt%)"]] / 40.30                       # moles de MgO (masa molar 40,30)
fe <- VAR / 71.85                                      # moles de FeO (masa molar 71,85)
VAR <- mg / (mg + fe)                                  # número de magnesio, entre 0 y 1
VAR[VAR >= 1] <- NA                                    # sin hierro medido no hay Mg# (la beta exige < 1)"""

CONTINUAS = [
    dict(nombre="inf_04_normal_SiO2", col="SiO2 (wt%)", etiqueta="SiO2", eje="SiO2 (wt%)", unidad="% en peso",
         modelo="normal", tlc=True,
         forma="El histograma es una campana casi simétrica alrededor de 49–50 %: la forma de un modelo normal.",
         pregunta1="¿Cuál es la probabilidad de que un basalto tenga más de 51 % de SiO2 (cerca del límite de 52 % con las rocas intermedias)?",
         titulo_p1="P(SiO2 > 51 %)", q1="51", lado1="mayor",
         pregunta2="Si se analizan 50 basaltos nuevos, ¿cuántos tendrían entre 48 y 50 % de SiO2?", a2="48", b2="50",
         conclusion="Los basaltos tienen una sílice muy constante: el SiO2 los define."),
    dict(nombre="inf_05_lognormal_Zr", col="Zr (ppm)", etiqueta="Zr", eje="Zr (ppm)", unidad="ppm",
         modelo="log-normal", tlc=False,
         forma="El histograma tiene una cola larga hacia la derecha y no baja de cero: la forma típica de los "
               "elementos traza, que se describe con un modelo log-normal (el logaritmo de Zr es normal).",
         pregunta1="¿Cuál es la probabilidad de que un basalto tenga más de 150 ppm de Zr (basaltos enriquecidos, como los de islas oceánicas)?",
         titulo_p1="P(Zr > 150 ppm)", q1="150", lado1="mayor",
         pregunta2="Si se analizan 50 basaltos nuevos, ¿cuántos tendrían entre 50 y 100 ppm de Zr (típico de dorsales)?",
         a2="50", b2="100", conclusion="El circonio se concentra en pocos basaltos enriquecidos y la mayoría tiene valores bajos."),
    dict(nombre="inf_06_exponencial_K2O", col="K2O (wt%)", etiqueta="K2O", eje="K2O (wt%)", unidad="% en peso",
         modelo="exponencial", tlc=False,
         forma="El histograma es máximo cerca de cero y decrece: la mayoría de los basaltos tiene muy poco potasio. "
               "Es la forma del modelo exponencial.",
         pregunta1="¿Cuál es la probabilidad de que un basalto tenga menos de 0,2 % de K2O (basalto de dorsal empobrecido)?",
         titulo_p1="P(K2O < 0,2 %)", q1="0.2", lado1="menor",
         pregunta2="Si se analizan 50 basaltos nuevos, ¿cuántos tendrían entre 0,5 y 1 % de K2O?", a2="0.5", b2="1",
         conclusion="El potasio separa a los basaltos de dorsal (pobres en K2O) de los de arco e intraplaca."),
    dict(nombre="inf_07_beta_Mg", col="Mg#", etiqueta="Mg#", eje="Mg# = Mg/(Mg+Fe)", unidad="(proporción)",
         modelo="beta", tlc=False, calc=MG_NUMERO,
         forma="El número de magnesio (Mg#) es la proporción de magnesio frente a magnesio más hierro: vale entre 0 y 1. "
               "Mide qué tan primitivo es un magma (los magmas recién salidos del manto tienen Mg# cercano a 0,7). Una "
               "variable acotada entre 0 y 1 se describe con el modelo beta, el único de la plantilla para proporciones.",
         pregunta1="¿Cuál es la probabilidad de que un basalto tenga Mg# mayor que 0,65 (magma primitivo, poco evolucionado)?",
         titulo_p1="P(Mg# > 0,65)", q1="0.65", lado1="mayor",
         pregunta2="Si se analizan 50 basaltos nuevos, ¿cuántos tendrían Mg# entre 0,5 y 0,6?", a2="0.5", b2="0.6",
         conclusion="La mayoría de los basaltos ya perdió parte de su magnesio al cristalizar olivino: no son magmas primitivos."),
]


def continua(c):
    m = MODELOS[c["modelo"]]
    calc = c.get("calc", 'VAR <- DF[["' + c["col"] + '"]]')
    c = c | {"calc_muestra": calc.replace("DF", "muestra").replace("VAR", "x"),
             "calc_base": calc.replace("DF", "base").replace("VAR", "poblacion")}
    d = lambda q: m["d"].replace("Q", q)  # noqa: E731
    p = lambda q: m["p"].replace("Q", q)  # noqa: E731
    p1 = p(c["q1"]) if c["lado1"] == "menor" else f"1 - {p(c['q1'])}"
    zona1 = f"xs <= {c['q1']}" if c["lado1"] == "menor" else f"xs >= {c['q1']}"
    c = {k: v for k, v in c.items() if k != "tlc"} | {"tlc": TLC if c["tlc"] else ""}
    cuerpo = CONTINUA.format(
        **c, fit=m["fit"], param=m["param"], d_curva=d("x"), d_grid=d("seq(min(x), max(x), length.out = 400)"), p_Ls=p("Ls"), p_Li=p("Li"), d_xs=d("xs"),
        d_zona=d("zona"), p1=p1, zona1=zona1, p2=f"{p(c['b2'])} - {p(c['a2'])}", param_texto=m["texto"],
        url=URL)
    return (CABECERA.format(titulo=f"Inferencia de {c['etiqueta']} en basaltos: modelo {c['modelo']}", autores=AUTORES, url=URL)
            + cuerpo + GUARDAR.format(nombre=c["nombre"], etiqueta=c["etiqueta"], tipo="continua", modelo=c["modelo"],
                                      parametros=m["parametros"], n_resumen="length(x)",
                                      ic_texto='paste0("[", round(IC[["inferior"]], 2), " ; ", round(IC[["superior"]], 2), "]")',
                                      real="round(media_real, 3)"))


DISCRETA = '''
## 2. Tabla de distribución de cantidad

{explicacion}

```{{r tabla}}
x <- as.character(muestra[["{col}"]])
x <- x[!is.na(x) & x != ""]                            # quita vacíos (en el orden del sorteo)
exito <- x == "{categoria}"                            # TRUE = {exito_texto}
c(casos = length(x), exitos = sum(exito), proporcion = mean(exito))
{construir}
Fo <- as.vector(table(factor(y, levels = 0:max(y))))   # cuántas veces salió 0, 1, 2, ...
hi <- round(Fo / sum(Fo) * 100, 2)
TDF <- data.frame(valor = 0:max(y), ni = Fo, hi)
knitr::kable(TDF, caption = "Tabla N° 1: distribución de {variable_y}")
```

## 3. Gráfica de distribución de cantidad

```{{r grafica, fig.width = 8, fig.height = 4.8}}
barplot(hi, names.arg = 0:max(y), col = "#86b6ef", border = "white", las = 1,
        main = "Gráfica N° 1: {titulo_grafica}", xlab = "{eje}", ylab = "Porcentaje (%)")
```
{lgn}
## 4. Conjetura del modelo

{conjetura}

```{{r conjetura, fig.width = 8, fig.height = 4.8}}
{param}
valores <- 0:max(y)
P <- {p_puntual}                                        # probabilidad de cada valor según el modelo
P[length(P)] <- {p_cola}                                # el último valor acumula la cola ("o más")
Fe <- P * length(y)                                    # frecuencia esperada
# Para el chi-cuadrado cada clase debe esperar al menos 5 casos: los valores altos se juntan en una clase "o más"
corte <- max(which(Fe >= 5))
Fo2 <- c(Fo[1:(corte - 1)], sum(Fo[corte:length(Fo)]))
Fe2 <- c(Fe[1:(corte - 1)], sum(Fe[corte:length(Fe)]))
clase <- c(0:(corte - 2), paste0(corte - 1, " o más"))
knitr::kable(data.frame(clase, Fo = Fo2, Fe = round(Fe2, 2)), caption = "Tabla N° 2: frecuencias observadas y esperadas")
barplot(rbind(Fo2, Fe2), beside = TRUE, names.arg = clase, col = c("#86b6ef", "#d95926"), border = "white", las = 1,
        ylim = c(0, max(Fo2, Fe2) * 1.2),
        main = "Gráfica N° {n_graf_conj}: Datos vs modelo {modelo}", xlab = "{eje}", ylab = "Cantidad")
legend("topright", c("observado (Fo)", "modelo (Fe)"), fill = c("#86b6ef", "#d95926"), bty = "n")
```

## 5. Test de aprobación

```{{r test, fig.width = 6, fig.height = 5}}
lim <- range(0, Fo2 / sum(Fo2) * 100, Fe2 / sum(Fo2) * 100)   # mismos ejes en x e y
plot(Fo2 / sum(Fo2) * 100, Fe2 / sum(Fo2) * 100, pch = 19, col = "#3987e5", las = 1, xlim = lim, ylim = lim,
     main = "Gráfica N° {n_graf_test}: Frecuencia observada vs esperada", xlab = "Observada (%)", ylab = "Esperada (%)")
abline(a = 0, b = 1, col = "#d95926", lwd = 2)

pearson <- cor(Fo2, Fe2) * 100
gl <- length(Fo2) - 1
x2 <- sum((Fo2 - Fe2)^2 / Fe2)
umbral <- qchisq(0.95, gl)
resultado <- ifelse(x2 < umbral, "se acepta el modelo", "se rechaza el modelo")
knitr::kable(data.frame(Variable = "{variable_y}", Pearson = round(pearson, 2), Chi_cuadrado = round(x2, 2),
                        Umbral = round(umbral, 2), Resultado = resultado),
             caption = "Tabla N° 3: pruebas de bondad de ajuste")
```

El chi-cuadrado (`r round(x2, 2)`) es `r ifelse(x2 < umbral, "menor", "mayor")` que el umbral (`r round(umbral, 2)`):
`r resultado`. La correlación entre lo observado y lo esperado es de `r round(pearson, 1)` %.

## 6. Estimación de probabilidades

**{pregunta1}**

```{{r prob1, fig.width = 8, fig.height = 4.5}}
p1 <- {p1}
p1 * 100
vp <- 0:{max_vp}                                       # valores posibles que se dibujan
Pp <- {p_grafica}
barplot(Pp * 100, names.arg = vp, las = 1, border = "white", col = ifelse(vp {marca1}, "#d95926", "gray75"),
        main = "Gráfica N° {n_graf_p}: {titulo_p1}", xlab = "{eje}", ylab = "Probabilidad (%)")
legend("topright", paste0("P = ", round(p1 * 100, 2), " %"), bty = "n", cex = 1.1)
```

**{pregunta2}**

```{{r prob2}}
{p2}
```

## 7. Intervalos de confianza

{ic_texto}

```{{r ic}}
{ic}
```

**Comprobación con la base completa.** La proporción real se conoce: ¿el intervalo la contiene?

```{{r comprobacion}}
if (!file.exists("data/earthchem_limpio.csv.gz")) {{
  download.file("{url}data/earthchem_limpio.csv.gz", "data/earthchem_limpio.csv.gz", mode = "wb")
}}
base <- read.csv(gzfile("data/earthchem_limpio.csv.gz", encoding = "UTF-8"), check.names = FALSE)
todos <- as.character(base[["{col}"]])
todos <- todos[!is.na(todos) & todos != ""]
p_real <- mean(todos == "{categoria}")
c(proporcion_real = p_real, dentro_del_intervalo = p_real >= IC[["inferior"]] & p_real <= IC[["superior"]])
```

## 8. Conclusión

{conclusion} El modelo pasa el test (chi-cuadrado `r round(x2, 2)` < umbral `r round(umbral, 2)`; Pearson
`r round(pearson, 1)` %). Con el 95 % de confianza, la proporción poblacional de {exito_texto} está entre
`r round(IC[["inferior"]] * 100, 2)` % y `r round(IC[["superior"]] * 100, 2)` %, y la proporción real de la base
(`r round(p_real * 100, 2)` %) `r ifelse(p_real >= IC[["inferior"]] & p_real <= IC[["superior"]], "cae dentro", "queda fuera")` del intervalo.
'''

IC_PROPORCION = '''p_m <- mean(exito)                                     # proporción en la muestra
z <- qnorm(0.975)
E <- z * sqrt(p_m * (1 - p_m) / length(exito))         # error máximo de estimación
IC <- c(inferior = p_m - E, proporcion = p_m, superior = p_m + E)
round(IC * 100, 2)                                     # en %'''

LGN = '''
**Probabilidad clásica y ley de los grandes números.** Si se recorre la muestra en el orden del sorteo, la proporción
de éxitos acumulada se acerca a la probabilidad real (la de la base completa) a medida que crece el número de casos.

```{r lgn, fig.width = 8, fig.height = 4.5}
frecuencia <- cumsum(exito) / seq_along(exito)         # proporción acumulada después de cada caso
plot(frecuencia, type = "l", col = "#3987e5", lwd = 2, las = 1, ylim = c(0, 0.6),
     main = "Gráfica N° 2: Ley de los grandes números", xlab = "Número de casos", ylab = "Proporción de éxitos")
abline(h = mean(exito), col = "#d95926", lwd = 2, lty = 2)
legend("topright", c("proporción acumulada", "proporción final de la muestra"), col = c("#3987e5", "#d95926"),
       lty = c(1, 2), lwd = 2, bty = "n")
```
'''

DISCRETAS = [
    dict(nombre="inf_01_binomial_ambiente", col="Tectonic Group", categoria="margen convergente", tipo="nominal",
         titulo="Inferencia de una variable nominal (ambiente tectónico): modelo binomial", modelo="binomial",
         exito_texto="análisis de margen convergente",
         explicacion="Variable **nominal**: ambiente tectónico agrupado. Cada análisis es un ensayo con dos resultados: "
                     "es de **margen convergente** (éxito) o no. La muestra se reparte, en el orden del sorteo, en lotes de "
                     "10 análisis y se cuenta cuántos de margen convergente hay en cada lote: ese conteo (0 a 10) es la "
                     "variable aleatoria X.",
         construir="lote <- 10\nB <- floor(length(exito) / lote)                      # número de lotes\n"
                   "grupo <- rep(1:B, each = lote)                         # a qué lote va cada análisis\n"
                   "y <- as.vector(tapply(exito[1:(B * lote)], grupo, sum))  # éxitos en cada lote",
         variable_y="X = análisis de margen convergente en un lote de 10", titulo_grafica="Margen convergente en lotes de 10 análisis",
         eje="Análisis de margen convergente en el lote", lgn=LGN,
         conjetura="X cuenta éxitos en un número fijo de ensayos independientes (n = 10) con la misma probabilidad p: es "
                   "el **modelo binomial**. p se estima con la proporción de éxitos.",
         param="n_ensayos <- lote\np <- mean(y) / n_ensayos                               # probabilidad de éxito estimada\np",
         p_puntual="dbinom(valores, n_ensayos, p)", max_vp=10, p_cola="1 - pbinom(max(y) - 1, n_ensayos, p)",
         n_graf_conj=3, n_graf_test=4, n_graf_p=5,
         pregunta1="En un lote de 10 análisis tomados al azar, ¿cuál es la probabilidad de que haya 3 o más de margen convergente?",
         p1="1 - pbinom(2, n_ensayos, p)", marca1=">= 3", titulo_p1="P(X ≥ 3) en un lote de 10",
         pregunta2="Si se revisan 50 lotes de 10, ¿en cuántos no habría ningún análisis de margen convergente?",
         p2="p0 <- dbinom(0, n_ensayos, p)\nc(probabilidad = p0 * 100, lotes_esperados_de_50 = p0 * 50)",
         ic_texto="Intervalo de confianza del 95 % para la **proporción poblacional** de análisis de margen convergente, "
                  "con la aproximación normal (n grande): p ± z·√(p(1 − p)/n).",
         ic=IC_PROPORCION, parametros='paste0("n = 10; p = ", round(p, 3))',
         conclusion="El número de análisis de margen convergente en un lote de 10 sigue un **modelo binomial** con "
                    "n = 10 y p = `r round(p, 3)`."),
    dict(nombre="inf_02_geometrica_ultrabasica", col="SiO2 Class", categoria="ultrabasica", tipo="ordinal",
         titulo="Inferencia de una variable ordinal (clase según SiO2): modelo geométrico", modelo="geométrico",
         exito_texto="rocas ultrabásicas",
         explicacion="Variable **ordinal**: clase según SiO2 (ultrabásica < básica < intermedia < ácida). Se recorren los "
                     "análisis en el orden del sorteo y se cuenta cuántos **no** son ultrabásicos antes de encontrar uno "
                     "ultrabásico (el éxito). Ese número de fracasos es la variable aleatoria X.",
         construir="posicion <- which(exito)                               # dónde aparece cada ultrabásica\n"
                   "y <- diff(c(0, posicion)) - 1                          # fracasos antes de cada éxito",
         variable_y="X = análisis antes de la primera roca ultrabásica", titulo_grafica="Análisis revisados antes de una roca ultrabásica",
         eje="Análisis antes de la primera ultrabásica", lgn="",
         conjetura="X cuenta los fracasos antes del primer éxito, en ensayos independientes con la misma probabilidad p: "
                   "es el **modelo geométrico**. p se estima como 1 / (media + 1).",
         param="p <- 1 / (mean(y) + 1)                                 # probabilidad de éxito estimada\np",
         p_puntual="dgeom(valores, p)", max_vp=15, p_cola="1 - pgeom(max(y) - 1, p)",
         n_graf_conj=2, n_graf_test=3, n_graf_p=4,
         pregunta1="¿Cuál es la probabilidad de encontrar la primera roca ultrabásica antes de revisar 5 análisis (X ≤ 4)?",
         p1="pgeom(4, p)", marca1="<= 4", titulo_p1="P(X ≤ 4)",
         pregunta2="En promedio, ¿cuántos análisis hay que revisar para encontrar una roca ultrabásica?",
         p2="c(fracasos_esperados = (1 - p) / p, analisis_a_revisar = 1 / p)",
         ic_texto="Intervalo de confianza del 95 % para la **proporción poblacional** de rocas ultrabásicas (la p del "
                  "modelo), con la aproximación normal: p ± z·√(p(1 − p)/n).",
         ic=IC_PROPORCION, parametros='paste0("p = ", round(p, 3))',
         conclusion="El número de análisis antes de encontrar una roca ultrabásica sigue un **modelo geométrico** con "
                    "p = `r round(p, 3)`: en promedio hay que revisar `r round(1 / p, 1)` análisis."),
    dict(nombre="inf_03_poisson_intermedias", col="Sample Type", categoria="igneous:volcanic:intermediate", tipo="discreta",
         titulo="Inferencia de una variable discreta (conteo de andesitas): modelo de Poisson", modelo="Poisson",
         exito_texto="rocas volcánicas intermedias",
         explicacion="Variable **discreta**: el número de rocas volcánicas intermedias (andesitas) en un lote de 30 "
                     "análisis. Es un conteo de un evento poco frecuente (cerca del 6 % de los análisis). Antes se probó "
                     "con N Analytes (número de analitos) y **no sirvió**: su varianza (122) es once veces su media (10,8) "
                     "y el modelo de Poisson exige que sean iguales; el chi-cuadrado salió miles de veces mayor que el umbral.",
         construir="lote <- 30\nB <- floor(length(exito) / lote)\n"
                   "grupo <- rep(1:B, each = lote)\n"
                   "y <- as.vector(tapply(exito[1:(B * lote)], grupo, sum))  # andesitas en cada lote de 30\n"
                   "c(media = mean(y), varianza = var(y))                  # en Poisson deben ser parecidas",
         variable_y="X = rocas intermedias en un lote de 30", titulo_grafica="Rocas volcánicas intermedias en lotes de 30 análisis",
         eje="Rocas intermedias en el lote", lgn="",
         conjetura="X cuenta un evento raro en un lote grande y su media y varianza son parecidas: es el **modelo de "
                   "Poisson**. λ se estima con la media.",
         param="lambda <- mean(y)                                     # promedio de andesitas por lote\nlambda",
         p_puntual="dpois(valores, lambda)", max_vp=8, p_cola="1 - ppois(max(y) - 1, lambda)",
         n_graf_conj=2, n_graf_test=3, n_graf_p=4,
         pregunta1="En un lote de 30 análisis, ¿cuál es la probabilidad de que no haya ninguna roca intermedia?",
         p1="dpois(0, lambda)", marca1="== 0", titulo_p1="P(X = 0) en un lote de 30",
         pregunta2="En 50 lotes de 30 análisis, ¿en cuántos habría 3 o más rocas intermedias?",
         p2="p3 <- 1 - ppois(2, lambda)\nc(probabilidad = p3 * 100, lotes_esperados_de_50 = p3 * 50)",
         ic_texto="Intervalo de confianza del 95 % para la **proporción poblacional** de rocas intermedias "
                  "(λ / 30), con la aproximación normal.",
         ic=IC_PROPORCION, parametros='paste0("lambda = ", round(lambda, 3))',
         conclusion="El número de rocas volcánicas intermedias en un lote de 30 análisis sigue un **modelo de Poisson** "
                    "con λ = `r round(lambda, 2)`."),
]


def discreta(c):
    cuerpo = DISCRETA.format(**c, url=URL, p_grafica=c["p_puntual"].replace("valores", "vp"))
    return (CABECERA.format(titulo=c["titulo"], autores=AUTORES, url=URL) + cuerpo
            + GUARDAR.format(nombre=c["nombre"], etiqueta=c["variable_y"], tipo=c["tipo"], modelo=c["modelo"],
                             parametros=c["parametros"], n_resumen="length(y)",
                             ic_texto='paste0("[", round(IC[["inferior"]] * 100, 2), " % ; ", round(IC[["superior"]] * 100, 2), " %]")',
                             real="round(p_real * 100, 2)"))


def main():
    for d in (RMD, HTML, IMG, RESUMEN):
        d.mkdir(parents=True, exist_ok=True)
    docs = {c["nombre"]: discreta(c) for c in DISCRETAS} | {c["nombre"]: continua(c) for c in CONTINUAS}
    for nombre, texto in docs.items():
        (RMD / f"{nombre}.Rmd").write_text(texto, encoding="utf-8")
    solo = sys.argv[1:] or list(docs)
    # clean = FALSE deja las figuras en docs/rpubs/<nombre>_files/: se copian a docs/img/inferencial/
    codigo = ("for (f in commandArgs(TRUE)) rmarkdown::render(file.path('R/inferencial', paste0(f, '.Rmd')), "
              "output_dir = 'docs/rpubs', knit_root_dir = getwd(), quiet = TRUE, envir = new.env(), clean = FALSE)")
    script = RMD / "_render.R"
    script.write_text(codigo, encoding="utf-8")
    try:
        subprocess.run([RSCRIPT, str(script), *solo], cwd=RAIZ, check=True)
    finally:
        script.unlink()
    for nombre in solo:
        figuras = HTML / f"{nombre}_files" / "figure-html"
        for png in figuras.glob("*.png"):
            shutil.copy(png, IMG / f"{nombre}-{png.name.replace('-1.png', '.png')}")
        shutil.rmtree(HTML / f"{nombre}_files", ignore_errors=True)
        for resto in [*RMD.glob(f"{nombre}.*"), *HTML.glob(f"{nombre}.*")]:
            if resto.suffix not in (".Rmd", ".html"):
                resto.unlink()
    filas = []
    for archivo in sorted(RESUMEN.glob("*.csv")):
        filas += list(csv.DictReader(archivo.read_text(encoding="utf-8").splitlines()))
    (RAIZ / "docs" / "data" / "inferencial.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(solo)} documentos -> {HTML}; figuras -> {IMG}")


if __name__ == "__main__":
    main()
