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
# Prefijo del PNG -> script que lo genera.
SCRIPTS = [("cual_", "01_cualitativas.R"), ("disc_", "02_discretas.R"), ("muestreo_", "04_muestreo.R"),
           ("", "03_continuas.R")]  # SiO2_agrupacion.png, MgO_toda_la_muestra.png, ...


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
    cabecera = "\n".join(l for l in (R / "funciones.R").read_text(encoding="utf-8").splitlines()[:20]
                         if l.startswith(("library(", ".libPaths", "SALIDAS", "GRAFICOS", "TABLAS_WEB", "for (d")))
    codigo = {}
    for png in sorted(IMG.glob("*.png")):
        script = next(s for prefijo, s in SCRIPTS if png.name.startswith(prefijo))
        texto = (R / script).read_text(encoding="utf-8").rstrip()
        nombres = usadas(texto, todas)
        codigo[png.name] = (
            f"# Gráfico: {png.name}\n# Lo genera R/{script}; correr desde la raíz del repositorio:  Rscript R/{script}\n\n"
            f"# ======================= R/{script} =======================\n{texto}\n\n"
            f"# =========== Funciones de R/funciones.R que usa (source(\"R/funciones.R\")) ===========\n"
            f"{cabecera}\n\n" + "\n\n".join(todas[n] for n in nombres) + "\n")
    SALIDA.write_text(json.dumps(codigo, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{len(codigo)} gráficos -> {SALIDA}")


if __name__ == "__main__":
    t = "a <- function(x) {\n  b(x)\n}\n# hace b\nb <- function(y) {\n  if (y) {\n    1\n  }\n}\n"
    f = funciones(t)
    assert list(f) == ["a", "b"] and f["b"].startswith("# hace b") and f["b"].endswith("}"), f
    assert usadas("a(1)", f) == ["a", "b"] and usadas("nada", f) == []
    main()
