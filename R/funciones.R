# Funciones de estadística descriptiva (Unidad 1) para la base EarthChem PetDB.
# Siguen la estructura de las plantillas del curso: TDF con Li, Ls, MC, ni, hi, Ni y Hi ascendentes y
# descendentes; histograma con barplot(space = 0), polígono, ojiva y diagrama de caja.
# Se cargan con source("R/funciones.R") desde la raíz del repositorio.
#
# Cómo leer este archivo: cada función empieza con un bloque de comentarios que dice QUÉ hace, QUÉ recibe
# (argumentos) y QUÉ devuelve. Dentro, los comentarios explican cada paso. Una función se define así:
#   nombre <- function(argumento1, argumento2 = valor_por_defecto) { ...instrucciones...; resultado }
# y la última línea de la función es lo que devuelve.

.libPaths(c(Sys.getenv("R_LIBS_USER"), .libPaths()))  # busca primero los paquetes instalados por el usuario
library(e1071)     # skewness() y kurtosis(), como en las plantillas
library(openxlsx)  # exportar las TDF a Excel

# Carpetas de salida (se crean solas si no existen).
SALIDAS <- "R/salidas"     # Excel con todas las tablas
GRAFICOS <- "docs/img/r"   # PNG: van directo a la web
TABLAS_WEB <- "docs/data/tdf"
for (d in c(SALIDAS, GRAFICOS, TABLAS_WEB)) dir.create(d, showWarnings = FALSE, recursive = TRUE)

# Guarda una tabla como CSV para que la página web la muestre.
#   tabla: data.frame;  nombre: nombre del archivo sin ".csv".
tabla_web <- function(tabla, nombre) {
  # file.path() arma la ruta con "/" y paste0() pega textos sin espacios: "docs/data/tdf/<nombre>.csv".
  # row.names = FALSE: no escribir la columna con el número de fila.
  write.csv(tabla, file.path(TABLAS_WEB, paste0(nombre, ".csv")), row.names = FALSE, fileEncoding = "UTF-8")
}

# Lee la base limpia (159 760 filas × 75 columnas) y la devuelve como data.frame.
leer_base <- function(ruta = "data/earthchem_limpio.csv.gz") {
  # El archivo está comprimido (.gz): gzfile() lo descomprime al vuelo mientras read.csv() lo lee.
  # gzfile() con encoding explícito: read.csv directo sobre el .gz se cae en Windows con R 4.6.
  # check.names = FALSE: conserva los nombres originales de las columnas, p. ej. "SiO2 (wt%)",
  # que se usan entre corchetes: base[["SiO2 (wt%)"]].
  read.csv(gzfile(ruta, encoding = "UTF-8"), check.names = FALSE)
}

# ---------------------------------------------------------------- variables cualitativas

# Tabla de distribución de frecuencias (TDF) de una variable cualitativa (Lección 5).
#   x: vector de categorías (texto);  orden: NULL si es nominal, o las categorías en orden si es ordinal.
# Devuelve un data.frame con categoria, ni (frecuencia absoluta) y hi (relativa, en %); si es ordinal,
# además Ni y Hi acumuladas.
tdf_cualitativa <- function(x, orden = NULL) {
  # 1) Quitar los vacíos: NA (no disponible) y "" (texto vacío). ! es "no", & es "y".
  x <- x[!is.na(x) & x != ""]
  # 2) Contar cuántas veces aparece cada categoría con table().
  #    Nominal: de mayor a menor (sort decreasing). Ordinal: factor() impone el orden natural.
  f <- if (is.null(orden)) sort(table(x), decreasing = TRUE) else table(factor(x, levels = orden))
  # 3) Pasar el conteo a una tabla: una fila por categoría.
  tdf <- data.frame(categoria = names(f), ni = as.vector(f))
  # 4) hi = ni / n · 100, redondeado a 2 decimales. sum(tdf$ni) es n.
  tdf$hi <- round(tdf$ni / sum(tdf$ni) * 100, 2)
  # 5) Solo si es ordinal: acumuladas. cumsum() suma "hasta aquí": 3, 5, 2 -> 3, 8, 10.
  #    En una nominal no tienen sentido porque las categorías no tienen orden.
  if (!is.null(orden)) {
    tdf$Ni_asc <- cumsum(tdf$ni)
    tdf$Hi_asc <- round(cumsum(tdf$ni) / sum(tdf$ni) * 100, 2)
  }
  tdf  # última línea: lo que devuelve la función
}

