# =====================================================================================================
# CÓDIGO PASO A PASO, CON EL ESTILO DE LA PLANTILLA DEL CURSO (Analisis_SiO2.R)
# =====================================================================================================
# Este script hace lo mismo que 01_cualitativas.R y 03_continuas.R para DOS variables, pero sin funciones
# propias: cada cálculo está escrito línea por línea, como en la plantilla del docente, y explicado.
# Al final comprueba que los resultados son idénticos a los del código con funciones.
#
# Cómo usarlo en RStudio:
#   1. File > Open Project... o Session > Set Working Directory: la carpeta del repositorio
#      (la que contiene las carpetas R/, data/, docs/).
#   2. Abrir este archivo y ejecutar línea por línea con Ctrl + Enter. Cada resultado aparece en la consola
#      y cada gráfico en el panel Plots.
#
# Recordatorio de R:
#   x <- 5            guarda el valor 5 con el nombre x (se lee "x recibe 5").
#   c(2, 30, 81)      crea un VECTOR: una lista de valores del mismo tipo.
#   base$columna      o base[["columna"]]: saca una columna de una tabla (data.frame) como vector.
#   nombre(...)       ejecuta una FUNCIÓN: un bloque de código con nombre que recibe datos entre paréntesis
#                     (argumentos) y devuelve un resultado. Ej.: mean(c(2, 4)) devuelve 3.
#   # texto           comentario: R lo ignora; sirve para explicar.
# =====================================================================================================

library(e1071)  # paquete con skewness() (asimetría) y kurtosis() (curtosis)

# -----------------------------------------------------------------------------------------------------
# 0. LEER LOS DATOS
# -----------------------------------------------------------------------------------------------------
# La plantilla usa read.csv(file = "Muestra.csv"). Nuestra base está comprimida (.gz): gzfile() la abre.
# check.names = FALSE conserva los nombres originales de las columnas, como "SiO2 (wt%)".
base <- read.csv(gzfile("data/earthchem_limpio.csv.gz", encoding = "UTF-8"), check.names = FALSE)
dim(base)   # filas y columnas: 159760 y 75

# Si no se está en RStudio (por ejemplo con Rscript), los gráficos se guardan como PNG en R/salidas/.
if (!interactive()) png("R/salidas/paso_a_paso_%d.png", width = 1400, height = 900, res = 130)

# =====================================================================================================
# PARTE A. VARIABLE CUALITATIVA NOMINAL: AMBIENTE TECTÓNICO AGRUPADO
# =====================================================================================================
grupo <- base[["Tectonic Group"]]   # vector con 159760 textos
grupo <- grupo[grupo != ""]         # se quitan las celdas vacías ("" = sin dato)
length(grupo)                       # n = 159456 análisis con dato

# table() cuenta cuántas veces aparece cada categoría; sort(decreasing = TRUE) las ordena de mayor a menor.
conteo <- sort(table(grupo), decreasing = TRUE)
conteo

categoria <- names(conteo)                 # los nombres de las categorías
ni <- as.vector(conteo)                    # frecuencia absoluta (as.vector quita los nombres)
hi <- round((ni / sum(ni)) * 100, 2)       # frecuencia relativa en %, con 2 decimales
TDF_grupo <- data.frame(categoria, ni, hi) # se juntan los vectores como columnas de una tabla
TDF_grupo
# En una variable NOMINAL no se calculan acumuladas (Ni, Hi): las categorías no tienen orden.

# Diagrama de barras: una barra por categoría, de altura ni.
barplot(ni, names.arg = categoria, col = "gray60", main = "Ambiente tectónico agrupado",
        ylab = "Cantidad", cex.names = 0.8)
# Diagrama circular: cada porción proporcional a hi.
pie(hi, labels = paste0(categoria, " ", hi, "%"), main = "Ambiente tectónico agrupado (%)")

moda <- categoria[which.max(ni)]   # which.max() da la posición del ni más grande
moda                                # "dorsal y corteza oceanica"

