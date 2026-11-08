# VARIABLES CONTINUAS: TDF, gráficas, outliers e indicadores (Lecciones 5 y 6).
# Correr desde la carpeta del repositorio:  Rscript R/03_continuas.R
#
# Pasos para cada variable:
#   1. Cuántos intervalos (reglas del curso).
#   2. TDF "por defecto" (como la plantilla) -> muestra el problema.
#   3. Outliers (regla IQR) y de qué rocas son.
#   4. TDF corregida: intervalos sobre el rango típico + 2 clases abiertas. No se borra ningún dato.
#   5. Lo mismo en un grupo homogéneo (rocas volcánicas máficas).
#   6. Error de agrupación e indicadores.
# Explicación completa: R/analisis_agrupacion_outliers.md

source("R/funciones.R")   # carga las funciones del proyecto
base <- leer_base()       # lee la base completa

ESTRATO <- "igneous:volcanic:mafic"   # grupo homogéneo: basaltos y afines

# Variables a analizar: columna, nombre corto, unidad, ¿usar logaritmo?
VARIABLES <- list(
  list(col = "SiO2 (wt%)", nombre = "SiO2", unidad = "wt%", log = FALSE),
  list(col = "MgO (wt%)",  nombre = "MgO",  unidad = "wt%", log = FALSE),
  # Cr: valores extremos (hasta 29,5 %): se analiza en log10, donde es casi simétrica
  list(col = "Cr (ppm)",   nombre = "Cr",   unidad = "ppm", log = TRUE)
)

libro <- createWorkbook()   # Excel vacío
n_graf <- 1                 # número de la próxima gráfica

for (v in VARIABLES) {                       # repite para cada variable
  tiene <- !is.na(base[[v$col]])             # TRUE = la fila tiene dato
  x <- base[[v$col]][tiene]                  # valores de la variable
  tipo <- base[["Sample Type"]][tiene]       # tipo de roca de cada valor
  esc <- if (v$log) log10(x) else x                     # escala de análisis (log10: 10, 100, 1000 -> 1, 2, 3)
  unidad <- if (v$log) paste("log10", v$unidad) else v$unidad
  nombre <- if (v$log) paste("log10", v$nombre) else v$nombre
  cat("\n==========", v$col, "==========\n")
  cat("n =", length(x), " | rango:", min(x), "-", max(x), "\n")

  # Paso 1: número de intervalos según cada regla
  reglas <- reglas_k(length(x))
  print(reglas)

  # Paso 2: TDF por defecto (como la plantilla: Sturges sobre todo el rango)
  tdf_def <- tdf_continua(x, redondear = FALSE)
  cat(sprintf("Por defecto: k = %d, a = %.4g; el intervalo más poblado concentra el %.1f %% de los datos\n",
              nrow(tdf_def), tdf_def$Ls[1] - tdf_def$Li[1], max(tdf_def$hi)))

  # Paso 3: outliers y de qué rocas son (rocas reales -> no se borran)
  lim <- limites_iqr(esc)                                # límites IQR
  es_out <- esc < lim["inferior"] | esc > lim["superior"] # TRUE = outlier
  lim_orig <- if (v$log) 10^lim else lim                 # límites en la unidad original
  cat(sprintf("Límites IQR: [%.4g ; %.4g] %s -> %d outliers (%.1f %%)\n", lim_orig[1], lim_orig[2], v$unidad,
              sum(es_out), mean(es_out) * 100))
  rocas_out <- sort(table(tipo[es_out]), decreasing = TRUE)  # outliers por tipo de roca
  print(head(rocas_out, 5))                                  # los 5 tipos más frecuentes

  # Paso 4: TDF corregida (intervalos en el rango típico + clases abiertas) y su error
  tdf_todo <- tdf_continua(esc, lim = lim)
  err_todo <- error_agrupacion(esc, tdf_todo)
  cat(sprintf("Corregida: %d clases cerradas de amplitud %g + abiertas\n", sum(!is.na(tdf_todo$MC)),
              tdf_todo$Ls[!is.na(tdf_todo$MC)][1] - tdf_todo$Li[!is.na(tdf_todo$MC)][1]))
  print(tdf_todo)
  print(err_todo)

  # Paso 5: lo mismo solo con rocas volcánicas máficas (grupo homogéneo)
  ee <- esc[tipo == ESTRATO]                             # valores de ese grupo
  lim_e <- limites_iqr(ee)
  pct_e <- mean(ee < lim_e["inferior"] | ee > lim_e["superior"]) * 100  # % de outliers en el grupo
  tdf_est <- tdf_continua(ee, lim = lim_e)
  err_est <- error_agrupacion(ee, tdf_est)
  cat(sprintf("Estrato %s: n = %d, outliers %.1f %%\n", ESTRATO, length(ee), pct_e))
  print(tdf_est)
  print(err_est)

  # Paso 6: indicadores de toda la muestra y del grupo, lado a lado
  ind <- data.frame(indicador = indicadores(x)$indicador, toda_la_muestra = indicadores(x)$valor,
                    rocas_volcanicas_maficas = indicadores(x[tipo == ESTRATO])$valor)
  if (v$log) ind$log10_toda_la_muestra <- indicadores(esc)$valor   # y en log10 si corresponde
  print(ind, digits = 4)

  # Gráficas (PNG en docs/img/r/)
  comparar_agrupacion(tdf_def, tdf_todo, v$nombre, unidad, paste0(v$nombre, "_agrupacion.png"))       # por defecto vs corregida
  graficos_continua(esc, tdf_todo, nombre, v$unidad, paste0(v$nombre, "_toda_la_muestra.png"), n_graf) # toda la muestra
  graficos_continua(ee, tdf_est, paste(nombre, "en rocas volcánicas máficas"), v$unidad,               # solo el grupo
                    paste0(v$nombre, "_estrato_mafico.png"), n_graf + 3)
  n_graf <- n_graf + 6                                   # se usaron 6 números de gráfica

  # Tablas para la web (CSV)
  tabla_web(cbind(intervalo = etiquetas(tdf_todo), tdf_todo), paste0("cont_", v$nombre))
  tabla_web(cbind(intervalo = etiquetas(tdf_est), tdf_est), paste0("cont_", v$nombre, "_estrato"))
  tabla_web(rbind(cbind(muestra = "toda", err_todo), cbind(muestra = "volcanicas maficas", err_est)),
            paste0("cont_", v$nombre, "_error"))
  tabla_web(ind, paste0("cont_", v$nombre, "_indicadores"))

  # Excel: una hoja por variable, tablas una debajo de otra
  hoja <- v$nombre
  addWorksheet(libro, hoja)
  fila <- 1                                  # fila donde empieza la próxima tabla
  bloque <- function(titulo, tabla) {        # mini función: escribe título + tabla y baja la fila
    writeData(libro, hoja, titulo, startRow = fila)
    writeData(libro, hoja, tabla, startRow = fila + 1)
    fila <<- fila + nrow(tabla) + 4          # <<- cambia "fila" fuera de la función
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

saveWorkbook(libro, file.path(SALIDAS, "TDF_continuas.xlsx"), overwrite = TRUE)  # guarda el Excel
cat("\nSalidas en", SALIDAS, "\n")
