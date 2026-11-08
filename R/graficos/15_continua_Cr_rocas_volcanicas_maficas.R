# =========================================================================================
# GRÁFICO: log10 Cr en rocas volcánicas máficas   (Cr_estrato_mafico.png)
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
x <- base[["Cr (ppm)"]]
tipo <- base[["Sample Type"]]                        # tipo de roca de cada fila
tiene <- !is.na(x)                                     # filas con dato
x <- x[tiene]
tipo <- tipo[tiene]
x <- log10(x)                                          # escala log10: 10, 100, 1000 ppm -> 1, 2, 3
x <- x[tipo == "igneous:volcanic:mafic"]          # solo rocas volcánicas máficas
n <- length(x)

# ---- 2. Límites de outliers (regla intercuartílica) ----
Q1 <- quantile(x, 0.25, names = FALSE)
Q3 <- quantile(x, 0.75, names = FALSE)
IR <- Q3 - Q1                                          # rango intercuartílico
lim_inf <- Q1 - 1.5 * IR                               # menos que esto = outlier bajo
lim_sup <- Q3 + 1.5 * IR                               # más que esto = outlier alto
tipico <- x[x >= lim_inf & x <= lim_sup]               # los intervalos se arman con estos datos
# Los outliers NO se borran: se cuentan en las clases abiertas (son otras rocas, no errores).

# ---- 3. Intervalos (regla de Sturges) ----
k <- round(1 + 3.3 * log10(n))                         # número de intervalos
a <- (max(tipico) - min(tipico)) / k                   # amplitud calculada
a <- 0.2                                               # se redondea hacia arriba a un número cómodo
desde <- floor(min(tipico) / a) * a                    # primer límite: múltiplo de a
k <- floor((max(tipico) - desde) / a) + 1              # intervalos que hacen falta para llegar al máximo
Li <- desde + (0:(k - 1)) * a                          # límites inferiores
Ls <- Li + a                                           # límites superiores
MC <- (Li + Ls) / 2                                    # marca de clase

# ---- 4. Frecuencias ----
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

# ---- 5. Gráficos: histograma + polígono, ojiva y caja ----
etiq <- paste0("[", Li, "-", Ls, "[")                  # texto de cada intervalo
nota <- c(if (abajo > 0) paste0("< ", Li[1], ": ", abajo, " (", round(abajo / n * 100, 2), " %)"),
          if (arriba > 0) paste0("≥ ", Ls[k], ": ", arriba, " (", round(arriba / n * 100, 2), " %)"))
png("docs/img/r/Cr_estrato_mafico.png", width = 1800, height = 1200, res = 130)    # abre la imagen
layout(matrix(c(1, 1, 2, 3), 2, 2, byrow = TRUE), heights = c(1.15, 1))   # arriba 1 gráfico, abajo 2
par(mar = c(8, 5, 4, 1))
h <- barplot(hi, names.arg = etiq, space = 0, las = 2, col = "#3987e5", border = "white",   # histograma
             ylab = "Porcentaje (%)", cex.names = .75, ylim = c(0, max(hi) * 1.15),
             main = "Gráfica No. 16: Histograma y polígono de frecuencias de log10 Cr en rocas volcánicas máficas (ppm)")
lines(c(h[1] - 1, h, h[length(h)] + 1), c(0, hi, 0), col = "#d95926", lwd = 2, type = "b", pch = 16, cex = .6)  # polígono
mtext(if (length(nota) > 0) paste0("Clases abiertas (fuera del gráfico): ", paste(nota, collapse = " · ")) else "",
      side = 1, line = 6.5, cex = .7, col = "gray30")  # nota bajo el histograma
par(mar = c(5, 5, 4, 1))
plot(Ls, Hi_asc, type = "b", pch = 16, col = "#3987e5", ylim = c(0, 100),            # ojiva ascendente
     xlab = "log10 Cr en rocas volcánicas máficas (ppm)", ylab = "Porcentaje acumulado (%)",
     main = "Gráfica No. 17: Ojiva ascendente y descendente")
lines(Li, Hi_dsc, type = "b", pch = 17, col = "#d95926")                              # ojiva descendente
abline(h = 50, lty = 3, col = "gray50")                # línea del 50 %: donde se cruzan está la mediana
legend("right", c("ascendente (≤)", "descendente (≥)"), col = c("#3987e5", "#d95926"), pch = c(16, 17), bty = "n", cex = .85)
boxplot(x, horizontal = TRUE, col = "#86b6ef", xlab = "log10 Cr en rocas volcánicas máficas (ppm)",       # diagrama de caja
        main = "Gráfica No. 18: Diagrama de caja (todos los datos)")
dev.off()                                              # cierra y guarda la imagen

# ---- 6. Error de agrupación: media y desviación con la TDF vs con los datos ----
xc <- x[x >= Li[1] & x <= Ls[k]]                       # los datos de los intervalos normales
media_agrupada <- sum(MC * ni) / sum(ni)               # cada dato = la marca de clase de su intervalo
desv_agrupada <- sqrt(sum((MC - media_agrupada)^2 * ni) / sum(ni))
c(error_media = abs(media_agrupada - mean(xc)) / mean(xc) * 100,   # en %; menos de 5 % = bien
  error_desviacion = abs(desv_agrupada - sd(xc)) / sd(xc) * 100)

# ---- 7. Indicadores (con los datos sin agrupar, en log10) ----
library(e1071)                                         # para asimetría y curtosis (install.packages("e1071"))
c(n = n, media = mean(x), mediana = median(x), desviacion = sd(x), varianza = var(x),
  CV = sd(x) / mean(x) * 100, asimetria = skewness(x), curtosis = kurtosis(x))

# Abre la imagen que se acaba de crear (solo en RStudio)
if (interactive()) browseURL(file.path(getwd(), "docs/img/r/Cr_estrato_mafico.png"))
