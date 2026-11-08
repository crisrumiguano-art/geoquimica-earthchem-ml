# =========================================================================================
# GRÁFICO: Clase de roca según SiO2   (cual_clase_sio2.png)
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
x <- base[["SiO2 Class"]]                         # la columna de la base
x <- as.character(x)                         # como texto
x <- x[!is.na(x) & x != ""]                  # quita los vacíos

# ---- 2. Tabla de frecuencias ----
orden <- c("ultrabasica", "basica", "intermedia", "acida")   # ordinal: su orden natural
conteo <- table(factor(x, levels = orden))   # cuenta cada categoría, en ese orden
categoria <- names(conteo)
ni <- as.vector(conteo)                      # frecuencia absoluta
hi <- round(ni / sum(ni) * 100, 2)           # frecuencia relativa (%)
Ni <- cumsum(ni)                             # acumulada absoluta (solo ordinales)
Hi <- round(cumsum(ni) / sum(ni) * 100, 2)   # acumulada relativa (%)
TDF <- data.frame(categoria, ni, hi, Ni, Hi)
TDF                                          # muestra la tabla
categoria[which.max(ni)]                     # moda: la categoría con más casos
categoria[which(Hi >= 50)[1]]                # mediana: donde Hi llega al 50 %

# ---- 3. Gráfico: barras + circular ----
png("docs/img/r/cual_clase_sio2.png", width = 1600, height = 700, res = 130)   # abre la imagen
par(mfrow = c(1, 2), mar = c(9, 5, 4, 1))    # 2 gráficos lado a lado
colores <- gray.colors(length(ni), start = .25, end = .85)       # un gris por categoría
barplot(ni, names.arg = categoria, las = 2, col = colores, ylab = "Cantidad",   # barras: altura = ni
        main = "Gráfica No. 5: Clase de roca según SiO2", cex.names = .8, cex.main = .9)
par(mar = c(1, 1, 4, 1))
pie(hi, labels = paste0(hi, "%"), col = colores, clockwise = TRUE, cex = .75,  # circular: porción = hi
    main = "Gráfica No. 6: Clase de roca según SiO2 (%)", cex.main = .9)
legend("topright", legend = categoria, fill = colores, cex = .6, bty = "n")
dev.off()                                    # cierra y guarda la imagen

# Abre la imagen que se acaba de crear (solo en RStudio)
if (interactive()) browseURL(file.path(getwd(), "docs/img/r/cual_clase_sio2.png"))
