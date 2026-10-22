# Muestreo probabilístico (Lección 3): aleatorio simple, sistemático y estratificado sobre la base PetDB.
# Ejecutar desde la raíz del repositorio:  Rscript R/04_muestreo.R
# La base completa (N = 159 760) es el marco muestral. Se extraen tres muestras del mismo tamaño n y se comparan
# con la población; después se repite cada método 500 veces para ver cuál estima mejor la media.

source("R/funciones.R")
base <- leer_base()
set.seed(2026)  # misma semilla = mismas muestras cada vez que se corre

N <- nrow(base)
# Estratos: ambiente tectónico agrupado; las 304 filas sin ambiente forman su propio estrato.
estrato <- base[["Tectonic Group"]]
estrato[is.na(estrato) | estrato == ""] <- "sin dato"
base$Estrato <- estrato

# ------------------------------------------------------------ tamaño de muestra
# n0 = z^2 p q / e^2 y corrección por población finita n = n0 / (1 + (n0 - 1) / N).
# p = q = 0,5 (la peor varianza posible), 95 % de confianza (z = 1,96), error e = 3 %.
z <- 1.96; p <- 0.5; e <- 0.03
n0 <- z^2 * p * (1 - p) / e^2
n <- ceiling(n0 / (1 + (n0 - 1) / N))
cat("N =", N, " n0 =", round(n0, 1), " n =", n, "\n")

# ------------------------------------------------------------ los tres métodos
aleatorio <- function() sample(N, n)  # sorteo sin reposición: todas las filas con la misma chance

sistematico <- function() {
  k <- floor(N / n)        # intervalo de selección
  i <- sample(k, 1)        # arranque aleatorio entre 1 y k
  i + (0:(n - 1)) * k      # i, i+k, i+2k, ..., i+(n-1)k
}

afijacion <- function() {
  # Afijación proporcional: n_h = n * N_h / N, redondeada por restos mayores para que sume n exacto.
  Nh <- table(base$Estrato)
  bruto <- n * Nh / N
  nh <- floor(bruto)
  falta <- n - sum(nh)
  nh[order(bruto - nh, decreasing = TRUE)[seq_len(falta)]] <- nh[order(bruto - nh, decreasing = TRUE)[seq_len(falta)]] + 1
  nh
}
NH <- afijacion()

estratificado <- function() {
  # Muestreo aleatorio simple dentro de cada estrato, con el tamaño que le toca.
  unlist(lapply(names(NH), function(h) {
    filas <- which(base$Estrato == h)
    filas[sample(length(filas), NH[[h]])]
  }), use.names = FALSE)
}

k <- floor(N / n)
muestras <- list(aleatoria = aleatorio(), sistematica = sistematico(), estratificada = estratificado())
stopifnot(all(lengths(muestras) == n))

# ------------------------------------------------------------ tabla de afijación
tabla_afijacion <- data.frame(estrato = names(NH), N_h = as.vector(table(base$Estrato)[names(NH)]),
                              peso = round(as.vector(table(base$Estrato)[names(NH)]) / N * 100, 2),
                              n_h = as.vector(NH))
print(tabla_afijacion)

# ------------------------------------------------------------ comparación con la población
pct <- function(filas) round(prop.table(table(factor(base$Estrato[filas], levels = names(NH)))) * 100, 2)
comp_estratos <- data.frame(estrato = names(NH), poblacion = as.vector(pct(seq_len(N))),
                            aleatoria = as.vector(pct(muestras$aleatoria)),
                            sistematica = as.vector(pct(muestras$sistematica)),
                            estratificada = as.vector(pct(muestras$estratificada)))
print(comp_estratos)

