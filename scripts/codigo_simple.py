"""Código R SIMPLE de cada gráfico de la web: paso a paso, sin funciones propias, como la plantilla del curso.

Cada plantilla repite exactamente lo que hacen las funciones de R/funciones.R para ese gráfico, escrito en
línea, de modo que el PNG sale idéntico (scripts/codigo_r.py lo usa y la prueba lo compara byte a byte).
Las amplitudes «redondas» se leen de las TDF que exportó R (docs/data/tdf/), para escribirlas como número.
"""
import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TDF = RAIZ / "docs" / "data" / "tdf"
BASE_URL = "https://github.com/crisrumiguano-art/geoquimica-earthchem-ml/raw/main/data/earthchem_limpio.csv.gz"
MAFICAS = "igneous:volcanic:mafic"

CUAL = {  # archivo -> (columna, título, orden o None, número de gráfica)
    "grupo_tectonico": ("Tectonic Group", "Ambiente tectónico agrupado", None, 1),
    "tipo_de_roca": ("Sample Type", "Tipo de roca", None, 3),
    "clase_sio2": ("SiO2 Class", "Clase de roca según SiO2", ["ultrabasica", "basica", "intermedia", "acida"], 5),
    "alteracion": ("Alteration Grade", "Grado de alteración",
                   ["0 fresca", "1 leve", "2 moderada", "3 extensa", "4 casi total", "5 total"], 7),
}
DISC = {"anio": ("Publication Year", "Año de publicación", "año", 1),
        "analitos": ("N Analytes", "Número de analitos", "analitos", 4)}
CONT = {"SiO2": ("SiO2 (wt%)", "wt%", False, 1), "MgO": ("MgO (wt%)", "wt%", False, 7),
        "Cr": ("Cr (ppm)", "ppm", True, 13)}


def amplitud(csv_nombre):
    """Amplitud de las clases cerradas de una TDF exportada por R (p. ej. 2 para SiO2)."""
    with open(TDF / csv_nombre, encoding="utf-8") as f:
        fila = next(r for r in csv.DictReader(f) if r["MC"] != "NA")
    a = float(fila["Ls"]) - float(fila["Li"])
    return f"{a:g}" if abs(a - round(a, 6)) < 1e-9 else repr(a)


def r_vector(valores):
    return "c(" + ", ".join(f'"{v}"' for v in valores) + ")"


INICIO = '''# =========================================================================================
# GRÁFICO: @TITULO@   (@PNG@)
# Código simple, paso a paso. Copiar todo en RStudio y ejecutar (Ctrl + A, Ctrl + Enter).
# Antes: Session > Set Working Directory > la carpeta donde se quiere trabajar.
# Las líneas con # son explicaciones (R no las ejecuta).
# =========================================================================================

# ---- 0. Leer la base de datos (la primera vez la descarga, 26 MB) ----
if (!file.exists("data/earthchem_limpio.csv.gz")) {
  dir.create("data", showWarnings = FALSE)
  download.file("@URL@", "data/earthchem_limpio.csv.gz", mode = "wb")
}
base <- read.csv(gzfile("data/earthchem_limpio.csv.gz", encoding = "UTF-8"), check.names = FALSE)
dir.create("docs/img/r", recursive = TRUE, showWarnings = FALSE)   # carpeta donde se guarda el gráfico
'''

FIN = '''
# Abre la imagen que se acaba de crear (solo en RStudio)
if (interactive()) browseURL(file.path(getwd(), "docs/img/r/@PNG@"))
'''

