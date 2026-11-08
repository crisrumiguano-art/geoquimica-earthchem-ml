"""Código R de cada gráfico de la web, en versión SIMPLE (paso a paso, sin funciones propias).

Salidas:
  docs/data/codigo_r.json   lo que muestra el botón «Código R» de cada gráfica (app.js)
  R/graficos/NN_*.R         el mismo código, un archivo por gráfico, para abrir en RStudio

El código de cada gráfico sale de las plantillas de scripts/codigo_simple.py; el de muestreo es R/04_muestreo.R.
Volver a correr después de tocar R/ o las plantillas.   Uso: python scripts/codigo_r.py
"""
import json
from pathlib import Path

from codigo_simple import simple

RAIZ = Path(__file__).resolve().parent.parent
R = RAIZ / "R"
IMG = RAIZ / "docs" / "img" / "r"
SALIDA = RAIZ / "docs" / "data" / "codigo_r.json"
CARPETA = R / "graficos"
# Orden y nombre de archivo como aparecen en la página Descriptiva
ORDEN = [
    ("cual_grupo_tectonico.png", "01_cualitativa_ambiente_tectonico.R"),
    ("cual_tipo_de_roca.png", "02_cualitativa_tipo_de_roca.R"),
    ("cual_clase_sio2.png", "03_cualitativa_clase_SiO2.R"),
    ("cual_alteracion.png", "04_cualitativa_grado_de_alteracion.R"),
    ("disc_anio.png", "05_discreta_anio_de_publicacion.R"),
    ("disc_analitos.png", "06_discreta_numero_de_analitos.R"),
    ("SiO2_agrupacion.png", "07_continua_SiO2_agrupacion_por_defecto_vs_corregida.R"),
    ("SiO2_toda_la_muestra.png", "08_continua_SiO2_toda_la_muestra.R"),
    ("SiO2_estrato_mafico.png", "09_continua_SiO2_rocas_volcanicas_maficas.R"),
    ("MgO_agrupacion.png", "10_continua_MgO_agrupacion_por_defecto_vs_corregida.R"),
    ("MgO_toda_la_muestra.png", "11_continua_MgO_toda_la_muestra.R"),
    ("MgO_estrato_mafico.png", "12_continua_MgO_rocas_volcanicas_maficas.R"),
    ("Cr_agrupacion.png", "13_continua_Cr_agrupacion_por_defecto_vs_corregida.R"),
    ("Cr_toda_la_muestra.png", "14_continua_Cr_toda_la_muestra.R"),
    ("Cr_estrato_mafico.png", "15_continua_Cr_rocas_volcanicas_maficas.R"),
]


def main():
    pngs = {p.name for p in IMG.glob("*.png")}
    assert {p for p, _ in ORDEN} | {p for p in pngs if p.startswith("muestreo_")} == pngs, "falta o sobra un gráfico en ORDEN"
    codigo = {}
    CARPETA.mkdir(exist_ok=True)
    for viejo in CARPETA.glob("*.R"):
        viejo.unlink()
    for png, archivo in ORDEN:
        codigo[png] = simple(png)
        (CARPETA / archivo).write_text(codigo[png], encoding="utf-8")
    muestreo = (R / "04_muestreo.R").read_text(encoding="utf-8")
    for png in sorted(p for p in pngs if p.startswith("muestreo_")):
        codigo[png] = muestreo  # los dos gráficos salen del mismo cálculo: se muestra el script entero
    codigo["05_paso_a_paso.R"] = (R / "05_paso_a_paso.R").read_text(encoding="utf-8")
    SALIDA.write_text(json.dumps(codigo, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{len(codigo)} códigos -> {SALIDA}; {len(ORDEN)} archivos -> {CARPETA}")


if __name__ == "__main__":
    main()