# Diagrama de barras (ni) y diagrama circular (hi) de una TDF cualitativa, guardados en un PNG.
#   tdf: salida de tdf_cualitativa();  titulo: texto;  archivo: nombre del PNG;  n_graf: número de gráfica.
graficos_cualitativa <- function(tdf, titulo, archivo, n_graf = 1) {
  # png() abre un "lienzo" en un archivo: todo lo que se dibuje hasta dev.off() va a esa imagen.
  # width/height en píxeles; res = resolución (puntos por pulgada).
  png(file.path(GRAFICOS, archivo), width = 1600, height = 700, res = 130)
  # par(mfrow = c(1, 2)): divide el lienzo en 1 fila y 2 columnas (dos gráficos lado a lado).
  # mar = márgenes (abajo, izquierda, arriba, derecha), en líneas de texto; abajo es grande por los nombres.
  par(mfrow = c(1, 2), mar = c(9, 5, 4, 1))
  colores <- gray.colors(nrow(tdf), start = .25, end = .85)  # un gris distinto por categoría
  # Barras: altura = ni. las = 2 pone los nombres verticales; cex.names achica la letra.
  barplot(tdf$ni, names.arg = tdf$categoria, las = 2, col = colores, ylab = "Cantidad",
          main = paste0("Gráfica No. ", n_graf, ": ", titulo), cex.names = .8, cex.main = .9)
  par(mar = c(1, 1, 4, 1))
  # Circular: cada porción es proporcional a hi; las etiquetas muestran el porcentaje.
  pie(tdf$hi, labels = paste0(tdf$hi, "%"), col = colores, clockwise = TRUE, cex = .75,
      main = paste0("Gráfica No. ", n_graf + 1, ": ", titulo, " (%)"), cex.main = .9)
  legend("topright", legend = tdf$categoria, fill = colores, cex = .6, bty = "n")  # bty = "n": sin recuadro
  dev.off()  # cierra el lienzo y escribe el PNG
}

# ---------------------------------------------------------------- variables continuas y discretas

# Número de intervalos k según las reglas del curso (Lección 5), para comparar.
#   n: cantidad de datos. Ejemplo: n = 57 031 -> Sturges k = round(1 + 3,3 · log10(57 031)) = 17.
reglas_k <- function(n) {
  data.frame(regla = c("Sturges: 1 + 3,3 log n", "raíz de n", "2 · raíz de n"),
             k = c(round(1 + 3.3 * log10(n)), round(sqrt(n)), round(2 * sqrt(n))))
}

# Lleva la amplitud a un valor "redondo" (1, 2, 2,5 o 5 por una potencia de 10) igual o mayor:
# intervalos como [45-50[ son legibles; [44,317-50,108[ no.
#   a: amplitud calculada. Ejemplo: a = 4,3 -> potencia p = 1 -> el primer múltiplo >= 4,3 es 5 -> devuelve 5.
amplitud_redonda <- function(a) {
  p <- 10^floor(log10(a))  # potencia de 10 de la amplitud: 4,3 -> 1;  43 -> 10;  0,43 -> 0,1
  # Prueba 1·p, 2·p, 2,5·p, 5·p y 10·p y devuelve el primero que alcanza a cubrir a.
  # (- 1e-12 evita que un error de redondeo del computador descarte un valor exacto).
  for (m in c(1, 2, 2.5, 5, 10)) if (m * p >= a - 1e-12) return(m * p)
}

