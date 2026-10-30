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

# Variables continuas: columna de la base, nombre corto, unidad y si se analiza en logaritmo base 10.
VARIABLES <- list(
  list(col = "SiO2 (wt%)", nombre = "SiO2", unidad = "wt%", log = FALSE),
  list(col = "MgO (wt%)",  nombre = "MgO",  unidad = "wt%", log = FALSE),
  # Cr: cola extrema (cromititas de hasta 29,5 %). Se analiza en log10, donde es casi simétrica.
  list(col = "Cr (ppm)",   nombre = "Cr",   unidad = "ppm", log = TRUE)
)

libro <- createWorkbook()
n_graf <- 1

for (v in VARIABLES) {
  # tiene marca las filas con dato. Con ese mismo filtro se toman el valor (x) y el tipo de roca (tipo),
  # así cada valor queda emparejado con su roca.
  tiene <- !is.na(base[[v$col]])
  x <- base[[v$col]][tiene]
  tipo <- base[["Sample Type"]][tiene]
  # Escala de análisis: log10 convierte 10, 100, 1000 ppm en 1, 2, 3; así una cola enorme se vuelve casi simétrica.
  esc <- if (v$log) log10(x) else x                     # escala de análisis
  unidad <- if (v$log) paste("log10", v$unidad) else v$unidad
  nombre <- if (v$log) paste("log10", v$nombre) else v$nombre
  cat("\n==========", v$col, "==========\n")
  cat("n =", length(x), " | rango:", min(x), "-", max(x), "\n")

  # Paso 1: cuántos intervalos sugiere cada regla del curso.
  reglas <- reglas_k(length(x))
  print(reglas)

  # Por defecto (como la plantilla, en la escala original)
  # Paso 2: TDF como la plantilla (Sturges, a = R / k desde el mínimo). Sirve para mostrar el problema:
  # los extremos estiran el rango y casi todos los datos caen en uno o dos intervalos.
  tdf_def <- tdf_continua(x, redondear = FALSE)
  cat(sprintf("Por defecto: k = %d, a = %.4g; el intervalo más poblado concentra el %.1f %% de los datos\n",
              nrow(tdf_def), tdf_def$Ls[1] - tdf_def$Li[1], max(tdf_def$hi)))

  # Outliers y de qué rocas son
  # Paso 3: outliers por la regla intercuartílica y de qué rocas son. table(tipo[es_out]) cuenta los outliers
  # por tipo de roca: si son peridotitas o cromititas, son otras rocas reales, no errores, y NO se borran.
  lim <- limites_iqr(esc)
  es_out <- esc < lim["inferior"] | esc > lim["superior"]
  lim_orig <- if (v$log) 10^lim else lim
  cat(sprintf("Límites IQR: [%.4g ; %.4g] %s -> %d outliers (%.1f %%)\n", lim_orig[1], lim_orig[2], v$unidad,
              sum(es_out), mean(es_out) * 100))
  rocas_out <- sort(table(tipo[es_out]), decreasing = TRUE)
  print(head(rocas_out, 5))

  # TDF corregida, toda la muestra
  # Paso 4: TDF corregida. Intervalos redondos solo sobre el rango típico (límites IQR) y los extremos en
  # dos clases abiertas ("< Li" y "≥ Ls"): todos los datos siguen contados. Luego, su error de agrupación.
  tdf_todo <- tdf_continua(esc, lim = lim)
  err_todo <- error_agrupacion(esc, tdf_todo)
  cat(sprintf("Corregida: %d clases cerradas de amplitud %g + abiertas\n", sum(!is.na(tdf_todo$MC)),
              tdf_todo$Ls[!is.na(tdf_todo$MC)][1] - tdf_todo$Li[!is.na(tdf_todo$MC)][1]))
  print(tdf_todo)
  print(err_todo)

  # Estrato homogéneo
  # Paso 5: lo mismo dentro de un estrato homogéneo (solo rocas volcánicas máficas). Al quitar la mezcla de
  # rocas distintas, la distribución es más compacta y hay menos outliers.
  ee <- esc[tipo == ESTRATO]
  lim_e <- limites_iqr(ee)
  pct_e <- mean(ee < lim_e["inferior"] | ee > lim_e["superior"]) * 100
  tdf_est <- tdf_continua(ee, lim = lim_e)
  err_est <- error_agrupacion(ee, tdf_est)
  cat(sprintf("Estrato %s: n = %d, outliers %.1f %%\n", ESTRATO, length(ee), pct_e))
  print(tdf_est)
  print(err_est)

  # Paso 6: indicadores de toda la muestra y del estrato, lado a lado (y en log10 si corresponde).
  ind <- data.frame(indicador = indicadores(x)$indicador, toda_la_muestra = indicadores(x)$valor,
                    rocas_volcanicas_maficas = indicadores(x[tipo == ESTRATO])$valor)
  if (v$log) ind$log10_toda_la_muestra <- indicadores(esc)$valor
  print(ind, digits = 4)

  # Gráficas
  # Gráficas: por defecto vs corregida (<var>_agrupacion.png), toda la muestra y el estrato (ver funciones.R).
  comparar_agrupacion(tdf_def, tdf_todo, v$nombre, unidad, paste0(v$nombre, "_agrupacion.png"))
  graficos_continua(esc, tdf_todo, nombre, v$unidad, paste0(v$nombre, "_toda_la_muestra.png"), n_graf)
  graficos_continua(ee, tdf_est, paste(nombre, "en rocas volcánicas máficas"), v$unidad,
                    paste0(v$nombre, "_estrato_mafico.png"), n_graf + 3)
  n_graf <- n_graf + 6

  # Tablas para la web
  tabla_web(cbind(intervalo = etiquetas(tdf_todo), tdf_todo), paste0("cont_", v$nombre))
  tabla_web(cbind(intervalo = etiquetas(tdf_est), tdf_est), paste0("cont_", v$nombre, "_estrato"))
  tabla_web(rbind(cbind(muestra = "toda", err_todo), cbind(muestra = "volcanicas maficas", err_est)),
            paste0("cont_", v$nombre, "_error"))
  tabla_web(ind, paste0("cont_", v$nombre, "_indicadores"))

  # Excel: una hoja por variable con las tablas apiladas
  hoja <- v$nombre
  addWorksheet(libro, hoja)
  fila <- 1
  # Función interna para escribir tablas una debajo de otra en la hoja de Excel.
  # El operador <<- modifica la variable fila de afuera de la función (la siguiente tabla empieza más abajo).
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