# ------------------------------------------------------------------------------------- cualitativas
CUALITATIVA = '''
# ---- 1. Datos ----
x <- base[["@COL@"]]                         # la columna de la base@PREVIO@
x <- as.character(x)                         # como texto
x <- x[!is.na(x) & x != ""]                  # quita los vacíos

# ---- 2. Tabla de frecuencias ----
@CONTEO@
categoria <- names(conteo)
ni <- as.vector(conteo)                      # frecuencia absoluta
hi <- round(ni / sum(ni) * 100, 2)           # frecuencia relativa (%)
@ACUM@
TDF                                          # muestra la tabla
categoria[which.max(ni)]                     # moda: la categoría con más casos@MEDIANA@

# ---- 3. Gráfico: barras + circular ----
png("docs/img/r/@PNG@", width = 1600, height = 700, res = 130)   # abre la imagen
par(mfrow = c(1, 2), mar = c(9, 5, 4, 1))    # 2 gráficos lado a lado
colores <- gray.colors(length(ni), start = .25, end = .85)       # un gris por categoría
barplot(ni, names.arg = categoria, las = 2, col = colores, ylab = "Cantidad",   # barras: altura = ni
        main = "Gráfica No. @N1@: @TITULO@", cex.names = .8, cex.main = .9)
par(mar = c(1, 1, 4, 1))
pie(hi, labels = paste0(hi, "%"), col = colores, clockwise = TRUE, cex = .75,  # circular: porción = hi
    main = "Gráfica No. @N2@: @TITULO@ (%)", cex.main = .9)
legend("topright", legend = categoria, fill = colores, cex = .6, bty = "n")
dev.off()                                    # cierra y guarda la imagen
'''


def cualitativa(clave, png):
    col, titulo, orden, n = CUAL[clave]
    previo = ""
    if clave == "tipo_de_roca":
        previo = ('\nfrec <- prop.table(table(x))                 # proporción de cada tipo\n'
                  'x[x %in% names(frec[frec < 0.01])] <- "otros" # los de menos de 1 % se juntan en "otros"')
    if clave == "alteracion":
        previo = ('\nx <- factor(x, levels = 0:5, labels = ' + r_vector(orden) + ')   # códigos 0-5 -> nombres')
    if orden:
        conteo = (f"orden <- {r_vector(orden)}   # ordinal: su orden natural\n"
                  "conteo <- table(factor(x, levels = orden))   # cuenta cada categoría, en ese orden")
        acum = ("Ni <- cumsum(ni)                             # acumulada absoluta (solo ordinales)\n"
                "Hi <- round(cumsum(ni) / sum(ni) * 100, 2)   # acumulada relativa (%)\n"
                "TDF <- data.frame(categoria, ni, hi, Ni, Hi)")
        mediana = "\ncategoria[which(Hi >= 50)[1]]                # mediana: donde Hi llega al 50 %"
    else:
        conteo = "conteo <- sort(table(x), decreasing = TRUE)  # cuenta cada categoría, de mayor a menor"
        acum = "TDF <- data.frame(categoria, ni, hi)         # nominal: sin acumuladas (no hay orden)"
        mediana = ""
    return (CUALITATIVA.replace("@COL@", col).replace("@PREVIO@", previo).replace("@CONTEO@", conteo)
            .replace("@ACUM@", acum).replace("@MEDIANA@", mediana).replace("@N1@", str(n))
            .replace("@N2@", str(n + 1)).replace("@TITULO@", titulo).replace("@PNG@", png)), titulo


# ----------------------------------------------------------------------- cuantitativas: TDF + gráficos
INTERVALOS = '''
# ---- @P@. Intervalos (regla de Sturges) ----
k <- round(1 + 3.3 * log10(n))                         # número de intervalos
a <- (max(tipico) - min(tipico)) / k                   # amplitud calculada
a <- @A@                                               # se redondea hacia arriba a un número cómodo
desde <- floor(min(tipico) / a) * a                    # primer límite: múltiplo de a
k <- floor((max(tipico) - desde) / a) + 1              # intervalos que hacen falta para llegar al máximo
Li <- desde + (0:(k - 1)) * a                          # límites inferiores
Ls <- Li + a                                           # límites superiores
MC <- (Li + Ls) / 2                                    # marca de clase

# ---- @P2@. Frecuencias ----
dentro <- x[x >= Li[1] & x <= Ls[k]]
ni <- as.vector(table(cut(dentro, breaks = c(Li, Ls[k]), right = FALSE, include.lowest = TRUE)))  # cuenta por intervalo [Li, Ls[
abajo <- sum(x < Li[1])                                # clase abierta "menor que" (outliers bajos)
arriba <- sum(x > Ls[k])                               # clase abierta "mayor o igual" (outliers altos)
hi <- round(ni / n * 100, 2)                           # frecuencia relativa (%)
todos <- c(abajo, ni, arriba)                          # con las clases abiertas, para acumular
cerradas <- 2:(k + 1)                                  # posiciones de los intervalos normales
Ni_asc <- cumsum(todos)[cerradas]                      # acumulada ascendente
Ni_dsc <- rev(cumsum(rev(todos)))[cerradas]            # acumulada descendente
Hi_asc <- round(cumsum(todos) / n * 100, 2)[cerradas]
Hi_dsc <- round(rev(cumsum(rev(todos))) / n * 100, 2)[cerradas]
TDF <- data.frame(Li, Ls, MC, ni, hi, Ni_asc, Ni_dsc, Hi_asc, Hi_dsc)
TDF                                                    # la tabla
c(abajo = abajo, arriba = arriba)                      # datos en las clases abiertas (no se borra ninguno)
'''

