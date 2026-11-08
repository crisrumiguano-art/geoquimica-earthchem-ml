# =========================================================================================
# GRÁFICO: MgO: agrupación por defecto vs corregida   (MgO_agrupacion.png)
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
x <- base[["MgO (wt%)"]]
tipo <- base[["Sample Type"]]                        # tipo de roca de cada fila
tiene <- !is.na(x)                                     # filas con dato
x <- x[tiene]
tipo <- tipo[tiene]
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
a <- 2                                               # se redondea hacia arriba a un número cómodo
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

# ---- 5. TDF "por defecto" (como la plantilla): Sturges sobre TODO el rango, en la escala original ----
x0 <- base[["MgO (wt%)"]]
x0 <- x0[!is.na(x0)]
k0 <- round(1 + 3.3 * log10(length(x0)))
a0 <- (max(x0) - min(x0)) / k0                         # amplitud sin redondear
Li0 <- min(x0) + (0:(k0 - 1)) * a0
Ls0 <- Li0 + a0
ni0 <- as.vector(table(cut(x0[x0 <= Ls0[k0]], breaks = c(Li0, Ls0[k0]), right = FALSE, include.lowest = TRUE)))
arriba0 <- sum(x0 > Ls0[k0])                           # por redondeo, el máximo puede quedar afuera
hi0 <- round(c(ni0, arriba0[arriba0 > 0]) / length(x0) * 100, 2)
num <- function(v) trimws(formatC(round(v, 1), format = "fg", digits = 6))   # número a texto: 1 decimal, 6 cifras
etiq0 <- c(paste0("[", num(Li0), "-", num(Ls0), "["), if (arriba0 > 0) paste0("≥ ", num(Ls0[k0])))

# ---- 6. Gráfico: por defecto (izquierda) vs corregida (derecha) ----
etiq <- paste0("[", Li, "-", Ls, "[")
nota <- c(if (abajo > 0) paste0("< ", Li[1], ": ", abajo, " (", round(abajo / n * 100, 2), " %)"),
          if (arriba > 0) paste0("≥ ", Ls[k], ": ", arriba, " (", round(arriba / n * 100, 2), " %)"))
png("docs/img/r/MgO_agrupacion.png", width = 1800, height = 780, res = 130)    # abre la imagen
par(mfrow = c(1, 2), mar = c(8, 5, 4, 1))              # 2 histogramas lado a lado
barplot(hi0, names.arg = etiq0, space = 0, las = 2, cex.names = .65, col = "gray60", border = "white",
        ylab = "Porcentaje (%)", main = paste0("Por defecto: Sturges sobre el rango completo\nMgO, k = ", length(hi0)))
barplot(hi, names.arg = etiq, space = 0, las = 2, cex.names = .65, col = "#3987e5", border = "white",
        ylab = "Porcentaje (%)", main = paste0("Corregida: rango típico (IQR) + clases abiertas\nMgO (wt%), k = ", k, " cerradas"))
mtext(if (length(nota) > 0) paste0("Clases abiertas (fuera del gráfico): ", paste(nota, collapse = " · ")) else "",
      side = 1, line = 6.5, cex = .65, col = "gray30")
dev.off()                                              # cierra y guarda la imagen

# Abre la imagen que se acaba de crear (solo en RStudio)
if (interactive()) browseURL(file.path(getwd(), "docs/img/r/MgO_agrupacion.png"))
