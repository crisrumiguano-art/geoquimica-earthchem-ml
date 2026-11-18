"""Un documento R Markdown por variable, con el formato RPubs que mostró el docente en clase (18/11/2026,
https://rpubs.com/dcmendez/1446860): 1. Librerías · 2. Leer datos · 3. Selección de variable · 4. Tabla de
distribución de frecuencia (gt) · 5. Gráficas, cada una aparte · 6. Indicadores estadísticos (gt) · 7. Conclusión.

La selección de la variable y el cálculo de la TDF salen de los scripts simples de R/graficos/ (los mismos del botón
«Código R»), así los números de RPubs y de la web no se separan. Correr después de scripts/codigo_r.py.

Uso: python scripts/rpubs.py [nombre ...]
Salidas: R/rpubs/*.Rmd y docs/rpubs/*.html (los HTML se suben a RPubs con markdown::rpubsUpload).
"""
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GRAFICOS = RAIZ / "R" / "graficos"
RMD = RAIZ / "R" / "rpubs"
HTML = RAIZ / "docs" / "rpubs"
RSCRIPT = r"C:\Program Files\R\R-4.6.1\bin\Rscript.exe"
AUTORES = "Cristoffer Rumiguano, Ana Gabriela Fernández, Evelyn Bustamante, Jessica Haro y Jhonattan Ligña"
FUENTE = "Autores: Rumiguano, Fernández, Bustamante, Haro y Ligña · Datos: EarthChem PetDB (1932-2025)"
CONTEXTO = "en las porciones de roca de EarthChem PetDB (1932-2025)"

# archivo, nombre de la variable, tipo, script de R/graficos, etiqueta del eje, conclusión fija
DOCUMENTOS = [
    ("01_ambiente_tectonico", "Ambiente tectónico agrupado", "nominal", "01", "Ambiente tectónico",
     "La base está dominada por rocas del fondo oceánico: PetDB nació para compilar la petrología de dorsales y "
     "corteza oceánica, así que esta proporción describe la compilación y no a la Tierra entera."),
    ("02_tipo_de_roca", "Tipo de roca", "nominal", "02", "Tipo de roca",
     "Predominan las rocas ígneas volcánicas máficas (basaltos), coherente con el peso de las dorsales en la base; "
     "las categorías con menos de 1 % se agrupan en «otros» para que las gráficas se puedan leer."),
    ("03_clase_SiO2", "Clase según SiO2", "ordinal", "03", "Clase según SiO2",
     "La mayoría de las rocas son básicas (45 a 52 % de SiO2), es decir basaltos y gabros, las rocas más comunes de "
     "la corteza oceánica. Al ser ordinal, la tabla lleva frecuencias acumuladas y tiene mediana."),
    ("04_grado_de_alteracion", "Grado de alteración", "ordinal", "04", "Grado de alteración",
     "Casi la mitad de las rocas con dato de alteración está fresca. Las rocas muy alteradas se deben usar con "
     "cuidado en los elementos que el agua mueve con facilidad (K, Rb, Ba)."),
    ("05_anio_de_publicacion", "Año de publicación", "discreta", "05", "Año de publicación",
     "La mayor parte de los datos es posterior a 1990: la producción creció con las técnicas modernas de laboratorio "
     "(ICP-MS). El año es discreto, pero se agrupa en intervalos porque toma muchos valores distintos."),
    ("06_numero_de_analitos", "Número de analitos", "discreta", "06", "Número de analitos",
     "Muchas porciones de roca tienen pocos analitos: no todas tienen un análisis completo. Por eso, al comparar dos "
     "elementos se usan solo las filas que tienen ambos datos, sin inventar los que faltan."),
    ("07_SiO2", "SiO2", "continua", "08", "SiO2 (wt%)",
     "El SiO2 se concentra en el rango basáltico (45 a 52 %). Los valores fuera del rango típico son otras rocas "
     "(peridotitas, riolitas), no errores: se cuentan en clases abiertas y no se borran."),
    ("08_MgO", "MgO", "continua", "11", "MgO (wt%)",
     "El MgO tiene cola hacia valores altos: las peridotitas del manto (más de 35 % de MgO) se suman a los "
     "basaltos (unos 7 a 10 %). No son errores sino otra roca, por eso no se borran."),
    ("09_Cr", "Cr", "continua", "14", "log10 Cr (ppm)",
     "El cromo varía en varios órdenes de magnitud (de menos de 1 ppm a cromititas con más de 10 000 ppm), por eso "
     "se analiza en log10. En esa escala la distribución es mucho más simétrica."),
]
TIPO_LARGO = {"nominal": "cualitativa nominal", "ordinal": "cualitativa ordinal",
              "discreta": "cuantitativa discreta", "continua": "cuantitativa continua"}
