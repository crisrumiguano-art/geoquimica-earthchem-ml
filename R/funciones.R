# FUNCIONES DEL PROYECTO (Unidad 1, estadística descriptiva)
# Aquí se escriben UNA vez los procedimientos del curso; los scripts 01 a 04 los usan.
# Se cargan con: source("R/funciones.R")
#
# Cómo leer:
#   nombre <- function(a, b) { ... }   = crea una función llamada "nombre" que recibe a y b
#   la última línea de la función      = lo que devuelve
#   # texto                            = comentario (R no lo ejecuta)

.libPaths(c(Sys.getenv("R_LIBS_USER"), .libPaths()))  # dónde buscar paquetes instalados
library(e1071)     # paquete: asimetría y curtosis
library(openxlsx)  # paquete: guardar Excel

# Carpetas donde se guardan los resultados (se crean si no existen)
SALIDAS <- "R/salidas"     # Excel
GRAFICOS <- "docs/img/r"   # imágenes PNG de la web
TABLAS_WEB <- "docs/data/tdf"
for (d in c(SALIDAS, GRAFICOS, TABLAS_WEB)) dir.create(d, showWarnings = FALSE, recursive = TRUE)

# QUÉ HACE: guarda una tabla como archivo CSV para la página web.
# RECIBE: tabla (data.frame) y nombre (texto).   DEVUELVE: nada (crea el archivo).
tabla_web <- function(tabla, nombre) {
  write.csv(tabla, file.path(TABLAS_WEB, paste0(nombre, ".csv")),  # ruta: docs/data/tdf/nombre.csv
            row.names = FALSE, fileEncoding = "UTF-8")             # sin números de fila; con tildes
}

# QUÉ HACE: lee la base de datos completa.
# RECIBE: ruta del archivo.   DEVUELVE: tabla de 159 760 filas × 75 columnas.
leer_base <- function(ruta = "data/earthchem_limpio.csv.gz") {
  read.csv(gzfile(ruta, encoding = "UTF-8"),  # gzfile = abre el archivo comprimido .gz
           check.names = FALSE)               # deja los nombres tal cual: "SiO2 (wt%)"
}

# ---------------------------------------------------------------- variables cualitativas

# QUÉ HACE: tabla de frecuencias (TDF) de una variable cualitativa.
# RECIBE: x = categorías; orden = NULL si es nominal, o el orden si es ordinal.
# DEVUELVE: tabla con categoria, ni, hi (y Ni, Hi si es ordinal).
tdf_cualitativa <- function(x, orden = NULL) {
  x <- x[!is.na(x) & x != ""]                       # quita vacíos
  f <- if (is.null(orden)) sort(table(x), decreasing = TRUE)  # nominal: cuenta y ordena de mayor a menor
       else table(factor(x, levels = orden))        # ordinal: cuenta en su orden natural
  tdf <- data.frame(categoria = names(f), ni = as.vector(f))  # ni = frecuencia absoluta
  tdf$hi <- round(tdf$ni / sum(tdf$ni) * 100, 2)    # hi = frecuencia relativa (%)
  if (!is.null(orden)) {                            # solo ordinales: acumuladas
    tdf$Ni_asc <- cumsum(tdf$ni)                     # cumsum = suma acumulada
    tdf$Hi_asc <- round(cumsum(tdf$ni) / sum(tdf$ni) * 100, 2)
  }
  tdf                                               # devuelve la tabla
}

# QUÉ HACE: dibuja diagrama de barras + diagrama circular y los guarda en un PNG.
# RECIBE: tdf (de tdf_cualitativa), título, nombre del archivo, número de gráfica.
graficos_cualitativa <- function(tdf, titulo, archivo, n_graf = 1) {
  png(file.path(GRAFICOS, archivo), width = 1600, height = 700, res = 130)  # abre la imagen
  par(mfrow = c(1, 2), mar = c(9, 5, 4, 1))         # 2 gráficos lado a lado; márgenes
  colores <- gray.colors(nrow(tdf), start = .25, end = .85)  # un gris por categoría
  barplot(tdf$ni, names.arg = tdf$categoria, las = 2, col = colores, ylab = "Cantidad",  # barras: altura = ni
          main = paste0("Gráfica No. ", n_graf, ": ", titulo), cex.names = .8, cex.main = .9)
  par(mar = c(1, 1, 4, 1))
  pie(tdf$hi, labels = paste0(tdf$hi, "%"), col = colores, clockwise = TRUE, cex = .75,  # circular: porción = hi
      main = paste0("Gráfica No. ", n_graf + 1, ": ", titulo, " (%)"), cex.main = .9)
  legend("topright", legend = tdf$categoria, fill = colores, cex = .6, bty = "n")  # leyenda
  dev.off()                                         # cierra y guarda la imagen
}

