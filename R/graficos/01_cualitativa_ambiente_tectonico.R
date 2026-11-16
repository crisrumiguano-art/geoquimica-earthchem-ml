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
nombres <- c("dorsal y corteza oceanica" = "dorsal y corteza oceánica")   # nombres en español
cambia <- x %in% names(nombres)
x[cambia] <- nombres[x[cambia]]               # se reemplazan por el nombre en español
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
par(mfrow = c(1, 2), mar = c(10, 6.5, 4, 1))  # 2 gráficos lado a lado
colores <- gray.colors(length(ni), start = .25, end = .85)       # un gris por categoría
barplot(ni, names.arg = categoria, las = 2, col = colores,       # barras: altura = ni
        main = "Gráfica N° 1: Ambiente tectónico agrupado", cex.names = .8, cex.main = .9)
title(ylab = "Cantidad", line = 5)           # rótulo del eje, separado de los números
par(mar = c(1, 1, 4, 1))
pie(hi, labels = ifelse(hi >= 3, paste0(hi, " %"), ""), col = colores,   # circular: porción = hi
    clockwise = TRUE, cex = .75, main = "Gráfica N° 2: Ambiente tectónico agrupado (%)", cex.main = .9)   # solo se rotulan las de 3 % o más
legend("topright", legend = paste0(categoria, " (", hi, " %)"), fill = colores, cex = .6, bty = "n")   # leyenda con %
dev.off()                                    # cierra y guarda la imagen

# Abre la imagen que se acaba de crear (solo en RStudio)
if (interactive()) browseURL(file.path(getwd(), "docs/img/r/cual_grupo_tectonico.png"))
