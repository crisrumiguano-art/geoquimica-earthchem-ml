# Variables cuantitativas continuas: TDF, gráficas, outliers e indicadores (Lecciones 5 y 6).
# Ejecutar desde la raíz del repositorio:  Rscript R/03_continuas.R
#
# Para cada variable:
#   1. Número de intervalos según las reglas del curso.
#   2. TDF "por defecto" (plantilla: Sturges sobre el rango completo, a = R / k) -> muestra el problema.
#   3. Outliers por la regla intercuartílica, y de qué rocas son (¿errores o rocas reales?).
#   4. TDF corregida: intervalos cerrados sobre el rango típico (límites IQR), amplitud redonda y
#      dos clases abiertas para los extremos. No se borra ningún dato.
#   5. Lo mismo dentro de un estrato homogéneo (rocas volcánicas máficas).
#   6. Error de agrupación e indicadores.
# El razonamiento completo está en R/analisis_agrupacion_outliers.md.

source("R/funciones.R")
base <- leer_base()

ESTRATO <- "igneous:volcanic:mafic"   # basaltos y afines, el grupo más grande de la base

VARIABLES <- list(
  list(col = "SiO2 (wt%)", nombre = "SiO2", unidad = "wt%", log = FALSE),
  list(col = "MgO (wt%)",  nombre = "MgO",  unidad = "wt%", log = FALSE),
  # Cr: cola extrema (cromititas de hasta 29,5 %). Se analiza en log10, donde es casi simétrica.
  list(col = "Cr (ppm)",   nombre = "Cr",   unidad = "ppm", log = TRUE)
)

libro <- createWorkbook()
n_graf <- 1

for (v in VARIABLES) {
  tiene <- !is.na(base[[v$col]])
  x <- base[[v$col]][tiene]
  tipo <- base[["Sample Type"]][tiene]
  esc <- if (v$log) log10(x) else x                     # escala de análisis
  unidad <- if (v$log) paste("log10", v$unidad) else v$unidad
  nombre <- if (v$log) paste("log10", v$nombre) else v$nombre
  cat("\n==========", v$col, "==========\n")
  cat("n =", length(x), " | rango:", min(x), "-", max(x), "\n")

  reglas <- reglas_k(length(x))
  print(reglas)

  # Por defecto (como la plantilla, en la escala original)
  tdf_def <- tdf_continua(x, redondear = FALSE)
  cat(sprintf("Por defecto: k = %d, a = %.4g; el intervalo más poblado concentra el %.1f %% de los datos\n",
              nrow(tdf_def), tdf_def$Ls[1] - tdf_def$Li[1], max(tdf_def$hi)))

  # Outliers y de qué rocas son
  lim <- limites_iqr(esc)
  es_out <- esc < lim["inferior"] | esc > lim["superior"]
  lim_orig <- if (v$log) 10^lim else lim
  cat(sprintf("Límites IQR: [%.4g ; %.4g] %s -> %d outliers (%.1f %%)\n", lim_orig[1], lim_orig[2], v$unidad,
              sum(es_out), mean(es_out) * 100))
  rocas_out <- sort(table(tipo[es_out]), decreasing = TRUE)
  print(head(rocas_out, 5))

  # TDF corregida, toda la muestra
  tdf_todo <- tdf_continua(esc, lim = lim)
  err_todo <- error_agrupacion(esc, tdf_todo)
  cat(sprintf("Corregida: %d clases cerradas de amplitud %g + abiertas\n", sum(!is.na(tdf_todo$MC)),
              tdf_todo$Ls[!is.na(tdf_todo$MC)][1] - tdf_todo$Li[!is.na(tdf_todo$MC)][1]))
  print(tdf_todo)
  print(err_todo)

  # Estrato homogéneo
  ee <- esc[tipo == ESTRATO]
  lim_e <- limites_iqr(ee)
  pct_e <- mean(ee < lim_e["inferior"] | ee > lim_e["superior"]) * 100
  tdf_est <- tdf_continua(ee, lim = lim_e)
  err_est <- error_agrupacion(ee, tdf_est)
  cat(sprintf("Estrato %s: n = %d, outliers %.1f %%\n", ESTRATO, length(ee), pct_e))
  print(tdf_est)
  print(err_est)

  ind <- data.frame(indicador = indicadores(x)$indicador, toda_la_muestra = indicadores(x)$valor,
                    rocas_volcanicas_maficas = indicadores(x[tipo == ESTRATO])$valor)
  if (v$log) ind$log10_toda_la_muestra <- indicadores(esc)$valor
  print(ind, digits = 4)

  # Gráficas
  comparar_agrupacion(tdf_def, tdf_todo, v$nombre, unidad, paste0(v$nombre, "_agrupacion.png"))
  graficos_continua(esc, tdf_todo, nombre, v$unidad, paste0(v$nombre, "_toda_la_muestra.png"), n_graf)
  graficos_continua(ee, tdf_est, paste(nombre, "en rocas volcánicas máficas"), v$unidad,
                    paste0(v$nombre, "_estrato_mafico.png"), n_graf + 3)
  n_graf <- n_graf + 6

  # Excel: una hoja por variable con las tablas apiladas
  hoja <- v$nombre
  addWorksheet(libro, hoja)
  fila <- 1
  bloque <- function(titulo, tabla) {
    writeData(libro, hoja, titulo, startRow = fila)
    writeData(libro, hoja, tabla, startRow = fila + 1)
    fila <<- fila + nrow(tabla) + 4
  }
  bloque("Número de intervalos según cada regla", reglas)
  bloque("TDF por defecto (Sturges sobre el rango completo, a = R/k)", cbind(intervalo = etiquetas(tdf_def, 3), tdf_def))
  bloque(sprintf("Outliers IQR: %d de %d (%.1f %%), por tipo de roca", sum(es_out), length(x), mean(es_out) * 100),
         data.frame(tipo_de_roca = names(rocas_out), ni = as.vector(rocas_out)))
  bloque(paste0("TDF corregida, toda la muestra (", unidad, "): rango IQR + clases abiertas"),
         cbind(intervalo = etiquetas(tdf_todo), tdf_todo))
  bloque("Error de agrupación (toda la muestra, clases cerradas)", err_todo)
  bloque(paste0("TDF corregida, rocas volcánicas máficas (", unidad, ")"), cbind(intervalo = etiquetas(tdf_est), tdf_est))
  bloque("Error de agrupación (rocas volcánicas máficas)", err_est)
  bloque("Indicadores", ind)
}

saveWorkbook(libro, file.path(SALIDAS, "TDF_continuas.xlsx"), overwrite = TRUE)
cat("\nSalidas en", SALIDAS, "\n")