# ---------------------------------------------------------------- variables continuas y discretas

# QUÉ HACE: número de intervalos k según 3 reglas del curso (para comparar).
# RECIBE: n = cantidad de datos.   DEVUELVE: tabla regla / k.
reglas_k <- function(n) {
  data.frame(regla = c("Sturges: 1 + 3,3 log n", "raíz de n", "2 · raíz de n"),
             k = c(round(1 + 3.3 * log10(n)), round(sqrt(n)), round(2 * sqrt(n))))
}

# QUÉ HACE: redondea la amplitud hacia arriba a un número "redondo" (1, 2, 2,5, 5, 10...).
# RECIBE: a (ej. 1,71).   DEVUELVE: amplitud redonda (ej. 2).   Sirve para intervalos legibles: [48-50[.
amplitud_redonda <- function(a) {
  p <- 10^floor(log10(a))                           # potencia de 10: 1,71 -> 1;  17 -> 10
  for (m in c(1, 2, 2.5, 5, 10)) if (m * p >= a - 1e-12) return(m * p)  # primer múltiplo que alcanza
}

# QUÉ HACE: límites para detectar outliers (regla intercuartílica).
# RECIBE: x = datos.   DEVUELVE: límite inferior y superior.   Outlier = fuera de esos límites.
limites_iqr <- function(x) {
  q <- quantile(x, c(.25, .75), names = FALSE)      # Q1 y Q3
  ir <- q[2] - q[1]                                  # IR = Q3 - Q1
  c(inferior = q[1] - 1.5 * ir, superior = q[2] + 1.5 * ir)
}

# QUÉ HACE: TDF de una variable cuantitativa (Li, Ls, MC, ni, hi, Ni y Hi ↑ ↓).
# RECIBE: x = datos.  Opcionales: k (intervalos), a (amplitud), desde (primer límite), redondear,
#         lim = c(inf, sup): intervalos solo dentro de esos límites y lo de afuera en 2 clases abiertas.
# DEVUELVE: la TDF.   Sin opcionales = igual a la plantilla (Sturges, a = R / k).   No borra datos.
tdf_continua <- function(x, k = NULL, a = NULL, desde = NULL, redondear = TRUE, lim = NULL) {
  x <- x[!is.na(x)]                                  # quita vacíos
  n <- length(x)                                     # n = cantidad de datos
  if (is.null(k)) k <- round(1 + 3.3 * log10(n))     # k por Sturges
  xc <- if (is.null(lim)) x else x[x >= lim[1] & x <= lim[2]]  # datos que se agrupan en intervalos
  if (is.null(a)) a <- (max(xc) - min(xc)) / k       # amplitud = rango / k
  if (redondear) a <- amplitud_redonda(a)            # amplitud redonda
  if (is.null(desde)) desde <- if (redondear) floor(min(xc) / a) * a else min(xc)  # primer Li
  if (redondear) k <- floor((max(xc) - desde) / a) + 1  # k necesario para llegar al máximo
  Li <- desde + (0:(k - 1)) * a                      # límites inferiores
  Ls <- Li + a                                       # límites superiores
  dentro <- x >= Li[1] & x <= Ls[k]                  # datos dentro de los intervalos
  ni <- as.vector(table(cut(x[dentro], breaks = c(Li, Ls[k]), right = FALSE, include.lowest = TRUE)))  # cuenta por intervalo [Li, Ls[
  bajo <- sum(x < Li[1]); alto <- sum(x > Ls[k])     # datos fuera: por debajo y por encima
  if (bajo > 0) { Li <- c(-Inf, Li); Ls <- c(Li[2], Ls); ni <- c(bajo, ni) }  # clase abierta "< Li"
  if (alto > 0) { Li <- c(Li, Ls[length(Ls)]); Ls <- c(Ls, Inf); ni <- c(ni, alto) }  # clase abierta ">= Ls"
  MC <- ifelse(is.finite(Li) & is.finite(Ls), (Li + Ls) / 2, NA)  # marca de clase (las abiertas no tienen)
  data.frame(Li = Li, Ls = Ls, MC = MC, ni = ni, hi = round(ni / n * 100, 2),  # hi en %
             Ni_asc = cumsum(ni), Ni_dsc = rev(cumsum(rev(ni))),             # acumuladas ↑ y ↓
             Hi_asc = round(cumsum(ni) / n * 100, 2), Hi_dsc = round(rev(cumsum(rev(ni))) / n * 100, 2))
}

