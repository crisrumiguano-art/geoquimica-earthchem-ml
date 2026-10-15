# Variables cuantitativas discretas: TDF agrupada, gráficas e indicadores (Lecciones 5 y 6).
# Ejecutar desde la raíz del repositorio:  Rscript R/02_discretas.R
# Las dos discretas tienen muchos valores distintos (75 años, 76 conteos), así que se agrupan en
# intervalos como una continua, con k de Sturges y amplitud redonda.

source("R/funciones.R")
base <- leer_base()

CASOS <- list(
  list(col = "Publication Year", nombre = "Año de publicación", unidad = "año", archivo = "anio"),
  list(col = "N Analytes", nombre = "Número de analitos", unidad = "analitos", archivo = "analitos")
)

libro <- createWorkbook()
n_graf <- 1
for (c in CASOS) {
  x <- base[[c$col]]
  x <- x[!is.na(x)]
  cat("\n==========", c$nombre, "==========\n")
  cat("Valores distintos:", length(unique(x)), "\n")
  lim <- limites_iqr(x)
  out <- x < lim["inferior"] | x > lim["superior"]
  cat(sprintf("Límites IQR: [%g ; %g] -> %d outliers (%.1f %%)\n", lim[1], lim[2], sum(out), mean(out) * 100))
  tdf <- tdf_continua(x)   # todos los datos: los outliers de estas variables no deforman los intervalos
  print(tdf)
  ind <- indicadores(x)
  moda <- as.numeric(names(which.max(table(x))))
  ind <- rbind(ind, data.frame(indicador = "Moda", valor = moda))
  print(ind, digits = 6)
  graficos_continua(x, tdf, c$nombre, c$unidad, paste0("disc_", c$archivo, ".png"), n_graf)
  n_graf <- n_graf + 3
  tabla_web(cbind(intervalo = etiquetas(tdf, 0), tdf), paste0("disc_", c$archivo))
  tabla_web(ind, paste0("disc_", c$archivo, "_indicadores"))
  addWorksheet(libro, c$archivo)
  writeData(libro, c$archivo, cbind(intervalo = etiquetas(tdf, 0), tdf))
  writeData(libro, c$archivo, ind, startRow = nrow(tdf) + 4)
}
saveWorkbook(libro, file.path(SALIDAS, "TDF_discretas.xlsx"), overwrite = TRUE)
