# =========================================================================================
# MUESTREO (Lección 3): aleatorio simple, sistemático y estratificado
# Saca 3 muestras del mismo tamaño de la base (N = 159 760), las compara con la base completa
# y repite cada método 500 veces para ver cuál es más preciso.
# Correr desde la carpeta del repositorio (RStudio: abrir el proyecto; o Rscript R/04_muestreo.R).
# Las líneas con # son explicaciones (R no las ejecuta).
# =========================================================================================

library(openxlsx)   # para guardar Excel (install.packages("openxlsx"))

# ---- 1. Datos ----
base <- read.csv(gzfile("data/earthchem_limpio.csv.gz", encoding = "UTF-8"), check.names = FALSE)
set.seed(2026)      # semilla: el sorteo sale igual cada vez que se corre
N <- nrow(base)     # tamaño de la población (número de filas)

# Estratos = ambiente tectónico agrupado (las filas sin dato forman su propio estrato)
estrato <- base[["Tectonic Group"]]
estrato[is.na(estrato) | estrato == ""] <- "sin dato"

# ---- 2. Tamaño de la muestra ----
# n0 = z² · p · q / e²   y   n = n0 / (1 + (n0 - 1) / N)
z <- 1.96           # 95 % de confianza
p <- 0.5            # p = q = 0,5: el caso más desfavorable
e <- 0.03           # error máximo: 3 %
n0 <- z^2 * p * (1 - p) / e^2
n <- ceiling(n0 / (1 + (n0 - 1) / N))   # ceiling = redondear hacia arriba
c(N = N, n0 = n0, n = n)

# ---- 3. Cuántas filas le tocan a cada estrato (afijación proporcional) ----
Nh <- table(estrato)                    # tamaño de cada estrato
exacto <- n * Nh / N                    # n_h = n · N_h / N  (con decimales)
nh <- floor(exacto)                     # parte entera
falta <- n - sum(nh)                    # lo que falta para llegar a n
mayores <- order(exacto - nh, decreasing = TRUE)[seq_len(falta)]   # los de mayor decimal
nh[mayores] <- nh[mayores] + 1          # reciben 1 más
tabla_afijacion <- data.frame(estrato = names(Nh), N_h = as.vector(Nh),
                              peso = round(as.vector(Nh) / N * 100, 2), n_h = as.vector(nh))
tabla_afijacion

# ---- 4. Las tres muestras (cada una = números de fila) ----
# ALEATORIO SIMPLE: sorteo de n filas entre 1 y N, sin repetir
m_aleatoria <- sample(N, n)

# SISTEMÁTICO: una fila cada k, empezando en una fila sorteada entre 1 y k
k <- floor(N / n)                       # intervalo: 159760 / 1061 ≈ 150
inicio <- sample(k, 1)
m_sistematica <- inicio + (0:(n - 1)) * k   # inicio, inicio + k, inicio + 2k, ...

# ESTRATIFICADO: sorteo dentro de cada estrato, con su n_h
m_estratificada <- c()
for (h in names(nh)) {
  filas <- which(estrato == h)          # filas de ese estrato
  m_estratificada <- c(m_estratificada, filas[sample(length(filas), nh[[h]])])
}

# ---- 5. ¿Las muestras se parecen a la población? ----
# % de cada estrato en la población y en cada muestra
porcentaje <- function(filas) round(prop.table(table(factor(estrato[filas], levels = names(nh)))) * 100, 2)
comp_estratos <- data.frame(estrato = names(nh),
                            poblacion = as.vector(porcentaje(1:N)),
                            aleatoria = as.vector(porcentaje(m_aleatoria)),
                            sistematica = as.vector(porcentaje(m_sistematica)),
                            estratificada = as.vector(porcentaje(m_estratificada)))
comp_estratos

# Media de tres variables en la población y en cada muestra
comp_medias <- data.frame()
for (v in c("SiO2 (wt%)", "MgO (wt%)", "Publication Year")) {
  valores <- base[[v]]
  comp_medias <- rbind(comp_medias, data.frame(
    variable = v,
    poblacion = round(mean(valores, na.rm = TRUE), 3),
    aleatoria = round(mean(valores[m_aleatoria], na.rm = TRUE), 3),
    sistematica = round(mean(valores[m_sistematica], na.rm = TRUE), 3),
    estratificada = round(mean(valores[m_estratificada], na.rm = TRUE), 3),
    n_con_dato_estratificada = sum(!is.na(valores[m_estratificada]))))
}
comp_medias

