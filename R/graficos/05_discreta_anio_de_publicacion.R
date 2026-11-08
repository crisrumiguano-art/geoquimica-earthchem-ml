# =========================================================================================
# GRÁFICO: Año de publicación   (disc_anio.png)
# Código simple, paso a paso. Copiar todo en RStudio y ejecutar (Ctrl + A, Ctrl + Enter).
# Antes: Session > Set Working Directory > la carpeta donde se quiere trabajar.
# Las líneas con # son explicaciones (R no las ejecuta).
# =========================================================================================

# ---- 0. Leer la base de datos (la primera vez la descarga, 26 MB) ----
if (!file.exists("data/earthchem_limpio.csv.gz")) {
  dir.create("data", showWarnings = FALSE)
  download.file("https://github.com/crisrumiguano-art/geoquimica-earthchem-ml/raw/main/data/earthchem_limpio.csv.gz", "data/earthchem_limpio.csv.gz", mode = "wb")
}
base <- read.csv(gzfile("data/earthchem_limpio.csv.gz", encoding = "UTF-8"), check.names = FALSE)
dir.create("docs/img/r", recursive = TRUE, showWarnings = FALSE)   # carpeta donde se guarda el gráfico

# ---- 1. Datos ----
x <- base[["Publication Year"]]
x <- x[!is.na(x)]                                      # quita vacíos
n <- length(x)
tipico <- x                                            # aquí se agrupan todos los datos

# ---- 2. Intervalos (regla de Sturges) ----
k <- round(1 + 3.3 * log10(n))                         # número de intervalos
a <- (max(tipico) - min(tipico)) / k                   # amplitud calculada
a <- 10                                               # se redondea hacia arriba a un número cómodo
desde <- floor(min(tipico) / a) * a                    # primer límite: múltiplo de a
k <- floor((max(tipico) - desde) / a) + 1              # intervalos que hacen falta para llegar al máximo
Li <- desde + (0:(k - 1)) * a                          # límites inferiores
Ls <- Li + a                                           # límites superiores
MC <- (Li + Ls) / 2                                    # marca de clase

# ---- 3. Frecuencias ----
dentro <- x[x >= Li[1] & x <= Ls[k]]
ni <- as.vector(table(cut(dentro, breaks = c(Li, Ls[k]), right = FALSE, include.lowest = TRUE)))  # cuenta por intervalo [Li, Ls[
abajo <- sum(x < Li[1])                                # clase abierta "menor que" (outliers bajos)
arriba <- sum(x > Ls[k])                               # clase abierta "mayor o igual" (outliers altos)
hi <- round(ni / n * 100, 2)                           # frecuencia relativa (%)
todos <- c(abajo, ni, arriba)                          # con las clases abiertas, para acumular
cerradas <- 2:(k + 1)                                  # posiciones de los intervalos normales
Ni_asc <- cumsum(todos)[cerradas]                      # acumulada ascendente
Ni_dsc <- rev(cumsum(rev(todos)))[cerradas]            # acumulada descendente
Hi_asc <- round(cumsum(todos) / n * 100, 2)[cerradas]
Hi_dsc <- round(rev(cumsum(rev(todos))) / n * 100, 2)[cerradas]
TDF <- data.frame(Li, Ls, MC, ni, hi, Ni_asc, Ni_dsc, Hi_asc, Hi_dsc)
TDF                                                    # la tabla
c(abajo = abajo, arriba = arriba)                      # datos en las clases abiertas (no se borra ninguno)

# ---- 4. Gráficos: histograma + polígono, ojiva y caja ----
etiq <- paste0("[", Li, "-", Ls, "[")                  # texto de cada intervalo
nota <- c(if (abajo > 0) paste0("< ", Li[1], ": ", abajo, " (", round(abajo / n * 100, 2), " %)"),
          if (arriba > 0) paste0("≥ ", Ls[k], ": ", arriba, " (", round(arriba / n * 100, 2), " %)"))
png("docs/img/r/disc_anio.png", width = 1800, height = 1200, res = 130)    # abre la imagen
layout(matrix(c(1, 1, 2, 3), 2, 2, byrow = TRUE), heights = c(1.15, 1))   # arriba 1 gráfico, abajo 2
par(mar = c(8, 5, 4, 1))
h <- barplot(hi, names.arg = etiq, space = 0, las = 2, col = "#3987e5", border = "white",   # histograma
             ylab = "Porcentaje (%)", cex.names = .75, ylim = c(0, max(hi) * 1.15),
             main = "Gráfica No. 1: Histograma y polígono de frecuencias de Año de publicación (año)")
lines(c(h[1] - 1, h, h[length(h)] + 1), c(0, hi, 0), col = "#d95926", lwd = 2, type = "b", pch = 16, cex = .6)  # polígono
mtext(if (length(nota) > 0) paste0("Clases abiertas (fuera del gráfico): ", paste(nota, collapse = " · ")) else "",
      side = 1, line = 6.5, cex = .7, col = "gray30")  # nota bajo el histograma
par(mar = c(5, 5, 4, 1))
plot(Ls, Hi_asc, type = "b", pch = 16, col = "#3987e5", ylim = c(0, 100),            # ojiva ascendente
     xlab = "Año de publicación (año)", ylab = "Porcentaje acumulado (%)",
     main = "Gráfica No. 2: Ojiva ascendente y descendente")
lines(Li, Hi_dsc, type = "b", pch = 17, col = "#d95926")                              # ojiva descendente
abline(h = 50, lty = 3, col = "gray50")                # línea del 50 %: donde se cruzan está la mediana
legend("right", c("ascendente (≤)", "descendente (≥)"), col = c("#3987e5", "#d95926"), pch = c(16, 17), bty = "n", cex = .85)
boxplot(x, horizontal = TRUE, col = "#86b6ef", xlab = "Año de publicación (año)",       # diagrama de caja
        main = "Gráfica No. 3: Diagrama de caja (todos los datos)")
dev.off()                                              # cierra y guarda la imagen

# ---- 5. Indicadores (con los datos sin agrupar) ----
library(e1071)                                         # para asimetría y curtosis (install.packages("e1071"))
c(n = n, media = mean(x), mediana = median(x), desviacion = sd(x), varianza = var(x),
  CV = sd(x) / mean(x) * 100, asimetria = skewness(x), curtosis = kurtosis(x))
as.numeric(names(which.max(table(x))))                # moda: el valor que más se repite

# Abre la imagen que se acaba de crear (solo en RStudio)
if (interactive()) browseURL(file.path(getwd(), "docs/img/r/disc_anio.png"))