# QUÉ HACE: texto de cada intervalo: "[45-50[", "< 40" o "≥ 66".
# RECIBE: tdf y decimales.   DEVUELVE: vector de textos (para tablas y ejes).
etiquetas <- function(tdf, dec = 2) {
  f <- function(v) trimws(formatC(round(v, dec), format = "fg", digits = 6, big.mark = ""))  # número a texto
  ifelse(is.infinite(tdf$Li), paste0("< ", f(tdf$Ls)),                       # abierta abajo
         ifelse(is.infinite(tdf$Ls), paste0("≥ ", f(tdf$Li)), paste0("[", f(tdf$Li), "-", f(tdf$Ls), "[")))  # abierta arriba / normal
}

# QUÉ HACE: indicadores de posición, dispersión y forma (con todos los datos).
# RECIBE: x = datos.   DEVUELVE: tabla indicador / valor.
indicadores <- function(x) {
  x <- x[!is.na(x)]
  q <- quantile(x, c(.25, .5, .75), names = FALSE)  # Q1, mediana, Q3
  s <- sd(x); m <- mean(x)                          # desviación estándar y media
  data.frame(
    indicador = c("n", "Mínimo", "Q1", "Mediana", "Q3", "Máximo", "Media", "Rango intercuartílico",
                  "Varianza", "Desviación estándar", "Coeficiente de variación (%)", "Asimetría", "Curtosis"),
    valor = c(length(x), min(x), q[1], q[2], q[3], max(x), m, q[3] - q[1], var(x), s, s / m * 100,  # CV = s/media·100
              skewness(x), kurtosis(x)))            # asimetría y curtosis (paquete e1071)
}

# QUÉ HACE: error de agrupación: compara media y desviación de la TDF con las de los datos.
# RECIBE: x = datos, tdf.   DEVUELVE: tabla con ambos valores y el error en %.  (< 5 % = bien)
error_agrupacion <- function(x, tdf) {
  t <- tdf[!is.na(tdf$MC), ]                              # solo clases cerradas (tienen MC)
  x <- x[!is.na(x) & x >= min(t$Li) & x <= max(t$Ls)]     # los datos de esas clases
  xag <- sum(t$MC * t$ni) / sum(t$ni)                     # media agrupada = Σ MC·ni / n
  sag <- sqrt(sum((t$MC - xag)^2 * t$ni) / sum(t$ni))     # desviación agrupada
  data.frame(medida = c("Media", "Desviación estándar"),
             datos_totales = c(mean(x), sd(x)), datos_agrupados = c(xag, sag),
             error_pct = round(abs(c(xag - mean(x), sag - sd(x))) / c(mean(x), sd(x)) * 100, 2))  # error %
}

# QUÉ HACE: texto con las clases abiertas y cuántos datos tienen (va debajo del histograma).
nota_abiertas <- function(tdf) {
  ab <- tdf[is.na(tdf$MC), ]                        # filas sin MC = abiertas
  if (nrow(ab) == 0) return("")                     # si no hay, texto vacío
  paste0("Clases abiertas (fuera del gráfico): ", paste0(etiquetas(ab), ": ", ab$ni, " (", ab$hi, " %)", collapse = " · "))
}