# líneas de los scripts que en R Markdown sobran: imprimir resultados sueltos, guardar imágenes
QUITAR = re.compile(r'^(TDF\s+#|c\(abajo = abajo|categoria\[which|dir\.create\("docs|dev\.off|# Abre|if \(interactive)')

ESTILO_GT = """  tab_source_note(source_note = md("{fuente}")) %>%
  tab_options(
    table.border.top.color = "black",
    table.border.bottom.color = "black",
    column_labels.border.top.color = "black",
    column_labels.border.bottom.color = "black",
    column_labels.border.bottom.width = px(2),
    row.striping.include_table_body = TRUE,
    heading.border.bottom.color = "black",
    heading.border.bottom.width = px(2),
    table_body.hlines.color = "gray"
  )"""


def minus(texto):
    """Primera letra en minúscula, sin tocar fórmulas como SiO2."""
    return texto[0].lower() + texto[1:]


def secciones(numero):
    """{título: [líneas]} de las secciones '# ---- N. Título ----' de R/graficos/NN_*.R."""
    archivo = next(GRAFICOS.glob(f"{numero}_*.R"))
    salida, actual = {}, None
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        m = re.match(r"# ---- (\d+)\. (.*?) ----$", linea)
        if m:
            actual = salida.setdefault(m.group(2), [])
        elif actual is not None and not QUITAR.match(linea.strip()):
            actual.append(linea)
    return salida


def bloque(secs, *prefijos):
    """Une las secciones cuyo título empieza con alguno de los prefijos, sin líneas vacías al final."""
    lineas = [l for t, ls in secs.items() if t.startswith(prefijos) for l in ls]
    while lineas and not lineas[-1].strip():
        lineas.pop()
    return "\n".join(lineas)


def chunk(codigo, opciones=""):
    return f"```{{r{opciones}}}\n{codigo.strip()}\n```\n"


def gt(tabla, numero, subtitulo):
    return (f"{tabla} %>%\n  gt() %>%\n  sub_missing(missing_text = \"\") %>%\n"
            f"  tab_header(\n    title = md(\"*Tabla Nro. {numero}*\"),\n"
            f"    subtitle = md(\"**{subtitulo}**\")\n  ) %>%\n" + ESTILO_GT.format(fuente=FUENTE))


