# Variables cuantitativas discretas: TDF agrupada, gráficas e indicadores (Lecciones 5 y 6).
# Ejecutar desde la raíz del repositorio:  Rscript R/02_discretas.R
# Las dos discretas tienen muchos valores distintos (75 años, 76 conteos), así que se agrupan en
# intervalos como una continua, con k de Sturges y amplitud redonda.

# Carga las funciones del curso y la base (ver funciones.R).
source("R/funciones.R")
base <- leer_base()

# Variables discretas a analizar: columna de la base, nombre para los títulos, unidad y nombre de archivo.
CASOS <- list(
  list(col = "Publication Year", nombre = "Año de publicación", unidad = "año", archivo = "anio"),
  list(col = "N Analytes", nombre = "Número de analitos", unidad = "analitos", archivo = "analitos")
)

libro <- createWorkbook()
n_graf <- 1
for (c in CASOS) {
  x <- base[[c$col]]
  # Solo los valores medidos: !is.na() es "no es vacío".
  x <- x[!is.na(x)]
  cat("\n==========", c$nombre, "==========\n")
  # unique() deja un valor de cada uno: con muchos valores distintos conviene agrupar en intervalos.
  cat("Valores distintos:", length(unique(x)), "\n")
  # Outliers por la regla intercuartílica: out es TRUE para cada dato fuera de [Q1 - 1,5·IR ; Q3 + 1,5·IR].
  # sum(out) cuenta los TRUE y mean(out) da la proporción.
  lim <- limites_iqr(x)
  out <- x < lim["inferior"] | x > lim["superior"]
  cat(sprintf("Límites IQR: [%g ; %g] -> %d outliers (%.1f %%)\n", lim[1], lim[2], sum(out), mean(out) * 100))
  tdf <- tdf_continua(x)   # todos los datos: los outliers de estas variables no deforman los intervalos
  print(tdf)
  # Indicadores con todos los datos. La moda se agrega aparte: el valor que más se repite (table + which.max).
  ind <- indicadores(x)
  moda <- as.numeric(names(which.max(table(x))))
  ind <- rbind(ind, data.frame(indicador = "Moda", valor = moda))
  print(ind, digits = 6)
  # Histograma + polígono, ojiva y diagrama de caja en un PNG (ver graficos_continua en funciones.R).
  graficos_continua(x, tdf, c$nombre, c$unidad, paste0("disc_", c$archivo, ".png"), n_graf)
  n_graf <- n_graf + 3
  # cbind() pega columnas: agrega a la TDF una columna con el texto del intervalo, p. ej. "[2000-2010[".
  tabla_web(cbind(intervalo = etiquetas(tdf, 0), tdf), paste0("disc_", c$archivo))
  tabla_web(ind, paste0("disc_", c$archivo, "_indicadores"))
  addWorksheet(libro, c$archivo)
  writeData(libro, c$archivo, cbind(intervalo = etiquetas(tdf, 0), tdf))
  writeData(libro, c$archivo, ind, startRow = nrow(tdf) + 4)
}
saveWorkbook(libro, file.path(SALIDAS, "TDF_discretas.xlsx"), overwrite = TRUE)