# ---- 6. Repetir cada método 500 veces: ¿cuál es más preciso? ----
# Cada muestra da una media de SiO2 distinta; cuanto menos varían (error estándar), mejor el método.
R <- 500
sio2 <- base[["SiO2 (wt%)"]]
sim <- matrix(NA, nrow = R, ncol = 3, dimnames = list(NULL, c("aleatoria", "sistematica", "estratificada")))
for (r in 1:R) sim[r, "aleatoria"] <- mean(sio2[sample(N, n)], na.rm = TRUE)
for (r in 1:R) sim[r, "sistematica"] <- mean(sio2[sample(k, 1) + (0:(n - 1)) * k], na.rm = TRUE)
for (r in 1:R) {
  filas_r <- c()
  for (h in names(nh)) {
    filas <- which(estrato == h)
    filas_r <- c(filas_r, filas[sample(length(filas), nh[[h]])])
  }
  sim[r, "estratificada"] <- mean(sio2[filas_r], na.rm = TRUE)
}
comp_repeticiones <- data.frame(metodo = colnames(sim),
                                media_de_las_medias = round(colMeans(sim), 3),     # promedio de las 500 medias
                                error_estandar = round(apply(sim, 2, sd), 4),      # cuánto varían
                                sesgo = round(colMeans(sim) - mean(sio2, na.rm = TRUE), 4))
comp_repeticiones

# ---- 7. Gráficos ----
dir.create("docs/img/r", recursive = TRUE, showWarnings = FALSE)
png("docs/img/r/muestreo_estratos.png", width = 1100, height = 650, res = 130)
m <- t(as.matrix(comp_estratos[, -1]))              # filas = población y muestras; columnas = estratos
colnames(m) <- comp_estratos$estrato
barplot(m, beside = TRUE, col = c("gray25", "gray55", "gray75", "gray90"), ylim = c(0, max(m) * 1.2),
        main = "Gráfica No. 1: Porcentaje por ambiente tectónico, población y muestras",
        ylab = "Porcentaje (%)", cex.names = 0.8, legend.text = TRUE,
        args.legend = list(x = "topright", bty = "n", cex = 0.8))
dev.off()

png("docs/img/r/muestreo_repeticiones.png", width = 1100, height = 650, res = 130)
boxplot(sim, col = c("gray55", "gray75", "gray90"), ylab = "Media de SiO2 (wt%)",
        main = paste0("Gráfica No. 2: Media de SiO2 en ", R, " muestras de cada método (n = ", n, ")"))
abline(h = mean(sio2, na.rm = TRUE), lty = 2)       # media de la población
legend("topright", "media poblacional", lty = 2, bty = "n", cex = 0.8)
dev.off()

# ---- 8. Guardar resultados ----
base$Estrato <- estrato
dir.create("data/muestras", showWarnings = FALSE)
write.csv(base[m_aleatoria, ], "data/muestras/muestra_aleatoria.csv", row.names = FALSE, fileEncoding = "UTF-8")
write.csv(base[m_sistematica, ], "data/muestras/muestra_sistematica.csv", row.names = FALSE, fileEncoding = "UTF-8")
write.csv(base[m_estratificada, ], "data/muestras/muestra_estratificada.csv", row.names = FALSE, fileEncoding = "UTF-8")

resumen <- data.frame(dato = c("N (población)", "confianza", "z", "p", "error e", "n0", "n", "k (sistemático)"),
                      valor = c(N, "95 %", z, p, e, round(n0, 1), n, k))
dir.create("R/salidas", showWarnings = FALSE)
libro <- createWorkbook()
addWorksheet(libro, "Tamano de muestra");    writeData(libro, "Tamano de muestra", resumen)
addWorksheet(libro, "Afijacion");            writeData(libro, "Afijacion", tabla_afijacion)
addWorksheet(libro, "Comparacion estratos"); writeData(libro, "Comparacion estratos", comp_estratos)
addWorksheet(libro, "Comparacion medias");   writeData(libro, "Comparacion medias", comp_medias)
addWorksheet(libro, "500 repeticiones");     writeData(libro, "500 repeticiones", comp_repeticiones)
saveWorkbook(libro, "R/salidas/Muestreo.xlsx", overwrite = TRUE)

# Tablas para la página web
dir.create("docs/data/tdf", recursive = TRUE, showWarnings = FALSE)
write.csv(resumen, "docs/data/tdf/muestreo_tamano.csv", row.names = FALSE, fileEncoding = "UTF-8")
write.csv(tabla_afijacion, "docs/data/tdf/muestreo_afijacion.csv", row.names = FALSE, fileEncoding = "UTF-8")
write.csv(comp_estratos, "docs/data/tdf/muestreo_estratos.csv", row.names = FALSE, fileEncoding = "UTF-8")
write.csv(comp_medias, "docs/data/tdf/muestreo_medias.csv", row.names = FALSE, fileEncoding = "UTF-8")
write.csv(comp_repeticiones, "docs/data/tdf/muestreo_repeticiones.csv", row.names = FALSE, fileEncoding = "UTF-8")