def graficas_cualitativa(nombre, eje):
    titulo = lambda n, que: f'"Gráfica N°{n}: {que} de {minus(nombre)}\\n{CONTEXTO}"'
    barras = """par(mar = c(10, 6.5, 5, 1))              # margen abajo para los nombres largos
barplot({y},
        main = {titulo},
        ylab = "",
        col = "{color}",
        ylim = c(0, {tope}),
        las = 2,
        cex.names = 0.8,
        cex.main = 0.9,
        names.arg = categoria)
title(ylab = "{ylab}", line = 5)          # rótulo del eje, separado de los números
mtext("{eje}", side = 1, line = 8.5, cex = 0.85)"""
    salida = ["## 5. Gráficas", "### 5.1 Diagrama de barras de cantidad",
              chunk("# ===========================\n# Diagrama de barras de cantidad\n# ===========================\n"
                    + barras.format(y="ni", titulo=titulo(1, "Distribución"), color="mediumslateblue",
                                    tope="max(ni) * 1.1", ylab="Cantidad", eje=eje), ", fig.width = 8, fig.height = 6"),
              chunk("# ===========================================================\n"
                    "# Diagrama de barras con relación a la totalidad de los datos\n"
                    "# ===========================================================\n"
                    + barras.format(y="ni", titulo=titulo(2, "Distribución general"), color="mediumpurple1",
                                    tope="sum(ni)", ylab="Cantidad", eje=eje), ", fig.width = 8, fig.height = 6"),
              "### 5.2 Diagrama de barras porcentuales",
              chunk("# ===========================\n# Diagrama de barras porcentual\n# ===========================\n"
                    + barras.format(y="hi", titulo=titulo(3, "Distribución porcentual"), color="mediumslateblue",
                                    tope="max(hi) * 1.1", ylab="Porcentaje (%)", eje=eje), ", fig.width = 8, fig.height = 6"),
              chunk("# =========================================================\n"
                    "# Diagrama de barras porcentual con relación a la totalidad\n"
                    "# =========================================================\n"
                    + barras.format(y="hi", titulo=titulo(4, "Distribución porcentual general"), color="mediumpurple1",
                                    tope="100", ylab="Porcentaje (%)", eje=eje), ", fig.width = 8, fig.height = 6"),
              "### 5.3 Diagrama circular",
              chunk(f"""# =========================
# DIAGRAMA CIRCULAR
# =========================
etiquetas <- ifelse(hi >= 3, paste0(hi, " %"), "")   # solo se rotulan las porciones de 3 % o más
colores <- c("steelblue3", "lightsteelblue3", "lightsteelblue1", "violetred", "wheat", "yellow",
             "darkseagreen3", "salmon", "plum3", "gray70")
layout(matrix(1:2, nrow = 1), widths = c(3, 2))   # a la izquierda la torta, a la derecha la leyenda
par(mar = c(1, 1, 4, 1))
pie(hi,
    labels = etiquetas,
    col = colores[seq_along(hi)],
    clockwise = TRUE,
    main = {titulo(5, "Distribución")},
    cex = 0.9,
    cex.main = 0.9)
par(mar = c(1, 0, 4, 1))
plot.new()                                  # panel vacío para la leyenda
legend("center",
       legend = paste0(categoria, " (", hi, " %)"),   # la leyenda lleva el % de todas
       fill = colores[seq_along(hi)],
       title = "Leyenda",
       cex = 0.85)""", ", fig.width = 9, fig.height = 6")]
    return salida


def graficas_cuantitativa(nombre, eje):
    titulo = lambda n, que: f'"Gráfica N°{n}: {que} de {eje}\\n{CONTEXTO}"'
    alto = ", fig.width = 9, fig.height = 6"
    return ["## 5. Gráficas",
            "Los datos de las clases abiertas (fuera del rango típico) no entran en el histograma ni en el polígono, "
            "pero sí en las ojivas y en el diagrama de caja.",
            "### 5.1 Histograma",
            chunk(f"""# =========================
# HISTOGRAMA
# =========================
etiq <- paste0("[", Li, "-", Ls, "[")      # texto de cada intervalo
par(mar = c(8, 5, 5, 1))
barplot(hi,
        names.arg = etiq,
        space = 0,                          # barras juntas: la variable es continua
        main = {titulo(1, "Histograma")},
        ylab = "Porcentaje (%)",
        col = "mediumslateblue",
        border = "white",
        ylim = c(0, max(hi) * 1.15),
        las = 2,
        cex.names = 0.75,
        cex.main = 0.9)
mtext("{eje}", side = 1, line = 6.5, cex = 0.85)""", alto),
            "### 5.2 Polígono de frecuencias",
            chunk(f"""# =========================
# POLÍGONO DE FRECUENCIAS
# =========================
plot(c(Li[1] - a / 2, MC, Ls[k] + a / 2), c(0, hi, 0),   # une las marcas de clase y cierra en cero
     type = "b",
     pch = 16,
     col = "violetred",
     lwd = 2,
     main = {titulo(2, "Polígono de frecuencias")},
     xlab = "{eje}",
     ylab = "Porcentaje (%)",
     cex.main = 0.9)""", alto),
            "### 5.3 Ojivas ascendente y descendente",
            "Las dos ojivas se cruzan a la altura del 50 %: ahí está la mediana.",
            chunk(f"""# =========================
# OJIVAS
# =========================
plot(Ls, Hi_asc,
     type = "b",
     pch = 16,
     col = "mediumslateblue",
     ylim = c(0, 100),
     main = {titulo(3, "Ojivas")},
     xlab = "{eje}",
     ylab = "Porcentaje acumulado (%)",
     cex.main = 0.9)
lines(Li, Hi_dsc, type = "b", pch = 17, col = "violetred")
abline(h = 50, lty = 3, col = "gray50")
legend("right",
       legend = c("ascendente", "descendente"),
       col = c("mediumslateblue", "violetred"),
       pch = c(16, 17),
       title = "Leyenda",
       cex = 0.8)""", alto),
            "### 5.4 Diagrama de caja",
            chunk(f"""# =========================
# DIAGRAMA DE CAJA
# =========================
boxplot(x,
        horizontal = TRUE,
        col = "lightsteelblue1",
        main = {titulo(4, "Diagrama de caja")},
        xlab = "{eje}",
        cex.main = 0.9)""", ", fig.width = 9, fig.height = 4.5")]


