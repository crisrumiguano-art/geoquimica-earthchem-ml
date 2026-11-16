# VARIABLES CUALITATIVAS: tabla de frecuencias (TDF), barras y circular (Lección 5).
# Correr desde la carpeta del repositorio:  Rscript R/01_cualitativas.R
# Nominal = sin orden: solo ni y hi.   Ordinal = con orden: además Ni y Hi acumuladas.

source("R/funciones.R")   # carga las funciones del proyecto
base <- leer_base()       # lee la base completa (tabla)

# Tipo de roca: las categorías con menos de 1 % se juntan en "otros" (gráfico legible)
tipo <- base[["Sample Type"]]                       # saca la columna
frec <- prop.table(table(tipo))                     # proporción de cada categoría
tipo[tipo %in% names(frec[frec < 0.01])] <- "otros" # las de < 1 % pasan a "otros"

# Nombres en español (con tildes) para tablas y gráficos; la base guarda los originales de PetDB
en_espanol <- function(x, nombres) { x <- as.character(x); cambia <- x %in% names(nombres); x[cambia] <- nombres[x[cambia]]; x }
tipo <- en_espanol(tipo, c("igneous:volcanic:mafic" = "volcánica máfica", "igneous:plutonic:ultramafic" = "plutónica ultramáfica",
        "igneous:volcanic:clastic" = "volcanoclástica", "igneous:volcanic:intermediate" = "volcánica intermedia",
        "igneous:plutonic:mafic" = "plutónica máfica", "xenolith" = "xenolito", "metamorphic" = "metamórfica",
        "igneous:volcanic:felsic" = "volcánica félsica"))

# Lista de variables a analizar: datos (x), título, hoja de Excel y orden (NULL = nominal)
CASOS <- list(
  list(x = en_espanol(base[["Tectonic Group"]], c("dorsal y corteza oceanica" = "dorsal y corteza oceánica")),
       titulo = "Ambiente tectónico agrupado", hoja = "Grupo tectonico", orden = NULL),
  list(x = tipo, titulo = "Tipo de roca", hoja = "Tipo de roca", orden = NULL),
  list(x = en_espanol(base[["SiO2 Class"]], c(ultrabasica = "ultrabásica", basica = "básica", intermedia = "intermedia", acida = "ácida")),
       titulo = "Clase de roca según SiO2", hoja = "Clase SiO2",
       orden = c("ultrabásica", "básica", "intermedia", "ácida")),           # ordinal: su orden
  list(x = factor(base[["Alteration Grade"]], levels = 0:5,                  # factor: códigos 0-5 -> nombres
                  labels = c("fresca", "leve", "moderada", "extensa", "casi total", "total")),
       titulo = "Grado de alteración", hoja = "Alteracion",
       orden = c("fresca", "leve", "moderada", "extensa", "casi total", "total"))
)

libro <- createWorkbook()   # Excel vacío
n_graf <- 1                 # número de la próxima gráfica
for (c in CASOS) {          # repite para cada variable
  tdf <- tdf_cualitativa(as.character(c$x), c$orden)   # TDF (ver funciones.R)
  cat("\n==========", c$titulo, if (is.null(c$orden)) "(nominal)" else "(ordinal)", "==========\n")
  print(tdf)                                           # muestra la tabla en la consola
  if (!is.null(c$orden)) {
    cat("Mediana:", tdf$categoria[which(tdf$Hi_asc >= 50)[1]], "\n")  # mediana: donde Hi llega a 50 %
  }
  cat("Moda:", tdf$categoria[which.max(tdf$ni)], "\n")                # moda: la de mayor ni
  graficos_cualitativa(tdf, c$titulo, paste0("cual_", gsub(" ", "_", tolower(c$hoja)), ".png"), n_graf)  # barras + circular
  n_graf <- n_graf + 2                                 # se usaron 2 números de gráfica
  addWorksheet(libro, c$hoja)                          # hoja nueva en el Excel
  writeData(libro, c$hoja, tdf)                        # escribe la TDF
  tabla_web(tdf, paste0("cual_", gsub(" ", "_", tolower(c$hoja))))   # CSV para la web
}
saveWorkbook(libro, file.path(SALIDAS, "TDF_cualitativas.xlsx"), overwrite = TRUE)  # guarda el Excel
