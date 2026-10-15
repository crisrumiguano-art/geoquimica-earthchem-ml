# Funciones de estadística descriptiva (Unidad 1) para la base EarthChem PetDB.
# Siguen la estructura de las plantillas del curso: TDF con Li, Ls, MC, ni, hi, Ni y Hi ascendentes y
# descendentes; histograma con barplot(space = 0), polígono, ojiva y diagrama de caja.
# Se cargan con source("R/funciones.R") desde la raíz del repositorio.

.libPaths(c(Sys.getenv("R_LIBS_USER"), .libPaths()))
library(e1071)     # skewness() y kurtosis(), como en las plantillas
library(openxlsx)  # exportar las TDF a Excel

SALIDAS <- "R/salidas"     # Excel con todas las tablas
GRAFICOS <- "docs/img/r"   # PNG: van directo a la web
TABLAS_WEB <- "docs/data/tdf"
for (d in c(SALIDAS, GRAFICOS, TABLAS_WEB)) dir.create(d, showWarnings = FALSE, recursive = TRUE)

tabla_web <- function(tabla, nombre) {
  # CSV que la página /descriptiva/ muestra como tabla.
  write.csv(tabla, file.path(TABLAS_WEB, paste0(nombre, ".csv")), row.names = FALSE, fileEncoding = "UTF-8")
}

leer_base <- function(ruta = "data/earthchem_limpio.csv.gz") {
  # gzfile() con encoding explícito: read.csv directo sobre el .gz se cae en Windows con R 4.6.
  read.csv(gzfile(ruta, encoding = "UTF-8"), check.names = FALSE)
}

# ---------------------------------------------------------------- variables cualitativas

tdf_cualitativa <- function(x, orden = NULL) {
  # Nominal: ni y hi. Ordinal (se pasa 'orden'): además Ni y Hi acumuladas, que sí tienen sentido.
  x <- x[!is.na(x) & x != ""]
  f <- if (is.null(orden)) sort(table(x), decreasing = TRUE) else table(factor(x, levels = orden))
  tdf <- data.frame(categoria = names(f), ni = as.vector(f))
  tdf$hi <- round(tdf$ni / sum(tdf$ni) * 100, 2)
  if (!is.null(orden)) {
    tdf$Ni_asc <- cumsum(tdf$ni)
    tdf$Hi_asc <- round(cumsum(tdf$ni) / sum(tdf$ni) * 100, 2)
  }
  tdf
}

graficos_cualitativa <- function(tdf, titulo, archivo, n_graf = 1) {
  png(file.path(GRAFICOS, archivo), width = 1600, height = 700, res = 130)
  par(mfrow = c(1, 2), mar = c(9, 5, 4, 1))
  colores <- gray.colors(nrow(tdf), start = .25, end = .85)
  barplot(tdf$ni, names.arg = tdf$categoria, las = 2, col = colores, ylab = "Cantidad",
          main = paste0("Gráfica No. ", n_graf, ": ", titulo), cex.names = .8, cex.main = .9)
  par(mar = c(1, 1, 4, 1))
  pie(tdf$hi, labels = paste0(tdf$hi, "%"), col = colores, clockwise = TRUE, cex = .75,
      main = paste0("Gráfica No. ", n_graf + 1, ": ", titulo, " (%)"), cex.main = .9)
  legend("topright", legend = tdf$categoria, fill = colores, cex = .6, bty = "n")
  dev.off()
}

# ---------------------------------------------------------------- variables continuas y discretas

reglas_k <- function(n) {
  # Reglas del curso para el número de intervalos (Lección 5).
  data.frame(regla = c("Sturges: 1 + 3,3 log n", "raíz de n", "2 · raíz de n"),
             k = c(round(1 + 3.3 * log10(n)), round(sqrt(n)), round(2 * sqrt(n))))
}

amplitud_redonda <- function(a) {
  # Lleva la amplitud a un valor "redondo" (1, 2, 2,5 o 5 por una potencia de 10) igual o mayor:
  # intervalos como [45-50[ son legibles; [44,317-50,108[ no.
  p <- 10^floor(log10(a))
  for (m in c(1, 2, 2.5, 5, 10)) if (m * p >= a - 1e-12) return(m * p)
}