def rmd(nombre, variable, tipo, script, eje, conclusion):
    secs = secciones(script)
    cuali = tipo in ("nominal", "ordinal")
    p = [f'---\ntitle: "{variable}"\nsubtitle: "Universidad Central del Ecuador · FIGEMPA · Estadística y Probabilidades"\n'
         f'author: "{AUTORES}"\ndate: "2026-11-18"\n'
         "output:\n  html_document:\n    toc: true\n    toc_float: true\n    theme: readable\n    highlight: tango\n---\n",
         chunk("knitr::opts_chunk$set(message = FALSE, warning = FALSE, fig.align = \"center\")", ", include = FALSE"),
         f"> Proyecto estrictamente académico. Variable {TIPO_LARGO[tipo]}. Datos: EarthChem PetDB (CC BY 4.0), "
         "descargados el 13/10/2026. Web del proyecto: https://crisrumiguano-art.github.io/geoquimica-earthchem-ml/\n",
         "## 1. Librerías",
         chunk("library(gt)       # tablas con formato (Tabla Nro.)\n"
               "library(dplyr)    # el operador %>% para encadenar pasos"
               + ("" if cuali else "\nlibrary(e1071)    # asimetría y curtosis") +
               "\n\n# barplot(), pie(), plot(), boxplot(), legend() son del paquete graphics, y quantile(), sd(),\n"
               "# var() del paquete stats: los dos vienen con R y se cargan solos, no necesitan library()"),
         "## 2. Leer datos",
         chunk("""# =========================
# Cargar datos
# =========================
# La primera vez descarga la base limpia del repositorio del proyecto (26 MB)
if (!file.exists("data/earthchem_limpio.csv.gz")) {
  dir.create("data", showWarnings = FALSE)
  download.file("https://github.com/crisrumiguano-art/geoquimica-earthchem-ml/raw/main/data/earthchem_limpio.csv.gz",
                "data/earthchem_limpio.csv.gz", mode = "wb")
}
base <- read.csv(gzfile("data/earthchem_limpio.csv.gz", encoding = "UTF-8"), check.names = FALSE)
dim(base)    # 159 760 porciones de roca y 75 variables"""),
         "## 3. Selección de variable"]
    if cuali:
        p.append("Se toma la columna, se traducen las categorías al español y se quitan los vacíos (vacío = no medido).")
        p.append(chunk(bloque(secs, "Datos")))
    else:
        p.append("Se toma la columna y se quitan los vacíos (vacío = no medido, nunca cero)."
                 + (" El cromo se pasa a log10 porque va de menos de 1 a más de 10 000 ppm." if "Cr" in variable else ""))
        p.append(chunk(bloque(secs, "Datos")))

    p.append("## 4. Tabla de distribución de frecuencia")
    sub = f"Distribución de frecuencias de {minus(variable) if cuali else variable} {CONTEXTO}"
    if cuali:
        calculo = bloque(secs, "Tabla de frecuencias")
        if tipo == "ordinal":
            total = ('TDF_suma <- rbind(TDF, data.frame(categoria = "TOTAL", ni = sum(ni), hi = 100, Ni = NA, Hi = NA))\n'
                     'colnames(TDF_suma) <- c("' + eje + '", "ni", "hi(%)", "Ni", "Hi(%)")')
        else:
            total = ('TDF_suma <- rbind(TDF, data.frame(categoria = "TOTAL", ni = sum(ni), hi = 100))\n'
                     'colnames(TDF_suma) <- c("' + eje + '", "ni", "hi(%)")')
        p.append(chunk("# =========================\n# TABLA DE FRECUENCIAS\n# =========================\n"
                       + calculo + "\n" + total + "\n\n" + gt("TDF_suma", 1, sub)))
    else:
        if tipo == "continua":
            p.append("Los límites de los intervalos se fijan con los datos típicos (regla intercuartílica) y la regla "
                     "de Sturges; los valores extremos no se borran, se cuentan en dos clases abiertas.")
        else:
            p.append("El número de intervalos sale de la regla de Sturges, k = 1 + 3,3·log10(n), con una amplitud "
                     "redonda para que los límites sean fáciles de leer.")
        calculo = bloque(secs, "Límites", "Intervalos", "Frecuencias")
        total = ('TDF_suma <- rbind(TDF, data.frame(Li = NA, Ls = NA, MC = NA, ni = sum(ni), hi = sum(hi),\n'
                 '                                   Ni_asc = NA, Ni_dsc = NA, Hi_asc = NA, Hi_dsc = NA))\n'
                 'TDF_suma$Li[k + 1] <- "TOTAL"\n'
                 'colnames(TDF_suma) <- c("Li", "Ls", "MC", "ni", "hi(%)", "Ni asc", "Ni desc", "Hi asc(%)", "Hi desc(%)")')
        nota = ('\n\n# Clases abiertas: datos fuera de los intervalos (no se borra ninguno)\n'
                'c(menores = abajo, mayores = arriba)')
        p.append(chunk("# =========================\n# TABLA DE FRECUENCIAS\n# =========================\n"
                       + calculo + "\n" + total + "\n\n" + gt("TDF_suma", 1, sub) + nota))

    p += graficas_cualitativa(variable, eje) if cuali else graficas_cuantitativa(variable, eje)

    p.append("## 6. Indicadores estadísticos")
    sub = f"Indicadores estadísticos de {minus(variable) if cuali else variable} {CONTEXTO}"
    if cuali:
        mediana = ('Me <- categoria[which(Hi >= 50)[1]]    # mediana: primera categoría donde Hi llega al 50 %'
                   if tipo == "ordinal" else 'Me <- "-"                               # nominal: sin orden, no hay mediana')
        p.append("En una variable cualitativa solo tiene sentido la moda" +
                 (" y, por ser ordinal, la mediana." if tipo == "ordinal" else ".") + " El resto queda con «-».")
        p.append(chunk(f"""# =========================
# INDICADORES ESTADÍSTICOS
# =========================
Mo <- paste(categoria[ni == max(ni)], collapse = " - ")   # moda
{mediana}

tabla_indicadores <- data.frame(Variable = "{variable}", Rango = "-", X = "-", Me = Me, Mo = Mo,
                                V = "-", Sd = "-", Cv = "-", As = "-", K = "-", Valores_Atipicos = "-")

""" + gt("tabla_indicadores", 2, sub)))
        cierre = "res <- list(moda = Mo, hi_max = max(hi), n = sum(ni), k = length(ni))"
    else:
        moda = ("Mo <- as.numeric(names(which.max(table(x))))      # moda: el valor que más se repite"
                if tipo == "discreta" else
                "Mo <- MC[which.max(ni)]                            # moda: marca de la clase con más datos")
        p.append("Medidas de tendencia central, dispersión y forma, calculadas con los datos sin agrupar"
                 + (" (en log10)." if "Cr" in variable else "."))
        p.append(chunk(f"""# =========================
# INDICADORES ESTADÍSTICOS
# =========================
{moda}
cuartiles <- quantile(x, c(0.25, 0.75), names = FALSE)
RI <- cuartiles[2] - cuartiles[1]                     # rango intercuartílico
atipicos <- sum(x < cuartiles[1] - 1.5 * RI | x > cuartiles[2] + 1.5 * RI)

tabla_indicadores <- data.frame(
  Variable = "{eje}",
  Rango = paste(round(min(x), 2), "a", round(max(x), 2)),
  X = round(mean(x), 2),
  Me = round(median(x), 2),
  Mo = round(Mo, 2),
  V = round(var(x), 2),
  Sd = round(sd(x), 2),
  Cv = paste0(round(sd(x) / mean(x) * 100, 2), " %"),
  As = round(skewness(x), 2),
  K = round(kurtosis(x), 2),
  Valores_Atipicos = atipicos
)

""" + gt("tabla_indicadores", 2, sub)))
        cierre = ("res <- list(n = n, mediana = median(x), cv = sd(x) / mean(x) * 100, asim = skewness(x),\n"
                  "            atipicos = atipicos, moda = Mo)")
        if tipo == "continua":
            p.append("### Error de agrupación")
            p.append("Se compara la media y la desviación calculadas con la tabla (cada dato vale la marca de clase de "
                     "su intervalo) con las calculadas con los datos: menos de 5 % de error indica que la tabla "
                     "representa bien a los datos.")
            p.append(chunk(bloque(secs, "Error de agrupación").replace(
                "c(error_media =", "error <- c(error_media =") + "\n\n"
                + "tabla_error <- data.frame(Indicador = c(\"Media\", \"Desviación estándar\"),\n"
                  "                          Con_la_tabla = round(c(media_agrupada, desv_agrupada), 3),\n"
                  "                          Con_los_datos = round(c(mean(xc), sd(xc)), 3),\n"
                  "                          Error_porcentual = round(error, 2))\n\n"
                + gt("tabla_error", 3, f"Error de agrupación de {variable} {CONTEXTO}")))
            cierre += "\nres$err <- error[1]"
    p.append(chunk("f <- function(v, d = 2) format(round(v, d), big.mark = if (abs(v) >= 10000) \" \" else \"\", decimal.mark = \",\")\n" + cierre,
                   ", include = FALSE"))

    p.append("## 7. Conclusión")
    if cuali:
        texto = ("El valor más frecuente (moda) de la variable " + minus(variable) + " es **`r res$moda`**, con el "
                 "`r f(res$hi_max)` % de las `r f(res$n, 0)` porciones de roca con dato, repartidas en `r res$k` "
                 "categorías. " + conclusion)
    else:
        log = "Cr" in variable
        unidad = {"discreta": "" if "Año" in variable else " analitos"}.get(tipo, " ppm" if log else " %")
        texto = (f"Se analizaron `r f(res$n, 0)` porciones de roca con dato. La mediana es "
                 f"`r f({'10^res$mediana' if log else 'res$mediana'})`{unidad}"
                 + (" (en log10, la escala del análisis, `r f(res$mediana)`)" if log else "")
                 + ", el coeficiente de variación es `r f(res$cv)` % y la asimetría es `r f(res$asim)` "
                 "(`r if (res$asim > 0) \"cola hacia los valores altos\" else \"cola hacia los valores bajos\"`). "
                 "Hay `r f(res$atipicos, 0)` valores atípicos según la regla intercuartílica; no se borran. ")
        if tipo == "continua":
            texto += "El error de agrupación de la media es `r f(res$err)` %. "
        texto += conclusion
    p.append(texto)
    return "\n".join(p) + "\n"


def main():
    RMD.mkdir(exist_ok=True)
    HTML.mkdir(exist_ok=True)
    for nombre, *datos in DOCUMENTOS:
        (RMD / f"{nombre}.Rmd").write_text(rmd(nombre, *datos), encoding="utf-8")
    solo = sys.argv[1:] or [d[0] for d in DOCUMENTOS]
    codigo = ("for (f in commandArgs(TRUE)) rmarkdown::render(file.path('R/rpubs', paste0(f, '.Rmd')), "
              "output_dir = 'docs/rpubs', knit_root_dir = getwd(), quiet = TRUE, envir = new.env())")
    script = RMD / "_render.R"
    script.write_text(codigo, encoding="utf-8")
    try:
        subprocess.run([RSCRIPT, str(script), *solo], cwd=RAIZ, check=True)
    finally:
        script.unlink()
    print(f"{len(solo)} documentos -> {HTML}")


if __name__ == "__main__":
    main()
