# VARIABLES DISCRETAS: TDF agrupada, gráficas e indicadores (Lecciones 5 y 6).
# Correr desde la carpeta del repositorio:  Rscript R/02_discretas.R
# Tienen muchos valores distintos (75 años, 76 conteos): se agrupan en intervalos como una continua.

source("R/funciones.R")   # carga las funciones del proyecto
base <- leer_base()       # lee la base completa

# Variables a analizar: columna, nombre para títulos, unidad, nombre de archivo
CASOS <- list(
  list(col = "Publication Year", nombre = "Año de publicación", unidad = "año", archivo = "anio"),
  list(col = "N Analytes", nombre = "Número de analitos", unidad = "analitos", archivo = "analitos")
)

libro <- createWorkbook()   # Excel vacío
n_graf <- 1                 # número de la próxima gráfica
for (c in CASOS) {          # repite para cada variable
  x <- base[[c$col]]        # saca la columna
  x <- x[!is.na(x)]         # quita vacíos
  cat("\n==========", c$nombre, "==========\n")
  cat("Valores distintos:", length(unique(x)), "\n")   # cuántos valores diferentes hay
  lim <- limites_iqr(x)                                # límites de outliers (regla IQR)
  out <- x < lim["inferior"] | x > lim["superior"]     # TRUE = es outlier
  cat(sprintf("Límites IQR: [%g ; %g] -> %d outliers (%.1f %%)\n", lim[1], lim[2], sum(out), mean(out) * 100))
  tdf <- tdf_continua(x)   # TDF con todos los datos (aquí los outliers no deforman los intervalos)
  print(tdf)
  ind <- indicadores(x)                                # media, mediana, s, CV, asimetría...
  moda <- as.numeric(names(which.max(table(x))))       # moda: el valor que más se repite
  ind <- rbind(ind, data.frame(indicador = "Moda", valor = moda))  # rbind: agrega una fila
  print(ind, digits = 6)
  graficos_continua(x, tdf, c$nombre, c$unidad, paste0("disc_", c$archivo, ".png"), n_graf)  # histograma, ojiva, caja
  n_graf <- n_graf + 3                                 # se usaron 3 números de gráfica
  tabla_web(cbind(intervalo = etiquetas(tdf, 0), tdf), paste0("disc_", c$archivo))  # cbind: agrega columna "intervalo"
  tabla_web(ind, paste0("disc_", c$archivo, "_indicadores"))
  addWorksheet(libro, c$archivo)                       # hoja nueva en el Excel
  writeData(libro, c$archivo, cbind(intervalo = etiquetas(tdf, 0), tdf))  # TDF
  writeData(libro, c$archivo, ind, startRow = nrow(tdf) + 4)               # indicadores debajo
}
saveWorkbook(libro, file.path(SALIDAS, "TDF_discretas.xlsx"), overwrite = TRUE)  # guarda el Excel