limites_iqr <- function(x) {
  # Regla intercuartílica (Lección 6): outlier si x < Q1 - 1,5·IR o x > Q3 + 1,5·IR.
  q <- quantile(x, c(.25, .75), names = FALSE)
  ir <- q[2] - q[1]
  c(inferior = q[1] - 1.5 * ir, superior = q[2] + 1.5 * ir)
}

tdf_continua <- function(x, k = NULL, a = NULL, desde = NULL, redondear = TRUE, lim = NULL) {
  # Sin argumentos reproduce la plantilla: k por Sturges y a = R / k desde el mínimo.
  # redondear = TRUE: amplitud y primer límite redondos (intervalos legibles).
  # lim = c(inferior, superior): los intervalos cerrados cubren solo ese recorrido (p. ej. los límites
  #   IQR) y lo que queda fuera va a dos clases abiertas, "< Li" y ">= Ls". No se descarta ningún dato.
  x <- x[!is.na(x)]
  n <- length(x)
  if (is.null(k)) k <- round(1 + 3.3 * log10(n))
  xc <- if (is.null(lim)) x else x[x >= lim[1] & x <= lim[2]]
  if (is.null(a)) a <- (max(xc) - min(xc)) / k
  if (redondear) a <- amplitud_redonda(a)
  if (is.null(desde)) desde <- if (redondear) floor(min(xc) / a) * a else min(xc)
  # Con límites redondos, k es lo que haga falta para cubrir hasta el máximo (puede ser k ± 1).
  # Sin redondear se conserva k: el máximo cae en el último intervalo, cerrado por include.lowest.
  if (redondear) k <- floor((max(xc) - desde) / a) + 1
  Li <- desde + (0:(k - 1)) * a
  Ls <- Li + a
  dentro <- x >= Li[1] & x <= Ls[k]
  ni <- as.vector(table(cut(x[dentro], breaks = c(Li, Ls[k]), right = FALSE, include.lowest = TRUE)))
  bajo <- sum(x < Li[1]); alto <- sum(x > Ls[k])
  if (bajo > 0) { Li <- c(-Inf, Li); Ls <- c(Li[2], Ls); ni <- c(bajo, ni) }
  if (alto > 0) { Li <- c(Li, Ls[length(Ls)]); Ls <- c(Ls, Inf); ni <- c(ni, alto) }
  MC <- ifelse(is.finite(Li) & is.finite(Ls), (Li + Ls) / 2, NA)
  data.frame(Li = Li, Ls = Ls, MC = MC, ni = ni, hi = round(ni / n * 100, 2),
             Ni_asc = cumsum(ni), Ni_dsc = rev(cumsum(rev(ni))),
             Hi_asc = round(cumsum(ni) / n * 100, 2), Hi_dsc = round(rev(cumsum(rev(ni))) / n * 100, 2))
}

etiquetas <- function(tdf, dec = 2) {
  f <- function(v) trimws(formatC(round(v, dec), format = "fg", digits = 6, big.mark = ""))
  ifelse(is.infinite(tdf$Li), paste0("< ", f(tdf$Ls)),
         ifelse(is.infinite(tdf$Ls), paste0("≥ ", f(tdf$Li)), paste0("[", f(tdf$Li), "-", f(tdf$Ls), "[")))
}

indicadores <- function(x) {
  x <- x[!is.na(x)]
  q <- quantile(x, c(.25, .5, .75), names = FALSE)
  s <- sd(x); m <- mean(x)
  data.frame(
    indicador = c("n", "Mínimo", "Q1", "Mediana", "Q3", "Máximo", "Media", "Rango intercuartílico",
                  "Varianza", "Desviación estándar", "Coeficiente de variación (%)", "Asimetría", "Curtosis"),
    valor = c(length(x), min(x), q[1], q[2], q[3], max(x), m, q[3] - q[1], var(x), s, s / m * 100,
              skewness(x), kurtosis(x)))
}