GRAFICOS = '''
# ---- @P@. Gráficos: histograma + polígono, ojiva y caja ----
etiq <- paste0("[", Li, "-", Ls, "[")                  # texto de cada intervalo
nota <- c(if (abajo > 0) paste0("< ", Li[1], ": ", abajo, " (", round(abajo / n * 100, 2), " %)"),
          if (arriba > 0) paste0("≥ ", Ls[k], ": ", arriba, " (", round(arriba / n * 100, 2), " %)"))
png("docs/img/r/@PNG@", width = 1800, height = 1200, res = 130)    # abre la imagen
layout(matrix(c(1, 1, 2, 3), 2, 2, byrow = TRUE), heights = c(1.15, 1))   # arriba 1 gráfico, abajo 2
par(mar = c(8, 5, 4, 1))
h <- barplot(hi, names.arg = etiq, space = 0, las = 2, col = "#3987e5", border = "white",   # histograma
             ylab = "Porcentaje (%)", cex.names = .75, ylim = c(0, max(hi) * 1.15),
             main = "Gráfica No. @N1@: Histograma y polígono de frecuencias de @NOMBRE@ (@UNIDAD@)")
lines(c(h[1] - 1, h, h[length(h)] + 1), c(0, hi, 0), col = "#d95926", lwd = 2, type = "b", pch = 16, cex = .6)  # polígono
mtext(if (length(nota) > 0) paste0("Clases abiertas (fuera del gráfico): ", paste(nota, collapse = " · ")) else "",
      side = 1, line = 6.5, cex = .7, col = "gray30")  # nota bajo el histograma
par(mar = c(5, 5, 4, 1))
plot(Ls, Hi_asc, type = "b", pch = 16, col = "#3987e5", ylim = c(0, 100),            # ojiva ascendente
     xlab = "@NOMBRE@ (@UNIDAD@)", ylab = "Porcentaje acumulado (%)",
     main = "Gráfica No. @N2@: Ojiva ascendente y descendente")
lines(Li, Hi_dsc, type = "b", pch = 17, col = "#d95926")                              # ojiva descendente
abline(h = 50, lty = 3, col = "gray50")                # línea del 50 %: donde se cruzan está la mediana
legend("right", c("ascendente (≤)", "descendente (≥)"), col = c("#3987e5", "#d95926"), pch = c(16, 17), bty = "n", cex = .85)
boxplot(x, horizontal = TRUE, col = "#86b6ef", xlab = "@NOMBRE@ (@UNIDAD@)",       # diagrama de caja
        main = "Gráfica No. @N3@: Diagrama de caja (todos los datos)")
dev.off()                                              # cierra y guarda la imagen
'''

INDICADORES = '''
# ---- @P@. Indicadores (con los datos sin agrupar@ESCALA@) ----
library(e1071)                                         # para asimetría y curtosis (install.packages("e1071"))
c(n = n, media = mean(x), mediana = median(x), desviacion = sd(x), varianza = var(x),
  CV = sd(x) / mean(x) * 100, asimetria = skewness(x), curtosis = kurtosis(x))
'''

