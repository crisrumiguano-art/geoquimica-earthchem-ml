# =========================================================================================
# GRÁFICO: Ambiente tectónico agrupado   (cual_grupo_tectonico.png)
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
x <- base[["Tectonic Group"]]                         # la columna de la base
x <- as.character(x)                         # como texto
x <- x[!is.na(x) & x != ""]                  # quita los vacíos

# ---- 2. Tabla de frecuencias ----
conteo <- sort(table(x), decreasing = TRUE)  # cuenta cada categoría, de mayor a menor
categoria <- names(conteo)
ni <- as.vector(conteo)                      # frecuencia absoluta
hi <- round(ni / sum(ni) * 100, 2)           # frecuencia relativa (%)
TDF <- data.frame(categoria, ni, hi)         # nominal: sin acumuladas (no hay orden)
TDF                                          # muestra la tabla
categoria[which.max(ni)]                     # moda: la categoría con más casos

# ---- 3. Gráfico: barras + circular ----
png("docs/img/r/cual_grupo_tectonico.png", width = 1600, height = 700, res = 130)   # abre la imagen
par(mfrow = c(1, 2), mar = c(9, 5, 4, 1))    # 2 gráficos lado a lado
colores <- gray.colors(length(ni), start = .25, end = .85)       # un gris por categoría
barplot(ni, names.arg = categoria, las = 2, col = colores, ylab = "Cantidad",   # barras: altura = ni
        main = "Gráfica No. 1: Ambiente tectónico agrupado", cex.names = .8, cex.main = .9)
par(mar = c(1, 1, 4, 1))
pie(hi, labels = paste0(hi, "%"), col = colores, clockwise = TRUE, cex = .75,  # circular: porción = hi
    main = "Gráfica No. 2: Ambiente tectónico agrupado (%)", cex.main = .9)
legend("topright", legend = categoria, fill = colores, cex = .6, bty = "n")
dev.off()                                    # cierra y guarda la imagen

# Abre la imagen que se acaba de crear (solo en RStudio)
if (interactive()) browseURL(file.path(getwd(), "docs/img/r/cual_grupo_tectonico.png"))