error_agrupacion <- function(x, tdf) {
  # Lección 6: media y desviación con datos agrupados frente a datos totales.
  # Solo clases cerradas (las abiertas no tienen marca de clase).
  t <- tdf[!is.na(tdf$MC), ]
  x <- x[!is.na(x) & x >= min(t$Li) & x <= max(t$Ls)]
  xag <- sum(t$MC * t$ni) / sum(t$ni)
  sag <- sqrt(sum((t$MC - xag)^2 * t$ni) / sum(t$ni))
  data.frame(medida = c("Media", "Desviación estándar"),
             datos_totales = c(mean(x), sd(x)), datos_agrupados = c(xag, sag),
             error_pct = round(abs(c(xag - mean(x), sag - sd(x))) / c(mean(x), sd(x)) * 100, 2))
}

nota_abiertas <- function(tdf) {
  ab <- tdf[is.na(tdf$MC), ]
  if (nrow(ab) == 0) return("")
  paste0("Clases abiertas (fuera del gráfico): ", paste0(etiquetas(ab), ": ", ab$ni, " (", ab$hi, " %)", collapse = " · "))
}

graficos_continua <- function(x, tdf, nombre, unidad, archivo, n_graf = 1) {
  # Gráficas de la Lección 5: histograma + polígono (clases cerradas), ojiva combinada y diagrama de caja.
  t <- tdf[!is.na(tdf$MC), ]
  png(file.path(GRAFICOS, archivo), width = 1800, height = 1200, res = 130)
  layout(matrix(c(1, 1, 2, 3), 2, 2, byrow = TRUE), heights = c(1.15, 1))
  par(mar = c(8, 5, 4, 1))
  h <- barplot(t$hi, names.arg = etiquetas(t), space = 0, las = 2, col = "#3987e5", border = "white",
               ylab = "Porcentaje (%)", cex.names = .75, ylim = c(0, max(t$hi) * 1.15),
               main = paste0("Gráfica No. ", n_graf, ": Histograma y polígono de frecuencias de ", nombre, " (", unidad, ")"))
  lines(c(h[1] - 1, h, h[length(h)] + 1), c(0, t$hi, 0), col = "#d95926", lwd = 2, type = "b", pch = 16, cex = .6)
  mtext(nota_abiertas(tdf), side = 1, line = 6.5, cex = .7, col = "gray30")
  par(mar = c(5, 5, 4, 1))
  plot(t$Ls, t$Hi_asc, type = "b", pch = 16, col = "#3987e5", ylim = c(0, 100),
       xlab = paste0(nombre, " (", unidad, ")"), ylab = "Porcentaje acumulado (%)",
       main = paste0("Gráfica No. ", n_graf + 1, ": Ojiva ascendente y descendente"))
  lines(t$Li, t$Hi_dsc, type = "b", pch = 17, col = "#d95926")
  abline(h = 50, lty = 3, col = "gray50")
  legend("right", c("ascendente (≤)", "descendente (≥)"), col = c("#3987e5", "#d95926"), pch = c(16, 17), bty = "n", cex = .85)
  boxplot(x, horizontal = TRUE, col = "#86b6ef", xlab = paste0(nombre, " (", unidad, ")"),
          main = paste0("Gráfica No. ", n_graf + 2, ": Diagrama de caja (todos los datos)"))
  dev.off()
}

comparar_agrupacion <- function(tdf_defecto, tdf_final, nombre, unidad, archivo) {
  # La gráfica que justifica la decisión: histograma "por defecto" frente al corregido.
  t <- tdf_final[!is.na(tdf_final$MC), ]
  png(file.path(GRAFICOS, archivo), width = 1800, height = 780, res = 130)
  par(mfrow = c(1, 2), mar = c(8, 5, 4, 1))
  barplot(tdf_defecto$hi, names.arg = etiquetas(tdf_defecto, 1), space = 0, las = 2, cex.names = .65,
          col = "gray60", border = "white", ylab = "Porcentaje (%)",
          main = paste0("Por defecto: Sturges sobre el rango completo\n", nombre, ", k = ", nrow(tdf_defecto)))
  barplot(t$hi, names.arg = etiquetas(t), space = 0, las = 2, cex.names = .65,
          col = "#3987e5", border = "white", ylab = "Porcentaje (%)",
          main = paste0("Corregida: rango típico (IQR) + clases abiertas\n", nombre, " (", unidad, "), k = ", nrow(t), " cerradas"))
  mtext(nota_abiertas(tdf_final), side = 1, line = 6.5, cex = .65, col = "gray30")
  dev.off()
}