ERROR = '''
# ---- @P@. Error de agrupación: media y desviación con la TDF vs con los datos ----
xc <- x[x >= Li[1] & x <= Ls[k]]                       # los datos de los intervalos normales
media_agrupada <- sum(MC * ni) / sum(ni)               # cada dato = la marca de clase de su intervalo
desv_agrupada <- sqrt(sum((MC - media_agrupada)^2 * ni) / sum(ni))
c(error_media = abs(media_agrupada - mean(xc)) / mean(xc) * 100,   # en %; menos de 5 % = bien
  error_desviacion = abs(desv_agrupada - sd(xc)) / sd(xc) * 100)
'''


def numerar(bloques):
    """Pone los números de paso (1, 2, 3...) en orden."""
    texto, paso = "", 1
    for b in bloques:
        while "@P@" in b or "@P2@" in b:
            b = b.replace("@P@", str(paso), 1) if "@P@" in b else b
            paso += 1
            if "@P2@" in b:
                b = b.replace("@P2@", str(paso), 1)
                paso += 1
        texto += b
    return texto


def discreta(clave, png):
    col, titulo, unidad, n = DISC[clave]
    datos = (f'\n# ---- 1. Datos ----\nx <- base[["{col}"]]\nx <- x[!is.na(x)]                                      # quita vacíos\n'
             "n <- length(x)\ntipico <- x                                            # aquí se agrupan todos los datos\n")
    a = amplitud(f"disc_{clave}.csv")
    cuerpo = numerar([INTERVALOS.replace("@A@", a), GRAFICOS, INDICADORES.replace("@ESCALA@", "")])
    cuerpo = cuerpo.replace("# ---- 1. Intervalos", "# ---- 2. Intervalos").replace("# ---- 2. Frecuencias", "# ---- 3. Frecuencias") \
        .replace("# ---- 3. Gráficos", "# ---- 4. Gráficos").replace("# ---- 4. Indicadores", "# ---- 5. Indicadores")
    cuerpo += "as.numeric(names(which.max(table(x))))                # moda: el valor que más se repite\n"
    cuerpo = (cuerpo.replace("@PNG@", png).replace("@NOMBRE@", titulo).replace("@UNIDAD@", unidad)
              .replace("@N1@", str(n)).replace("@N2@", str(n + 1)).replace("@N3@", str(n + 2)))
    return datos + cuerpo, titulo


def continua(var, parte, png):
    col, unidad, log, n0 = CONT[var]
    nombre = f"log10 {var}" if log else var
    lineas = ["", "# ---- 1. Datos ----", f'x <- base[["{col}"]]', 'tipo <- base[["Sample Type"]]                        # tipo de roca de cada fila',
              "tiene <- !is.na(x)                                     # filas con dato",
              "x <- x[tiene]", "tipo <- tipo[tiene]"]
    if log:
        lineas.append("x <- log10(x)                                          # escala log10: 10, 100, 1000 ppm -> 1, 2, 3")
    if parte == "estrato_mafico":
        lineas.append(f'x <- x[tipo == "{MAFICAS}"]          # solo rocas volcánicas máficas')
    lineas += ["n <- length(x)", "",
               "# ---- 2. Límites de outliers (regla intercuartílica) ----",
               "Q1 <- quantile(x, 0.25, names = FALSE)",
               "Q3 <- quantile(x, 0.75, names = FALSE)",
               "IR <- Q3 - Q1                                          # rango intercuartílico",
               "lim_inf <- Q1 - 1.5 * IR                               # menos que esto = outlier bajo",
               "lim_sup <- Q3 + 1.5 * IR                               # más que esto = outlier alto",
               "tipico <- x[x >= lim_inf & x <= lim_sup]               # los intervalos se arman con estos datos",
               "# Los outliers NO se borran: se cuentan en las clases abiertas (son otras rocas, no errores)."]
    datos = "\n".join(lineas) + "\n"
    csv_tdf = f"cont_{var}{'_estrato' if parte == 'estrato_mafico' else ''}.csv"
    intervalos = INTERVALOS.replace("@A@", amplitud(csv_tdf)).replace("@P@", "3").replace("@P2@", "4")
    if parte == "agrupacion":
        return datos + intervalos + agrupacion(var, col, unidad, log, png), f"{var}: agrupación por defecto vs corregida"
    sufijo = " en rocas volcánicas máficas" if parte == "estrato_mafico" else ""
    n = n0 + (3 if sufijo else 0)
    graf = (GRAFICOS.replace("@P@", "5").replace("@PNG@", png).replace("@NOMBRE@", nombre + sufijo)
            .replace("@UNIDAD@", unidad).replace("@N1@", str(n)).replace("@N2@", str(n + 1)).replace("@N3@", str(n + 2)))
    escala = ", en log10" if log else ""
    return (datos + intervalos + graf + ERROR.replace("@P@", "6") + INDICADORES.replace("@P@", "7").replace("@ESCALA@", escala),
            f"{nombre}{sufijo}")


