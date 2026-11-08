"""Código R de cada gráfico de la web -> docs/data/codigo_r.json (lo muestra el botón «Código R» de app.js).

Para cada PNG de docs/img/r/ junta el script de R/ que lo genera y las funciones de R/funciones.R que ese
script usa (también las que llaman esas funciones), en el orden del archivo. Así el código que se ve en la web
es exactamente el que corrió. Volver a correr después de tocar cualquier archivo de R/.

Uso: python scripts/codigo_r.py
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
R = RAIZ / "R"
IMG = RAIZ / "docs" / "img" / "r"
SALIDA = RAIZ / "docs" / "data" / "codigo_r.json"
SOURCE = 'source("R/funciones.R")'
BASE_URL = "https://github.com/crisrumiguano-art/geoquimica-earthchem-ml/raw/main/data/earthchem_limpio.csv.gz"
# Prefijo del PNG -> script que lo genera.
SCRIPTS = [("cual_", "01_cualitativas.R"), ("disc_", "02_discretas.R"), ("muestreo_", "04_muestreo.R"),
           ("", "03_continuas.R")]  # SiO2_agrupacion.png, MgO_toda_la_muestra.png, ...


# ----------------------------------------------------------------------------------------------- un gráfico
# Los scripts 01-03 hacen varios gráficos en un bucle. Para la web se arma, por gráfico, solo lo que lo produce,
# con los mismos argumentos que usa el bucle (título, número de gráfica, unidad); así el PNG sale idéntico.
CUAL = {  # archivo -> (cómo obtener x, título, orden, número de gráfica)
    "grupo_tectonico": ('x <- base[["Tectonic Group"]]                      # columna: ambiente tectónico agrupado',
                        "Ambiente tectónico agrupado", "NULL", 1),
    "tipo_de_roca": ('x <- base[["Sample Type"]]                         # columna: tipo de roca\n'
                     'frec <- prop.table(table(x))                       # proporción de cada tipo\n'
                     'x[x %in% names(frec[frec < 0.01])] <- "otros"      # los de menos de 1 % -> "otros"',
                     "Tipo de roca", "NULL", 3),
    "clase_sio2": ('x <- base[["SiO2 Class"]]                          # columna: clase según SiO2',
                   "Clase de roca según SiO2", 'c("ultrabasica", "basica", "intermedia", "acida")', 5),
    "alteracion": ('x <- factor(base[["Alteration Grade"]], levels = 0:5,   # códigos 0-5 -> nombres\n'
                   '            labels = c("0 fresca", "1 leve", "2 moderada", "3 extensa", "4 casi total", "5 total"))',
                   "Grado de alteración", 'c("0 fresca", "1 leve", "2 moderada", "3 extensa", "4 casi total", "5 total")', 7),
}
DISC = {"anio": ("Publication Year", "Año de publicación", "año", 1),
        "analitos": ("N Analytes", "Número de analitos", "analitos", 4)}
CONT = {"SiO2": ("SiO2 (wt%)", "wt%", False, 1), "MgO": ("MgO (wt%)", "wt%", False, 7), "Cr": ("Cr (ppm)", "ppm", True, 13)}


def fragmento(png):
    """Código R que produce solo este PNG (sin bucle). None si se muestra el script entero (muestreo)."""
    nombre = png.removesuffix(".png")
    lineas = ["base <- leer_base()                                  # lee la base completa"]
    if nombre.startswith("cual_"):
        obtener, titulo, orden, n = CUAL[nombre[5:]]
        lineas += [obtener,
                   f"tdf <- tdf_cualitativa(as.character(x), orden = {orden})   # tabla de frecuencias"
                   + ("  (NULL = nominal)" if orden == "NULL" else "  (ordinal: con su orden)"),
                   "print(tdf)                                           # muestra la tabla",
                   f'graficos_cualitativa(tdf, "{titulo}", "{png}", n_graf = {n})   # barras + circular -> PNG']
    elif nombre.startswith("disc_"):
        col, titulo, unidad, n = DISC[nombre[5:]]
        lineas += [f'x <- base[["{col}"]]', "x <- x[!is.na(x)]                                    # quita vacíos",
                   "tdf <- tdf_continua(x)                               # TDF (Sturges, amplitud redonda)",
                   "print(tdf)",
                   f'graficos_continua(x, tdf, "{titulo}", "{unidad}", "{png}", n_graf = {n})   # histograma, ojiva, caja']
    elif nombre.startswith("muestreo_"):
        return None
    else:
        var, parte = nombre.split("_", 1)
        col, unidad, log, n = CONT[var]
        rotulo = f"log10 {var}" if log else var
        lineas += [f'x <- base[["{col}"]]', "x <- x[!is.na(x)]                                    # quita vacíos",
                   "esc <- log10(x)                                      # escala log10 (10, 100, 1000 -> 1, 2, 3)" if log
                   else "esc <- x                                             # escala original",
                   "lim <- limites_iqr(esc)                              # límites de outliers (regla IQR)"]
        if parte == "agrupacion":
            lineas += ["tdf_def <- tdf_continua(x, redondear = FALSE)        # TDF por defecto (como la plantilla)",
                       "tdf_todo <- tdf_continua(esc, lim = lim)             # TDF corregida: rango típico + clases abiertas",
                       f'comparar_agrupacion(tdf_def, tdf_todo, "{var}", "{"log10 " + unidad if log else unidad}", "{png}")   # los dos histogramas']
        elif parte == "toda_la_muestra":
            lineas += ["tdf <- tdf_continua(esc, lim = lim)                  # TDF corregida",
                       "print(tdf)",
                       f'graficos_continua(esc, tdf, "{rotulo}", "{unidad}", "{png}", n_graf = {n})   # histograma, ojiva, caja']
        else:  # estrato_mafico
            lineas += [f'tipo <- base[["Sample Type"]][!is.na(base[["{col}"]])]   # tipo de roca de cada valor',
                       'ee <- esc[tipo == "igneous:volcanic:mafic"]          # solo rocas volcánicas máficas',
                       "tdf <- tdf_continua(ee, lim = limites_iqr(ee))       # TDF del grupo",
                       "print(tdf)",
                       f'graficos_continua(ee, tdf, "{rotulo} en rocas volcánicas máficas", "{unidad}", "{png}", n_graf = {n + 3})']
    return "\n".join(lineas)


def funciones(texto):
    """{nombre: código} de cada `nombre <- function(...) { ... }` de primer nivel, en orden."""
    out, lineas, i = {}, texto.splitlines(), 0
    while i < len(lineas):
        m = re.match(r"^([A-Za-z_][\w.]*) <- function\b", lineas[i])
        if not m:
            i += 1
            continue
        j, nivel = i, 0
        while True:  # hasta cerrar la llave que abre la función
            nivel += lineas[j].count("{") - lineas[j].count("}")
            if nivel == 0 and "{" in "".join(lineas[i:j + 1]):
                break
            j += 1
        comentario = i
        while comentario > 0 and lineas[comentario - 1].startswith("#") and not lineas[comentario - 1].startswith("# ---"):
            comentario -= 1
        out[m.group(1)] = "\n".join(lineas[comentario:j + 1])
        i = j + 1
    return out


def usadas(texto, todas):
    """Nombres de `todas` que aparecen en `texto`, con sus dependencias."""
    pendientes, vistas = [texto], set()
    while pendientes:
        t = pendientes.pop()
        for nombre in todas:
            if nombre not in vistas and re.search(rf"\b{re.escape(nombre)}\(", t):
                vistas.add(nombre)
                pendientes.append(todas[nombre])
    return [n for n in todas if n in vistas]  # en el orden de funciones.R


def main():
    todas = funciones((R / "funciones.R").read_text(encoding="utf-8"))
    cabecera = "\n".join(l for l in (R / "funciones.R").read_text(encoding="utf-8").splitlines()[:30]
                         if l.startswith(("library(", ".libPaths", "SALIDAS", "GRAFICOS", "TABLAS_WEB", "for (d")))
    codigo = {}
    for png in sorted(IMG.glob("*.png")):
        script = next(s for prefijo, s in SCRIPTS if png.name.startswith(prefijo))
        propio = fragmento(png.name)
        if propio:  # solo lo de este gráfico
            texto, titulo2 = propio, f"Lo que arma ESTE gráfico (en el repo está dentro del bucle de R/{script})"
        else:       # muestreo: el script entero, sus gráficos salen del mismo cálculo
            texto = (R / script).read_text(encoding="utf-8").rstrip()
            assert SOURCE in texto, script
            texto = texto.replace(SOURCE, '# source("R/funciones.R")   <- no hace falta: las funciones ya están arriba', 1)
            titulo2 = f"Script R/{script}"
        nombres = usadas(texto, todas)
        # Versión autónoma: se puede copiar y correr en cualquier carpeta. Las funciones van ANTES del código
        # que las usa (R las necesita definidas antes).
        codigo[png.name] = (
            f"# Gráfico: {png.name}\n"
            "# Código COMPLETO de este gráfico: copiar todo en RStudio y ejecutar (Ctrl + A, Ctrl + Enter).\n"
            "#   Partes: 0 = descarga la base (solo la primera vez), 1 = funciones que usa, 2 = lo que dibuja el gráfico.\n"
            "#   Antes: Session > Set Working Directory > una carpeta cualquiera.\n"
            f"#   El gráfico queda en docs/img/r/{png.name} dentro de esa carpeta.\n"
            "# Las líneas con # son explicaciones: R no las ejecuta.\n\n"
            "# ============ 0. Base de datos (solo se descarga si no está) ============\n"
            'dir.create("data", showWarnings = FALSE)\n'
            'if (!file.exists("data/earthchem_limpio.csv.gz"))\n'
            f'  download.file("{BASE_URL}",\n'
            '                "data/earthchem_limpio.csv.gz", mode = "wb")   # mode = "wb": archivo binario\n\n'
            "# ============ 1. Funciones (de R/funciones.R) ============\n"
            f"{cabecera}\n\n" + "\n\n".join(todas[n] for n in nombres) + "\n\n"
            f"# ============ 2. {titulo2} ============\n{texto}\n")
    # Script completo sin funciones propias, con el estilo de la plantilla (sección «Cómo leer el código R»).
    codigo["05_paso_a_paso.R"] = (R / "05_paso_a_paso.R").read_text(encoding="utf-8")
    SALIDA.write_text(json.dumps(codigo, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{len(codigo)} gráficos -> {SALIDA}")


if __name__ == "__main__":
    t = "a <- function(x) {\n  b(x)\n}\n# hace b\nb <- function(y) {\n  if (y) {\n    1\n  }\n}\n"
    f = funciones(t)
    assert list(f) == ["a", "b"] and f["b"].startswith("# hace b") and f["b"].endswith("}"), f
    assert usadas("a(1)", f) == ["a", "b"] and usadas("nada", f) == []
    main()