# QUÉ HACE: histograma + polígono, ojiva ↑↓ y diagrama de caja en un PNG.
# RECIBE: x = datos, tdf, nombre y unidad (títulos), archivo, número de gráfica.
graficos_continua <- function(x, tdf, nombre, unidad, archivo, n_graf = 1) {
  t <- tdf[!is.na(tdf$MC), ]                        # solo clases cerradas
  png(file.path(GRAFICOS, archivo), width = 1800, height = 1200, res = 130)  # abre la imagen
  layout(matrix(c(1, 1, 2, 3), 2, 2, byrow = TRUE), heights = c(1.15, 1))   # arriba histograma; abajo ojiva y caja
  par(mar = c(8, 5, 4, 1))
  h <- barplot(t$hi, names.arg = etiquetas(t), space = 0, las = 2, col = "#3987e5", border = "white",  # histograma (barras pegadas)
               ylab = "Porcentaje (%)", cex.names = .75, ylim = c(0, max(t$hi) * 1.15),
               main = paste0("Gráfica No. ", n_graf, ": Histograma y polígono de frecuencias de ", nombre, " (", unidad, ")"))
  lines(c(h[1] - 1, h, h[length(h)] + 1), c(0, t$hi, 0), col = "#d95926", lwd = 2, type = "b", pch = 16, cex = .6)  # polígono
  mtext(nota_abiertas(tdf), side = 1, line = 6.5, cex = .7, col = "gray30")  # nota de clases abiertas
  par(mar = c(5, 5, 4, 1))
  plot(t$Ls, t$Hi_asc, type = "b", pch = 16, col = "#3987e5", ylim = c(0, 100),  # ojiva ascendente
       xlab = paste0(nombre, " (", unidad, ")"), ylab = "Porcentaje acumulado (%)",
       main = paste0("Gráfica No. ", n_graf + 1, ": Ojiva ascendente y descendente"))
  lines(t$Li, t$Hi_dsc, type = "b", pch = 17, col = "#d95926")  # ojiva descendente
  abline(h = 50, lty = 3, col = "gray50")           # línea del 50 % (donde se cruzan = mediana)
  legend("right", c("ascendente (≤)", "descendente (≥)"), col = c("#3987e5", "#d95926"), pch = c(16, 17), bty = "n", cex = .85)
  boxplot(x, horizontal = TRUE, col = "#86b6ef", xlab = paste0(nombre, " (", unidad, ")"),  # diagrama de caja
          main = paste0("Gráfica No. ", n_graf + 2, ": Diagrama de caja (todos los datos)"))
  dev.off()                                         # cierra y guarda
}

# QUÉ HACE: compara el histograma "por defecto" (plantilla) con el corregido (IQR + clases abiertas).
# RECIBE: las dos TDF, nombre, unidad y archivo.   Sirve para justificar la agrupación elegida.
comparar_agrupacion <- function(tdf_defecto, tdf_final, nombre, unidad, archivo) {
  t <- tdf_final[!is.na(tdf_final$MC), ]
  png(file.path(GRAFICOS, archivo), width = 1800, height = 780, res = 130)  # abre la imagen
  par(mfrow = c(1, 2), mar = c(8, 5, 4, 1))         # 2 histogramas lado a lado
  barplot(tdf_defecto$hi, names.arg = etiquetas(tdf_defecto, 1), space = 0, las = 2, cex.names = .65,  # izquierda: por defecto
          col = "gray60", border = "white", ylab = "Porcentaje (%)",
          main = paste0("Por defecto: Sturges sobre el rango completo\n", nombre, ", k = ", nrow(tdf_defecto)))
  barplot(t$hi, names.arg = etiquetas(t), space = 0, las = 2, cex.names = .65,  # derecha: corregido
          col = "#3987e5", border = "white", ylab = "Porcentaje (%)",
          main = paste0("Corregida: rango típico (IQR) + clases abiertas\n", nombre, " (", unidad, "), k = ", nrow(t), " cerradas"))
  mtext(nota_abiertas(tdf_final), side = 1, line = 6.5, cex = .65, col = "gray30")
  dev.off()
}