AGRUPACION = '''
# ---- 5. TDF "por defecto" (como la plantilla): Sturges sobre TODO el rango, en la escala original ----
x0 <- base[["@COL@"]]
x0 <- x0[!is.na(x0)]
k0 <- round(1 + 3.3 * log10(length(x0)))
a0 <- (max(x0) - min(x0)) / k0                         # amplitud sin redondear
Li0 <- min(x0) + (0:(k0 - 1)) * a0
Ls0 <- Li0 + a0
ni0 <- as.vector(table(cut(x0[x0 <= Ls0[k0]], breaks = c(Li0, Ls0[k0]), right = FALSE, include.lowest = TRUE)))
arriba0 <- sum(x0 > Ls0[k0])                           # por redondeo, el máximo puede quedar afuera
hi0 <- round(c(ni0, arriba0[arriba0 > 0]) / length(x0) * 100, 2)
num <- function(v) trimws(formatC(round(v, 1), format = "fg", digits = 6))   # número a texto: 1 decimal, 6 cifras
etiq0 <- c(paste0("[", num(Li0), "-", num(Ls0), "["), if (arriba0 > 0) paste0("≥ ", num(Ls0[k0])))

# ---- 6. Gráfico: por defecto (izquierda) vs corregida (derecha) ----
etiq <- paste0("[", Li, "-", Ls, "[")
nota <- c(if (abajo > 0) paste0("< ", Li[1], ": ", abajo, " (", round(abajo / n * 100, 2), " %)"),
          if (arriba > 0) paste0("≥ ", Ls[k], ": ", arriba, " (", round(arriba / n * 100, 2), " %)"))
png("docs/img/r/@PNG@", width = 1800, height = 780, res = 130)    # abre la imagen
par(mfrow = c(1, 2), mar = c(8, 5, 4, 1))              # 2 histogramas lado a lado
barplot(hi0, names.arg = etiq0, space = 0, las = 2, cex.names = .65, col = "gray60", border = "white",
        ylab = "Porcentaje (%)", main = paste0("Por defecto: Sturges sobre el rango completo\\n@VAR@, k = ", length(hi0)))
barplot(hi, names.arg = etiq, space = 0, las = 2, cex.names = .65, col = "#3987e5", border = "white",
        ylab = "Porcentaje (%)", main = paste0("Corregida: rango típico (IQR) + clases abiertas\\n@VAR@ (@UNIDAD@), k = ", k, " cerradas"))
mtext(if (length(nota) > 0) paste0("Clases abiertas (fuera del gráfico): ", paste(nota, collapse = " · ")) else "",
      side = 1, line = 6.5, cex = .65, col = "gray30")
dev.off()                                              # cierra y guarda la imagen
'''


def agrupacion(var, col, unidad, log, png):
    return (AGRUPACION.replace("@COL@", col).replace("@PNG@", png).replace("@VAR@", var)
            .replace("@UNIDAD@", f"log10 {unidad}" if log else unidad))


def simple(png):
    """Código simple completo de un PNG; None si no tiene plantilla (muestreo)."""
    nombre = png.removesuffix(".png")
    if nombre.startswith("cual_"):
        cuerpo, titulo = cualitativa(nombre[5:], png)
    elif nombre.startswith("disc_"):
        cuerpo, titulo = discreta(nombre[5:], png)
    elif nombre.startswith("muestreo_"):
        return None
    else:
        var, parte = nombre.split("_", 1)
        cuerpo, titulo = continua(var, parte, png)
    return (INICIO.replace("@TITULO@", titulo).replace("@PNG@", png).replace("@URL@", BASE_URL)
            + cuerpo + FIN.replace("@PNG@", png))