# Regla intercuartílica (Lección 6): outlier si x < Q1 - 1,5·IR o x > Q3 + 1,5·IR.
# Devuelve los dos límites con nombre: c(inferior = ..., superior = ...).
limites_iqr <- function(x) {
  q <- quantile(x, c(.25, .75), names = FALSE)  # Q1 (25 %) y Q3 (75 %)
  ir <- q[2] - q[1]                              # rango intercuartílico IR = Q3 - Q1
  c(inferior = q[1] - 1.5 * ir, superior = q[2] + 1.5 * ir)
}

# TDF de una variable cuantitativa: Li, Ls, MC, ni, hi, Ni y Hi ascendentes y descendentes.
#   x: datos numéricos;  k: número de intervalos (si no se da, Sturges);  a: amplitud (si no, R / k);
#   desde: primer límite inferior;  redondear: amplitud y límites redondos;
#   lim = c(inferior, superior): los intervalos cerrados cubren solo ese recorrido (p. ej. los límites
#   IQR) y lo que queda fuera va a dos clases abiertas, "< Li" y ">= Ls". No se descarta ningún dato.
# Sin argumentos reproduce la plantilla del curso: k por Sturges y a = R / k desde el mínimo.
tdf_continua <- function(x, k = NULL, a = NULL, desde = NULL, redondear = TRUE, lim = NULL) {
  x <- x[!is.na(x)]  # solo los datos medidos
  n <- length(x)
  if (is.null(k)) k <- round(1 + 3.3 * log10(n))                          # regla de Sturges
  xc <- if (is.null(lim)) x else x[x >= lim[1] & x <= lim[2]]              # datos del recorrido a agrupar
  if (is.null(a)) a <- (max(xc) - min(xc)) / k                             # amplitud = rango / k
  if (redondear) a <- amplitud_redonda(a)
  if (is.null(desde)) desde <- if (redondear) floor(min(xc) / a) * a else min(xc)  # p. ej. 44,3 con a = 5 -> 40
  # Con límites redondos, k es lo que haga falta para cubrir hasta el máximo (puede ser k ± 1).
  # Sin redondear se conserva k: el máximo cae en el último intervalo, cerrado por include.lowest.
  if (redondear) k <- floor((max(xc) - desde) / a) + 1
  # Límites: Li = desde, desde + a, desde + 2a, ...;  Ls = Li + a.  (0:(k - 1) es la secuencia 0, 1, ..., k-1)
  Li <- desde + (0:(k - 1)) * a
  Ls <- Li + a
  # Contar los datos de cada intervalo [Li, Ls[ : cut() asigna cada dato a su intervalo y table() los cuenta.
  # right = FALSE: el intervalo incluye su límite inferior y no el superior, como en el curso.
  dentro <- x >= Li[1] & x <= Ls[k]
  ni <- as.vector(table(cut(x[dentro], breaks = c(Li, Ls[k]), right = FALSE, include.lowest = TRUE)))
  # Clases abiertas: los datos por debajo del primer Li y por encima del último Ls (si los hay).
  # -Inf e Inf marcan el extremo abierto; esas clases no tienen marca de clase.
  bajo <- sum(x < Li[1]); alto <- sum(x > Ls[k])
  if (bajo > 0) { Li <- c(-Inf, Li); Ls <- c(Li[2], Ls); ni <- c(bajo, ni) }
  if (alto > 0) { Li <- c(Li, Ls[length(Ls)]); Ls <- c(Ls, Inf); ni <- c(ni, alto) }
  MC <- ifelse(is.finite(Li) & is.finite(Ls), (Li + Ls) / 2, NA)  # marca de clase = punto medio
  # Acumuladas: ascendente = cumsum (de arriba hacia abajo); descendente = cumsum al revés (rev).
  data.frame(Li = Li, Ls = Ls, MC = MC, ni = ni, hi = round(ni / n * 100, 2),
             Ni_asc = cumsum(ni), Ni_dsc = rev(cumsum(rev(ni))),
             Hi_asc = round(cumsum(ni) / n * 100, 2), Hi_dsc = round(rev(cumsum(rev(ni))) / n * 100, 2))
}