VARIABLES <- c("SiO2 (wt%)", "MgO (wt%)", "Publication Year")
media <- function(v, filas) mean(base[[v]][filas], na.rm = TRUE)
comp_medias <- do.call(rbind, lapply(VARIABLES, function(v) data.frame(
  variable = v, poblacion = round(media(v, seq_len(N)), 3),
  aleatoria = round(media(v, muestras$aleatoria), 3), sistematica = round(media(v, muestras$sistematica), 3),
  estratificada = round(media(v, muestras$estratificada), 3),
  n_con_dato_estratificada = sum(!is.na(base[[v]][muestras$estratificada])))))
print(comp_medias)

# ------------------------------------------------------------ 500 repeticiones: ¿qué método es más preciso?
# Si se repite el muestreo, la media muestral cambia. Su desviación estándar (error estándar) mide la precisión.
R <- 500
sio2 <- base[["SiO2 (wt%)"]]
sim <- sapply(list(aleatoria = aleatorio, sistematica = sistematico, estratificada = estratificado),
              function(f) replicate(R, mean(sio2[f()], na.rm = TRUE)))
comp_repeticiones <- data.frame(metodo = colnames(sim), media_de_las_medias = round(colMeans(sim), 3),
                                error_estandar = round(apply(sim, 2, sd), 4),
                                sesgo = round(colMeans(sim) - mean(sio2, na.rm = TRUE), 4))
print(comp_repeticiones)

# ------------------------------------------------------------ gráficos
png(file.path(GRAFICOS, "muestreo_estratos.png"), width = 1100, height = 650, res = 130)
m <- t(as.matrix(comp_estratos[, -1])); colnames(m) <- comp_estratos$estrato
barplot(m, beside = TRUE, col = c("gray25", "gray55", "gray75", "gray90"), ylim = c(0, max(m) * 1.2),
        main = "Gráfica No. 1: Porcentaje por ambiente tectónico, población y muestras",
        ylab = "Porcentaje (%)", cex.names = 0.8, legend.text = TRUE,
        args.legend = list(x = "topright", bty = "n", cex = 0.8))
dev.off()

png(file.path(GRAFICOS, "muestreo_repeticiones.png"), width = 1100, height = 650, res = 130)
boxplot(sim, col = c("gray55", "gray75", "gray90"), ylab = "Media de SiO2 (wt%)",
        main = paste0("Gráfica No. 2: Media de SiO2 en ", R, " muestras de cada método (n = ", n, ")"))
abline(h = mean(sio2, na.rm = TRUE), lty = 2)
legend("topright", "media poblacional", lty = 2, bty = "n", cex = 0.8)
dev.off()

# ------------------------------------------------------------ salidas
dir.create("data/muestras", showWarnings = FALSE)
for (nombre in names(muestras)) {
  write.csv(base[muestras[[nombre]], ], file.path("data/muestras", paste0("muestra_", nombre, ".csv")),
            row.names = FALSE, fileEncoding = "UTF-8")
}
resumen <- data.frame(dato = c("N (población)", "confianza", "z", "p", "error e", "n0", "n", "k (sistemático)"),
                      valor = c(N, "95 %", z, p, e, round(n0, 1), n, k))
libro <- createWorkbook()
for (h in list(list("Tamano de muestra", resumen), list("Afijacion", tabla_afijacion),
               list("Comparacion estratos", comp_estratos), list("Comparacion medias", comp_medias),
               list("500 repeticiones", comp_repeticiones))) {
  addWorksheet(libro, h[[1]]); writeData(libro, h[[1]], h[[2]])
}
saveWorkbook(libro, file.path(SALIDAS, "Muestreo.xlsx"), overwrite = TRUE)
for (h in list(list("muestreo_tamano", resumen), list("muestreo_afijacion", tabla_afijacion),
               list("muestreo_estratos", comp_estratos), list("muestreo_medias", comp_medias),
               list("muestreo_repeticiones", comp_repeticiones))) tabla_web(h[[2]], h[[1]])
cat("Listo: R/salidas/Muestreo.xlsx, data/muestras/*.csv, docs/img/r/muestreo_*.png\n")