# =====================================================================================================
# PARTE B. VARIABLE CUANTITATIVA CONTINUA: SiO2 (wt%)
# =====================================================================================================
SiO2 <- base[["SiO2 (wt%)"]]   # la plantilla hace: SiO2 <- as.numeric(datos[, 16])
SiO2 <- na.omit(SiO2)          # quita los NA (análisis donde no se midió SiO2), igual que la plantilla
n <- length(SiO2)
n                              # 57031

# ---- Paso 1: ¿cuántos intervalos? (regla de Sturges) -----------------------------------------------
k <- round(1 + 3.3 * log10(n))
k                              # 17

# ---- Paso 2: límites de outliers con la regla intercuartílica ----------------------------------------
# Valores fuera de [Q1 - 1,5·IR ; Q3 + 1,5·IR] son outliers. En esta base NO son errores: son otras rocas
# (peridotitas, granitos...). Por eso no se borran: se cuentan en dos clases abiertas.
Q1 <- quantile(SiO2, 0.25, names = FALSE)
Q3 <- quantile(SiO2, 0.75, names = FALSE)
IR <- Q3 - Q1
lim_inf <- Q1 - 1.5 * IR
lim_sup <- Q3 + 1.5 * IR
c(lim_inf, lim_sup)            # 36,3 y 65,4 wt%

# ---- Paso 3: amplitud e intervalos -----------------------------------------------------------------
# Amplitud = rango típico / k. Sale 1,71; se redondea hacia arriba a un valor "redondo" (2) para que los
# intervalos se lean fácil: [36-38[ en vez de [36,13-37,85[.
SiO2_tipico <- SiO2[SiO2 >= lim_inf & SiO2 <= lim_sup]   # & significa "y"
a_calculada <- (max(SiO2_tipico) - min(SiO2_tipico)) / k
a_calculada                    # 1,71
a <- 2
# Primer límite: el múltiplo de 2 justo por debajo del mínimo típico. floor() redondea hacia abajo.
desde <- floor(min(SiO2_tipico) / a) * a     # 36
hasta <- floor(max(SiO2_tipico) / a) * a     # 64: último límite inferior
Li <- seq(from = desde, to = hasta, by = a)  # 36, 38, 40, ..., 64   (como en la plantilla)
Ls <- Li + a                                  # 38, 40, 42, ..., 66
MC <- (Li + Ls) / 2                           # marca de clase

# ---- Paso 4: frecuencias -------------------------------------------------------------------------
# La plantilla escribe ni a mano (ni <- c(2, 30, 81, ...)). Aquí R cuenta: cut() asigna cada dato a su
# intervalo [Li, Ls[ (right = FALSE: incluye el límite de abajo, no el de arriba) y table() los cuenta.
# include.lowest = TRUE cierra también el último intervalo por arriba: un 66,0 exacto cuenta en [64-66].
dentro <- SiO2[SiO2 >= desde & SiO2 <= max(Ls)]
ni <- as.vector(table(cut(dentro, breaks = c(Li, max(Ls)), right = FALSE, include.lowest = TRUE)))
# Clases abiertas: lo que queda por debajo del primer Li y por encima del último Ls.
ni_abajo <- sum(SiO2 < desde)        # "< 36"
ni_arriba <- sum(SiO2 > max(Ls))     # "≥ 66" (en la práctica, mayores que 66)
c(ni_abajo, sum(ni), ni_arriba, n)   # las tres partes suman n: no se pierde ningún dato

# Tabla completa: clase abierta de abajo + intervalos + clase abierta de arriba.
Li_t <- c(-Inf, Li, max(Ls));  Ls_t <- c(desde, Ls, Inf)
MC_t <- c(NA, MC, NA)                # las clases abiertas no tienen marca de clase
ni_t <- c(ni_abajo, ni, ni_arriba)
hi_t <- round((ni_t / n) * 100, 2)

