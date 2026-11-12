"""Un documento R Markdown por variable, para publicar en RPubs como el proyecto modelo del docente
(https://geoquimicaglobal.framer.website/ -> rpubs.com): carga de datos, TDF, gráficos, indicadores, outliers y
conclusión, cada paso con su código.

Se arma desde los scripts simples de R/graficos/ (los mismos del botón «Código R»), así el código de RPubs y el de
la web no se separan. Correr después de scripts/codigo_r.py.

Uso: python scripts/rpubs.py
Salidas: R/rpubs/*.Rmd y docs/rpubs/*.html (los HTML se suben a RPubs desde RStudio: botón Publish).
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
AUTORES = ("Cristoffer Rumiguano, Ana Gabriela Fernández, Evelyn Bustamante, Jessica Haro, "
           "Jhonattan Ligña")

# archivo de salida, título, subtipo, scripts (principal, corrección de la agrupación, estrato), conclusión fija
DOCUMENTOS = [
    ("01_ambiente_tectonico", "Ambiente tectónico agrupado (Tectonic Group)", "cualitativa nominal", ["01"],
     "La base está dominada por rocas del fondo oceánico: PetDB nació para compilar la petrología de dorsales y "
     "corteza oceánica, así que esta proporción describe la compilación y no a la Tierra entera."),
    ("02_tipo_de_roca", "Tipo de roca (Sample Type)", "cualitativa nominal", ["02"],
     "Predominan las rocas ígneas volcánicas máficas (basaltos), coherente con el peso de las dorsales en la base; "
     "las categorías poco frecuentes se agrupan en «Otros» para que el gráfico se pueda leer."),
    ("03_clase_SiO2", "Clase según SiO2 (SiO2 Class)", "cualitativa ordinal", ["03"],
     "La mayoría de las rocas son básicas (45 a 52 % de SiO2), es decir basaltos y gabros, las rocas más comunes de "
     "la corteza oceánica. Al ser ordinal, la tabla lleva frecuencias acumuladas."),
    ("04_grado_de_alteracion", "Grado de alteración (Alteration Grade)", "cualitativa ordinal", ["04"],
     "Casi la mitad de los análisis informados son de rocas frescas. Los de rocas muy alteradas se deben usar con "
     "cuidado en los elementos que el agua mueve con facilidad (K, Rb, Ba)."),
    ("05_anio_de_publicacion", "Año de publicación (Publication Year)", "cuantitativa discreta", ["05"],
     "La mayor parte de los datos es posterior a 1990: la producción creció con las técnicas modernas de laboratorio "
     "(ICP-MS). El año es discreto, pero se agrupa en intervalos porque toma muchos valores distintos."),
    ("06_numero_de_analitos", "Número de analitos (N Analytes)", "cuantitativa discreta", ["06"],
     "Muchas muestras tienen pocos analitos: no todas tienen un análisis completo. Por eso, al comparar dos "
     "elementos se usan solo las filas que tienen ambos datos, sin inventar los que faltan."),
    ("07_SiO2", "SiO2 (wt%)", "cuantitativa continua", ["08", "07", "09"],
     "El SiO2 se concentra en el rango basáltico (45 a 52 %). En las rocas volcánicas máficas la dispersión baja "
     "mucho: separar por tipo de roca da distribuciones más limpias que mezclar todo."),
    ("08_MgO", "MgO (wt%)", "cuantitativa continua", ["11", "10", "12"],
     "El MgO tiene cola hacia valores altos: las peridotitas del manto (más de 35 % de MgO) se suman a los "
     "basaltos (unos 7 a 10 %). No son errores sino otra roca, por eso no se borran."),
    ("09_Cr", "Cr (ppm)", "cuantitativa continua", ["14", "13", "15"],
     "El cromo varía en varios órdenes de magnitud (de menos de 1 ppm a cromititas con más de 10 000 ppm), por eso "
     "se analiza en log10. En esa escala la distribución es mucho más simétrica."),
]

TEXTOS = [  # explicación corta antes de cada paso, según el título de la sección del script
    ("Datos", "Se toma la columna de la variable y se quitan las filas vacías (vacío = no medido, nunca cero)."),
    ("Tabla de frecuencias", "ni cuenta los casos de cada categoría y hi los expresa en porcentaje; la moda es la "
                             "categoría con más casos."),
    ("Límites de outliers", "Con el rango intercuartílico (IR = Q3 − Q1) se fijan los límites Q1 − 1,5·IR y "
                            "Q3 + 1,5·IR. Los datos que quedan fuera no se eliminan: se cuentan en clases abiertas."),
    ("Intervalos", "El número de intervalos sale de la regla de Sturges, k = 1 + 3,3·log10(n); la amplitud se "
                   "redondea a un número cómodo para que los límites sean fáciles de leer."),
    ("Frecuencias", "Tabla de distribución de frecuencias: límites, marca de clase, frecuencia absoluta y relativa, y "
                    "acumuladas ascendentes y descendentes."),
    ("Gráfico: barras", "Diagrama de barras (altura = ni) y diagrama circular (porción = hi)."),
    ("Gráficos", "Histograma con polígono de frecuencias, ojivas ascendente y descendente (se cruzan en la mediana) "
                 "y diagrama de caja."),
    ("Error de agrupación", "Se comparan la media y la desviación calculadas con la TDF (cada dato = la marca de "
                            "clase de su intervalo) con las calculadas con los datos; menos de 5 % de error indica "
                            "que la agrupación representa bien los datos."),
    ("Indicadores", "Medidas de tendencia central, dispersión y forma con los datos sin agrupar (asimetría y curtosis "
                    "con el paquete e1071)."),
    ("TDF \"por defecto\"", "Para justificar la corrección, se arma la TDF como en la plantilla: Sturges sobre todo el "
                            "rango, sin tratar los extremos."),
    ("Gráfico: por defecto", "A la izquierda, la agrupación por defecto (casi todo cae en uno o dos intervalos); a la "
                             "derecha, la corregida."),
]
QUITAR = ("dir.create(\"docs/img/r\"", "dev.off()", "# Abre la imagen", "if (interactive()) browseURL",
          "library(e1071)")


def secciones(numero):
    """Secciones '# ---- N. Título ----' del script R/graficos/NN_*.R: [(título, [líneas])], sin la lectura de la base."""
    archivo = next(GRAFICOS.glob(f"{numero}_*.R"))
    salida, actual = [], None
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        m = re.match(r"# ---- (\d+)\. (.*?) ----$", linea)
        if m:
            actual = None if m.group(1) == "0" else (m.group(2), [])
            if actual:
                salida.append(actual)
        elif actual and not linea.lstrip().startswith(QUITAR):
            actual[1].append(linea)
    return salida


class Documento:
    def __init__(self):
        self.partes, self.tablas = [], 0

    def texto(self, t):
        self.partes.append(t + "\n")

    def chunk(self, lineas, opciones=""):
        cuerpo, tabla_ind = [], False
        for linea in lineas:
            png = re.match(r'png\(".*?", width = (\d+), height = (\d+)', linea)
            if png:  # en R Markdown el gráfico se muestra en el documento: se fija su tamaño en el chunk
                opciones += f", fig.width = {int(png.group(1)) / 200:g}, fig.height = {int(png.group(2)) / 200:g}"
                continue
            if re.match(r"TDF\s+#", linea):
                self.tablas += 1
                linea = f'knitr::kable(TDF, caption = "Tabla N° {self.tablas}: distribución de frecuencias")'
            if linea.startswith("c(n = n,"):
                linea, tabla_ind = "ind <- " + linea, True
            cuerpo.append(linea)
        if tabla_ind:
            self.tablas += 1
            cuerpo.append(f'knitr::kable(data.frame(indicador = names(ind), valor = round(ind, 4)), row.names = FALSE,\n'
                          f'             caption = "Tabla N° {self.tablas}: indicadores estadísticos")')
        while cuerpo and not cuerpo[-1].strip():
            cuerpo.pop()
        self.partes.append(f"```{{r{opciones}}}\n" + "\n".join(cuerpo) + "\n```\n")

    def pasos(self, secs, nivel, prefijo, inicio=1):
        for i, (titulo, lineas) in enumerate(secs, inicio):
            self.texto(f"{'#' * nivel} {prefijo}{i}. {titulo[0].upper()}{titulo[1:]}")
            explicacion = next((t for clave, t in TEXTOS if titulo.startswith(clave)), "")
            if explicacion:
                self.texto(explicacion)
            self.chunk(lineas)


def rmd(nombre, titulo, subtipo, scripts, conclusion):
    d = Documento()
    d.texto(f'---\ntitle: "Análisis estadístico de la variable {subtipo}: {titulo}"\n'
            f'subtitle: "Geoquímica de rocas con datos de EarthChem PetDB · Estadística y Probabilidades, FIGEMPA – UCE"\n'
            f'author: "{AUTORES}"\ndate: "Noviembre de 2026"\n'
            "output:\n  html_document:\n    toc: true\n    toc_float: true\n    theme: flatly\n    highlight: tango\n---")
    d.texto("> Proyecto estrictamente académico. Datos: EarthChem PetDB (CC BY 4.0), descargados el 13/10/2026. "
            "Web del proyecto: https://crisrumiguano-art.github.io/geoquimica-earthchem-ml/")
    d.texto("## 1. Carga de datos y librerías")
    d.texto("Se lee la base limpia (159 760 análisis de roca total × 75 variables). La primera vez se descarga del "
            "repositorio del proyecto (26 MB).")
    d.chunk(["knitr::opts_chunk$set(",
             "  echo = TRUE,          # muestra el código en el documento",
             "  message = FALSE,      # sin mensajes de carga de paquetes",
             "  warning = FALSE,      # sin advertencias",
             "  fig.align = \"center\" # gráficos centrados",
             ")",
             "library(e1071)         # asimetría y curtosis (install.packages(\"e1071\"))",
             "if (!file.exists(\"data/earthchem_limpio.csv.gz\")) {",
             "  dir.create(\"data\", showWarnings = FALSE)",
             "  download.file(\"https://github.com/crisrumiguano-art/geoquimica-earthchem-ml/raw/main/data/earthchem_limpio.csv.gz\",",
             "                \"data/earthchem_limpio.csv.gz\", mode = \"wb\")",
             "}",
             "base <- read.csv(gzfile(\"data/earthchem_limpio.csv.gz\", encoding = \"UTF-8\"), check.names = FALSE)",
             "dim(base)              # filas y columnas"])
    principal = secciones(scripts[0])
    d.pasos(principal, 2, "", 2)  # la sección 1 es la carga de datos
    n = 1 + len(principal)
    if len(scripts) == 1:
        resumen = ("res <- list(moda = categoria[which.max(ni)], hi_max = max(hi), n = sum(ni), k = length(ni))"
                   if subtipo.startswith("cualitativa") else
                   "res <- list(n = n, media = mean(x), mediana = median(x), cv = sd(x) / mean(x) * 100,\n"
                   "            asim = skewness(x), fuera = abajo + arriba,\n"
                   "            moda = as.numeric(names(which.max(table(x)))))")
    else:
        resumen = ("res <- list(n = n, media = mean(x), mediana = median(x), cv = sd(x) / mean(x) * 100,\n"
                   "            asim = skewness(x), fuera = abajo + arriba,\n"
                   "            err = abs(media_agrupada - mean(xc)) / mean(xc) * 100)")
    d.chunk(["f <- function(v, d = 2) format(round(v, d), big.mark = if (abs(v) >= 10000) \" \" else \"\", decimal.mark = \",\")",
             resumen],
            ", include = FALSE")
    if len(scripts) > 1:
        n += 1
        d.texto(f"## {n}. Corrección de la agrupación")
        d.texto("Con Sturges sobre todo el rango, los valores extremos estiran los intervalos y casi todos los datos "
                "caen en uno o dos. Por eso la TDF de arriba usa el rango típico (sin outliers) y clases abiertas.")
        d.pasos([s for s in secciones(scripts[1]) if s[0].startswith(("TDF", "Gráfico: por defecto"))], 3, f"{n}.")
        n += 1
        d.texto(f"## {n}. Estrato: rocas volcánicas máficas")
        d.texto("El mismo análisis para un solo tipo de roca (basaltos y afines). Al separar por estrato, la "
                "distribución deja de mezclar rocas distintas.")
        d.pasos(secciones(scripts[2]), 3, f"{n}.")
    n += 1
    d.texto(f"## {n}. Conclusión")
    if subtipo.startswith("cualitativa"):
        d.texto("La categoría más frecuente (moda) es **`r res$moda`**, con el `r f(res$hi_max)` % de los "
                "`r f(res$n, 0)` casos con dato, repartidos en `r res$k` categorías. " + conclusion)
    else:
        log = "Cr" in titulo
        valor = "10^res$mediana" if log else "res$mediana"
        unidad = " ppm" if log else (" años" if "Año" in titulo else (" analitos" if "analitos" in titulo else " %"))
        texto = (f"Se analizaron `r f(res$n, 0)` casos con dato. La mediana es `r f({valor})`{unidad}"
                 + ("; en log10, la escala del análisis," if log else ";") +
                 " la asimetría es `r f(res$asim)` (`r if (res$asim > 0) \"cola hacia los valores altos\" else "
                 "\"cola hacia los valores bajos\"`) y el coeficiente de variación es `r f(res$cv)` %. ")
        if len(scripts) > 1:
            texto += ("`r f(res$fuera, 0)` datos quedaron en las clases abiertas: no se borraron, porque son otras "
                      "rocas y no errores. El error de agrupación de la media es `r f(res$err)` %. ")
        else:
            texto += "La moda es `r res$moda`. "
        d.texto(texto + conclusion)
    return "\n".join(d.partes)


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
    print(f"{len(DOCUMENTOS)} Rmd -> {RMD}; HTML -> {HTML}")


if __name__ == "__main__":
    main()
