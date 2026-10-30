# Variables cualitativas: TDF, diagrama de barras y diagrama circular (Lección 5).
# Ejecutar desde la raíz del repositorio:  Rscript R/01_cualitativas.R
# Nominales: solo ni y hi (las acumuladas no tienen sentido sin orden).
# Ordinales: además Ni y Hi acumuladas, en el orden natural de las categorías.

# source() ejecuta otro archivo: carga las funciones del curso (tdf_cualitativa, graficos_cualitativa...).
# leer_base() devuelve la base completa como data.frame (filas = análisis, columnas = variables).
source("R/funciones.R")
base <- leer_base()

# Tipo de roca: 27 categorías; las de menos de 1 % se agrupan en "otros" para que el gráfico sea legible.
# base[["columna"]] extrae una columna como vector. prop.table(table()) da la proporción de cada categoría;
# las que están por debajo de 0,01 (1 %) se reemplazan por "otros" con %in% ("está dentro de").
tipo <- base[["Sample Type"]]
frec <- prop.table(table(tipo))
tipo[tipo %in% names(frec[frec < 0.01])] <- "otros"

# CASOS es una lista de variables a analizar. Cada caso dice: los datos (x), el título, el nombre de la hoja de
# Excel y, si es ordinal, el orden de sus categorías (orden = NULL significa nominal).
# factor(..., labels = ...) cambia los códigos 0-5 del grado de alteración por su nombre.
CASOS <- list(
  list(x = base[["Tectonic Group"]], titulo = "Ambiente tectónico agrupado", hoja = "Grupo tectonico", orden = NULL),
  list(x = tipo, titulo = "Tipo de roca", hoja = "Tipo de roca", orden = NULL),
  list(x = base[["SiO2 Class"]], titulo = "Clase de roca según SiO2", hoja = "Clase SiO2",
       orden = c("ultrabasica", "basica", "intermedia", "acida")),
  list(x = factor(base[["Alteration Grade"]], levels = 0:5,
                  labels = c("0 fresca", "1 leve", "2 moderada", "3 extensa", "4 casi total", "5 total")),
       titulo = "Grado de alteración", hoja = "Alteracion",
       orden = c("0 fresca", "1 leve", "2 moderada", "3 extensa", "4 casi total", "5 total"))
)

# Libro de Excel vacío (paquete openxlsx): cada variable se agrega como una hoja.
# n_graf numera las gráficas en orden (Gráfica No. 1, 2, 3...).
libro <- createWorkbook()
n_graf <- 1
# Bucle: repite el mismo procedimiento para cada caso de la lista.
for (c in CASOS) {
  # TDF de la variable (ver tdf_cualitativa en funciones.R). as.character() asegura que sean textos.
  tdf <- tdf_cualitativa(as.character(c$x), c$orden)
  cat("\n==========", c$titulo, if (is.null(c$orden)) "(nominal)" else "(ordinal)", "==========\n")
  print(tdf)
  if (!is.null(c$orden)) {
    # Mediana de una ordinal: la categoría donde Hi_asc alcanza el 50 %.
    cat("Mediana:", tdf$categoria[which(tdf$Hi_asc >= 50)[1]], "\n")
  }
  # Moda = la categoría con mayor ni. which.max() da la posición del valor más grande.
  cat("Moda:", tdf$categoria[which.max(tdf$ni)], "\n")
  # Dibuja barras + circular y las guarda en docs/img/r/. El nombre del archivo sale de la hoja: tolower() pasa a
  # minúsculas y gsub(" ", "_", ...) cambia espacios por guion bajo: "Clase SiO2" -> cual_clase_sio2.png.
  graficos_cualitativa(tdf, c$titulo, paste0("cual_", gsub(" ", "_", tolower(c$hoja)), ".png"), n_graf)
  n_graf <- n_graf + 2
  # Guarda la TDF en una hoja del Excel y como CSV para la web.
  addWorksheet(libro, c$hoja)
  writeData(libro, c$hoja, tdf)
  tabla_web(tdf, paste0("cual_", gsub(" ", "_", tolower(c$hoja))))
}
saveWorkbook(libro, file.path(SALIDAS, "TDF_cualitativas.xlsx"), overwrite = TRUE)