Niasc <- cumsum(ni_t)                # acumulada ascendente: se suma de arriba hacia abajo
Nidsc <- rev(cumsum(rev(ni_t)))      # descendente: rev() invierte, se acumula y se vuelve a invertir
Hiasc <- round(cumsum(ni_t) / n * 100, 2)
Hidsc <- round(rev(cumsum(rev(ni_t))) / n * 100, 2)

TDF_SiO2 <- data.frame(Li = Li_t, Ls = Ls_t, MC = MC_t, ni = ni_t, hi = hi_t, Niasc, Nidsc, Hiasc, Hidsc)
TDF_SiO2

# ---- Paso 5: histograma y polígono de frecuencias (solo clases cerradas) --------------------------
Intervalos <- paste0("[", Li, "-", Ls, "[")   # textos "[36-38[", "[38-40[", ...
hi_cerradas <- hi_t[2:(length(hi_t) - 1)]     # se dejan fuera la primera y la última fila (abiertas)
Histograma <- barplot(hi_cerradas, names.arg = Intervalos, space = 0, las = 2,
                      main = "Histograma de SiO2", xlab = "SiO2 (wt%)", ylab = "Porcentaje %",
                      col = "#3987e5", ylim = c(0, 25))
# barplot() devuelve la posición del centro de cada barra: con eso se dibuja el polígono encima.
x <- c(Histograma[1] - 1, Histograma, Histograma[length(Histograma)] + 1)
y <- c(0, hi_cerradas, 0)
lines(x, y, col = "red", type = "b", pch = 16)

# ---- Paso 6: ojiva ascendente y descendente --------------------------------------------------------
Hiasc_c <- Hiasc[2:(length(Hiasc) - 1)];  Hidsc_c <- Hidsc[2:(length(Hidsc) - 1)]
plot(Ls, Hiasc_c, type = "b", col = "#3987e5", ylim = c(0, 100),
     main = "Ojiva ascendente y descendente de SiO2", xlab = "SiO2 (wt%)", ylab = "Porcentaje acumulado %")
lines(Li, Hidsc_c, type = "b", col = "red")
abline(h = 50, lty = 3)   # las dos ojivas se cruzan cerca del 50 %: ahí está la mediana

# ---- Paso 7: diagrama de caja e indicadores -------------------------------------------------------
caja <- boxplot(SiO2, horizontal = TRUE, main = "Diagrama de caja de SiO2", xlab = "SiO2 (wt%)")
length(caja$out)          # cuántos puntos dibuja como outliers

quantile(SiO2)            # mínimo, Q1, mediana, Q3, máximo
media <- mean(SiO2)
s <- sd(SiO2)             # desviación estándar
CV <- round((s / media) * 100, 2)   # coeficiente de variación, en % (como en la plantilla)
c(media = media, mediana = median(SiO2), s = s, varianza = var(SiO2), CV = CV,
  asimetria = skewness(SiO2), curtosis = kurtosis(SiO2))
# La plantilla usa EDA() del paquete PASWR, que da estos mismos indicadores en un solo resumen.

if (!interactive()) invisible(dev.off())

# =====================================================================================================
# COMPROBACIÓN: ¿da lo mismo que el código con funciones (funciones.R)?
# =====================================================================================================
# Se cargan las funciones y se calcula la misma TDF. stopifnot() detiene el script con error si algo
# no coincide; si no dice nada, todo es idéntico.
source("R/funciones.R")
tdf_funcion <- tdf_continua(SiO2, lim = c(lim_inf, lim_sup))
stopifnot(identical(tdf_funcion$ni, TDF_SiO2$ni), identical(tdf_funcion$Hi_asc, TDF_SiO2$Hiasc))
tdf_cual <- tdf_cualitativa(base[["Tectonic Group"]])
stopifnot(identical(tdf_cual$ni, TDF_grupo$ni), identical(tdf_cual$hi, TDF_grupo$hi))
cat("Comprobado: el paso a paso y las funciones dan exactamente las mismas tablas.\n")