# Texto de cada intervalo para tablas y gráficos: "[45-50[", "< 40" (abierta abajo), "≥ 66" (abierta arriba).
#   dec: decimales a mostrar.
etiquetas <- function(tdf, dec = 2) {
  # f() es una función interna: redondea y quita espacios sobrantes (trimws).
  f <- function(v) trimws(formatC(round(v, dec), format = "fg", digits = 6, big.mark = ""))
  # ifelse(condición, si_verdadero, si_falso) trabaja fila por fila.
  ifelse(is.infinite(tdf$Li), paste0("< ", f(tdf$Ls)),
         ifelse(is.infinite(tdf$Ls), paste0("≥ ", f(tdf$Li)), paste0("[", f(tdf$Li), "-", f(tdf$Ls), "[")))
}

# Indicadores de posición, dispersión y forma (Lección 6), calculados con TODOS los datos (no agrupados).
indicadores <- function(x) {
  x <- x[!is.na(x)]
  q <- quantile(x, c(.25, .5, .75), names = FALSE)  # Q1, mediana, Q3
  s <- sd(x); m <- mean(x)                          # desviación estándar y media
  data.frame(
    indicador = c("n", "Mínimo", "Q1", "Mediana", "Q3", "Máximo", "Media", "Rango intercuartílico",
                  "Varianza", "Desviación estándar", "Coeficiente de variación (%)", "Asimetría", "Curtosis"),
    # CV = s / media · 100.  Asimetría > 0: cola larga a la derecha.  Curtosis > 0: más puntiaguda que la normal.
    valor = c(length(x), min(x), q[1], q[2], q[3], max(x), m, q[3] - q[1], var(x), s, s / m * 100,
              skewness(x), kurtosis(x)))
}

# Error de agrupación (Lección 6): cuánto cambian la media y la desviación si se calculan con la TDF
# (suponiendo que cada dato vale la marca de clase de su intervalo) en vez de con los datos originales.
# Solo clases cerradas (las abiertas no tienen marca de clase).
error_agrupacion <- function(x, tdf) {
  t <- tdf[!is.na(tdf$MC), ]                              # solo filas con MC
  x <- x[!is.na(x) & x >= min(t$Li) & x <= max(t$Ls)]     # los mismos datos que cubren esas clases
  xag <- sum(t$MC * t$ni) / sum(t$ni)                     # media agrupada = Σ MC·ni / n
  sag <- sqrt(sum((t$MC - xag)^2 * t$ni) / sum(t$ni))     # desviación agrupada = raíz de Σ (MC - media)²·ni / n
  # error % = |agrupado - total| / total · 100.  Menos de 5 % se considera aceptable.
  data.frame(medida = c("Media", "Desviación estándar"),
             datos_totales = c(mean(x), sd(x)), datos_agrupados = c(xag, sag),
             error_pct = round(abs(c(xag - mean(x), sag - sd(x))) / c(mean(x), sd(x)) * 100, 2))
}

# Texto con las clases abiertas y cuántos datos tienen, para escribirlo debajo del histograma.
nota_abiertas <- function(tdf) {
  ab <- tdf[is.na(tdf$MC), ]              # las abiertas son las filas sin marca de clase
  if (nrow(ab) == 0) return("")
  paste0("Clases abiertas (fuera del gráfico): ", paste0(etiquetas(ab), ": ", ab$ni, " (", ab$hi, " %)", collapse = " · "))
}

