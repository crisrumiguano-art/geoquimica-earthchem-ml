# Variables cualitativas: TDF, diagrama de barras y diagrama circular (Lección 5).
# Ejecutar desde la raíz del repositorio:  Rscript R/01_cualitativas.R
# Nominales: solo ni y hi (las acumuladas no tienen sentido sin orden).
# Ordinales: además Ni y Hi acumuladas, en el orden natural de las categorías.

source("R/funciones.R")
base <- leer_base()

# Tipo de roca: 27 categorías; las de menos de 1 % se agrupan en "otros" para que el gráfico sea legible.
tipo <- base[["Sample Type"]]
frec <- prop.table(table(tipo))
tipo[tipo %in% names(frec[frec < 0.01])] <- "otros"

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

libro <- createWorkbook()
n_graf <- 1
for (c in CASOS) {
  tdf <- tdf_cualitativa(as.character(c$x), c$orden)
  cat("\n==========", c$titulo, if (is.null(c$orden)) "(nominal)" else "(ordinal)", "==========\n")
  print(tdf)
  if (!is.null(c$orden)) {
    # Mediana de una ordinal: la categoría donde Hi_asc alcanza el 50 %.
    cat("Mediana:", tdf$categoria[which(tdf$Hi_asc >= 50)[1]], "\n")
  }
  cat("Moda:", tdf$categoria[which.max(tdf$ni)], "\n")
  graficos_cualitativa(tdf, c$titulo, paste0("cual_", gsub(" ", "_", tolower(c$hoja)), ".png"), n_graf)
  n_graf <- n_graf + 2
  addWorksheet(libro, c$hoja)
  writeData(libro, c$hoja, tdf)
  tabla_web(tdf, paste0("cual_", gsub(" ", "_", tolower(c$hoja))))
}
saveWorkbook(libro, file.path(SALIDAS, "TDF_cualitativas.xlsx"), overwrite = TRUE)