# Gráficas de la Lección 5 en un solo PNG: histograma + polígono de frecuencias (clases cerradas),
# ojiva ascendente y descendente, y diagrama de caja con todos los datos.
#   x: datos;  tdf: salida de tdf_continua();  nombre y unidad: para los títulos;  archivo: PNG;  n_graf: número.
graficos_continua <- function(x, tdf, nombre, unidad, archivo, n_graf = 1) {
  t <- tdf[!is.na(tdf$MC), ]  # el histograma solo dibuja las clases cerradas
  png(file.path(GRAFICOS, archivo), width = 1800, height = 1200, res = 130)
  # layout(): el histograma ocupa toda la fila de arriba (1, 1) y abajo van la ojiva (2) y la caja (3).
  layout(matrix(c(1, 1, 2, 3), 2, 2, byrow = TRUE), heights = c(1.15, 1))
  par(mar = c(8, 5, 4, 1))
  # Histograma: barplot con space = 0 (barras pegadas, como pide la plantilla). barplot devuelve en h
  # la posición x del centro de cada barra, que sirve para dibujar el polígono encima.
  h <- barplot(t$hi, names.arg = etiquetas(t), space = 0, las = 2, col = "#3987e5", border = "white",
               ylab = "Porcentaje (%)", cex.names = .75, ylim = c(0, max(t$hi) * 1.15),
               main = paste0("Gráfica No. ", n_graf, ": Histograma y polígono de frecuencias de ", nombre, " (", unidad, ")"))
  # Polígono: une los puntos (centro de cada barra, hi) y baja a 0 un intervalo antes y uno después.
  lines(c(h[1] - 1, h, h[length(h)] + 1), c(0, t$hi, 0), col = "#d95926", lwd = 2, type = "b", pch = 16, cex = .6)
  mtext(nota_abiertas(tdf), side = 1, line = 6.5, cex = .7, col = "gray30")  # texto bajo el eje x
  par(mar = c(5, 5, 4, 1))
  # Ojiva ascendente: Hi acumulada "menor que" en cada límite superior Ls.
  plot(t$Ls, t$Hi_asc, type = "b", pch = 16, col = "#3987e5", ylim = c(0, 100),
       xlab = paste0(nombre, " (", unidad, ")"), ylab = "Porcentaje acumulado (%)",
       main = paste0("Gráfica No. ", n_graf + 1, ": Ojiva ascendente y descendente"))
  # Ojiva descendente: Hi acumulada "mayor o igual que" en cada límite inferior Li.
  lines(t$Li, t$Hi_dsc, type = "b", pch = 17, col = "#d95926")
  abline(h = 50, lty = 3, col = "gray50")  # donde se cruzan las dos ojivas, al 50 %, está la mediana
  legend("right", c("ascendente (≤)", "descendente (≥)"), col = c("#3987e5", "#d95926"), pch = c(16, 17), bty = "n", cex = .85)
  # Diagrama de caja: caja de Q1 a Q3, línea en la mediana, bigotes hasta 1,5·IR y puntos = outliers.
  boxplot(x, horizontal = TRUE, col = "#86b6ef", xlab = paste0(nombre, " (", unidad, ")"),
          main = paste0("Gráfica No. ", n_graf + 2, ": Diagrama de caja (todos los datos)"))
  dev.off()
}

# La gráfica que justifica la decisión de agrupación: histograma "por defecto" (Sturges sobre todo el
# rango) frente al corregido (intervalos sobre el rango típico IQR + clases abiertas).
comparar_agrupacion <- function(tdf_defecto, tdf_final, nombre, unidad, archivo) {
  t <- tdf_final[!is.na(tdf_final$MC), ]
  png(file.path(GRAFICOS, archivo), width = 1800, height = 780, res = 130)
  par(mfrow = c(1, 2), mar = c(8, 5, 4, 1))  # dos histogramas lado a lado
  # Izquierda: por defecto. Con valores extremos casi todo cae en una o dos barras y no se ve la forma.
  barplot(tdf_defecto$hi, names.arg = etiquetas(tdf_defecto, 1), space = 0, las = 2, cex.names = .65,
          col = "gray60", border = "white", ylab = "Porcentaje (%)",
          main = paste0("Por defecto: Sturges sobre el rango completo\n", nombre, ", k = ", nrow(tdf_defecto)))
  # Derecha: corregido. Los extremos no se borran: quedan contados en las clases abiertas (nota de abajo).
  barplot(t$hi, names.arg = etiquetas(t), space = 0, las = 2, cex.names = .65,
          col = "#3987e5", border = "white", ylab = "Porcentaje (%)",
          main = paste0("Corregida: rango típico (IQR) + clases abiertas\n", nombre, " (", unidad, "), k = ", nrow(t), " cerradas"))
  mtext(nota_abiertas(tdf_final), side = 1, line = 6.5, cex = .65, col = "gray30")
  dev.off()
}
