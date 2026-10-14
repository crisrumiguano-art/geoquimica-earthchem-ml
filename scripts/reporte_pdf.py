"""Genera docs/reporte_base_datos.pdf: descripción de la base para el equipo.

Uso: python scripts/reporte_pdf.py
"""
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from datos_dashboard import TIPOS

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", FUENTES / "arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FUENTES / "arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", FUENTES / "ariali.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

ss = getSampleStyleSheet()
CUERPO = ParagraphStyle("c", parent=ss["Normal"], fontName="Arial", fontSize=10.5, leading=15,
                        alignment=TA_JUSTIFY, spaceAfter=7)
TITULO = ParagraphStyle("t", parent=CUERPO, fontName="Arial-Bold", fontSize=19, leading=24, alignment=0, spaceAfter=4)
SUB = ParagraphStyle("s", parent=CUERPO, fontSize=10, textColor=colors.HexColor("#52514e"), alignment=0)
H2 = ParagraphStyle("h", parent=CUERPO, fontName="Arial-Bold", fontSize=13, leading=17, spaceBefore=12,
                    spaceAfter=6, alignment=0, textColor=colors.HexColor("#1c5cab"))
CELDA = ParagraphStyle("x", parent=CUERPO, fontSize=8.5, leading=11, alignment=0, spaceAfter=0)


def p(texto, estilo=CUERPO):
    return Paragraph(texto, estilo)


def tabla(filas, anchos):
    t = Table([[p(f"<b>{c}</b>" if i == 0 else str(c), CELDA) for c in f] for i, f in enumerate(filas)], colWidths=anchos, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f0fb")),
        ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#d5d4cc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def miles(n):
    return f"{n:,}".replace(",", ".")


def main():
    df = pd.read_csv(RAIZ / "data" / "earthchem_limpio.csv.gz", low_memory=False)
    n, ncol = df.shape
    mayores = ["SiO2 (wt%)", "Al2O3 (wt%)", "MgO (wt%)", "CaO (wt%)", "Na2O (wt%)", "K2O (wt%)"]
    completos = int(df[mayores].notna().all(axis=1).sum())
    articulos = df["Citation"].nunique()
    geo = df["Geographic Features"].fillna("")
    oceano = geo.str.contains("OCEAN").mean()
    tec = df["Tectonic Setting"].value_counts()
    sub = df["Sample SubType"].value_counts()
    reciente = (df["Publication Year"] >= 2000).mean()

    h = []
    h += [p("Base de datos de geoquímica de rocas", TITULO),
          p("Descripción, origen y preparación de la base EarthChem / PetDB usada en el proyecto de "
            "estadística y machine learning · octubre de 2026", SUB), Spacer(1, 10)]

    h += [p("1. Qué es esta base", H2), p(
        f"La base reúne {miles(n)} análisis químicos de rocas tomados de muestras recolectadas en todo el "
        "mundo. Cada fila corresponde al análisis de una muestra de <i>roca total</i>, es decir, de la roca "
        "molida y medida en conjunto, no de un mineral en particular. Para cada muestra se informa su "
        "composición en elementos mayores (sílice, aluminio, magnesio, calcio, sodio, potasio y otros, "
        "expresados como óxidos en porcentaje en peso), en elementos traza (en partes por millón) y en "
        "tierras raras, junto con información sobre el tipo de roca, el lugar donde se tomó, el ambiente "
        "geológico en que se formó y el artículo científico que publicó el dato."), p(
        f"Predominan las rocas ígneas, y en particular los basaltos ({miles(sub.get('BASALT', 0))} análisis), "
        f"seguidos por peridotitas, tefras, harzburgitas, diabasas, lherzolitas, gabros y andesitas. "
        f"Cerca de {oceano:.0%} de las muestras proviene del fondo oceánico, lo que se explica por el "
        "origen de la base: PetDB nació para reunir los datos de las dorsales oceánicas y de las "
        "perforaciones de los programas internacionales de exploración del océano (DSDP, ODP e IODP).")]

    h += [p("2. De dónde salieron los datos", H2), p(
        "Los datos provienen de <b>PetDB</b> (<i>Petrological Database</i>), una de las bases que integran "
        "<b>EarthChem</b>, la infraestructura de datos geoquímicos financiada por la National Science "
        "Foundation de Estados Unidos. Hoy PetDB se consulta a través de la <i>Astromaterials Data "
        "Synthesis</i> (search.astromat.org) y del portal de EarthChem (www.earthchem.org/petdb)."), p(
        f"PetDB no genera datos propios: su equipo los transcribe de artículos científicos revisados por "
        f"pares y los ordena en un formato común. La exportación usada aquí reúne datos de "
        f"{miles(articulos)} artículos publicados entre {int(df['Publication Year'].min())} y "
        f"{int(df['Publication Year'].max())}; algo más de la mitad ({reciente:.0%}) corresponde a "
        "trabajos publicados desde el año 2000. Cada fila conserva la cita completa del artículo de origen "
        "y un enlace a la ficha de la muestra en PetDB, de modo que cualquier valor se puede rastrear "
        "hasta su publicación."), p(
        "La descarga se hizo el <b>13 de octubre de 2026</b> desde el buscador de PetDB, con un único filtro: "
        "material analizado igual a <i>roca total</i> (incluyendo el material registrado como "
        "<i>roca total o vidrio sin especificar</i>). Se pidieron todas las familias de variables "
        "disponibles: elementos mayores, trazas, tierras raras, edades, miembros extremos, moda mineral, "
        "gases nobles y volátiles. La dirección exacta de la consulta quedó guardada en el repositorio, "
        "así que la descarga se puede repetir."), p(
        "Archivo de la consulta: <font face='Courier'>data/raw/earthchem_export_oct13_26_142339.txt</font>", SUB), p(
        "Los datos se distribuyen bajo licencia <b>Creative Commons Atribución 4.0 (CC BY 4.0)</b>: pueden "
        "usarse, transformarse y redistribuirse libremente siempre que se cite la fuente.")]

    h += [p("3. Cómo se preparó", H2), p(
        "La exportación original venía en dos archivos que suman unos 600 MB: uno con los resultados "
        "químicos, de 2.318 columnas, y otro con los datos descriptivos de cada muestra (ubicación, "
        "ambiente tectónico, textura, alteración, edad). Las columnas son tantas porque cada variable "
        "química viene acompañada de tres columnas de texto que indican el método analítico, un "
        "comentario sobre el método y el laboratorio. Esa información es valiosa para un especialista, "
        "pero para el análisis estadístico solo agrega ruido."), p(
        "La preparación consistió en: (a) unir los dos archivos, verificando que las muestras coincidieran "
        "fila por fila; (b) quitar las columnas de método, comentario y laboratorio; (c) conservar solo "
        "las variables químicas que tienen datos en al menos el 5 % de las muestras, lo que deja 52 "
        "variables y descarta, entre otras, las relaciones isotópicas, que aparecen en menos del 2 % de "
        "las filas; (d) convertir las coordenadas a grados decimales, con el sur y el oeste en negativo; "
        "y (e) dejar vacía, y no en cero, toda celda química sin medición. Además se construyeron cuatro "
        "variables nuevas, descritas en la sección siguiente. Todo el proceso está escrito en "
        "<font face='Courier'>scripts/limpiar.py</font> y se puede volver a ejecutar sobre los archivos originales.")]

    h += [p("4. Variables", H2), p(
        f"La base final tiene <b>{miles(n)} filas y {ncol} columnas</b>. Las variables cubren todos los tipos "
        "que se usan en estadística:"), tabla([
        ["Tipo", "Variables", "Comentario"],
        ["Nominales", "Sample Type, Sample SubType, Tectonic Setting, Geographic Features, Rock Texture, "
                      "Geologic Age, Expedition, Citation, Sample Alteration",
         f"Categorías sin orden. Por ejemplo, el ambiente tectónico tiene {df['Tectonic Setting'].nunique()} "
         f"valores y el subtipo de roca {df['Sample SubType'].nunique()}."],
        ["Nominal binaria", "Analyzed Material", "Solo dos valores: roca total y roca total o vidrio sin especificar."],
        ["Ordinales", "SiO2 Class, Alteration Grade",
         "Construidas para el proyecto. SiO2 Class clasifica la roca por su contenido de sílice: ultrabásica "
         "(menos de 45 %), básica (45–52 %), intermedia (52–63 %) y ácida (63 % o más). Alteration Grade "
         "traduce la alteración informada a una escala de 0 (fresca) a 5 (totalmente alterada)."],
        ["Numéricas discretas", "Publication Year, N Analytes",
         "Solo toman valores enteros. El año sale de la cita; N Analytes cuenta cuántas variables químicas "
         f"se midieron en la muestra (mediana: {int(df['N Analytes'].median())})."],
        ["Numéricas continuas", "52 variables químicas, Latitude, Longitude, elevación mínima y máxima, edad "
                                "máxima y mínima (Ma)",
         "Óxidos mayores en % en peso (wt%); trazas y tierras raras en partes por millón (ppm)."],
        ["Identificadores", "Sample Name, Sample URL", "No se analizan; sirven para rastrear cada muestra."],
    ], [3.2 * cm, 6.3 * cm, 7.5 * cm]), Spacer(1, 6), p(
        "El diccionario completo, con el tipo de cada columna y el porcentaje de filas con dato, está en el anexo.")]

    h += [p("5. Requisitos del trabajo", H2), tabla([
        ["Requisito", "Exigido", "Base"],
        ["Filas", "al menos 10.000", miles(n)],
        ["Columnas", "al menos 30", str(ncol)],
        ["Tipos de variables", "nominales, ordinales, discretas y continuas", "todos presentes (sección 4)"],
    ], [5 * cm, 6 * cm, 6 * cm])]

    h += [p("6. Limitaciones que conviene conocer", H2), p(
        f"<b>No todas las muestras tienen todas las mediciones.</b> Cada artículo midió lo que necesitaba "
        f"para su investigación, por lo que la base tiene muchos huecos. Solo {miles(completos)} filas "
        f"({completos / n:.0%}) tienen completos los seis óxidos principales (SiO2, Al2O3, MgO, CaO, Na2O y "
        "K2O), y las tierras raras aparecen en una de cada cinco filas. Hay incluso filas sin ninguna "
        "variable química, porque en ellas solo se informó la edad o la moda mineral. Una celda vacía "
        "significa que el valor no se midió, no que valga cero; conviene filtrar las filas completas para "
        "cada análisis en lugar de rellenar los huecos sin criterio."), p(
        "<b>Falta el TiO2.</b> El óxido de titanio, uno de los elementos mayores más usados para "
        "clasificar basaltos, prácticamente no vino en la exportación (cuatro valores en total). Si el "
        "análisis lo requiere, habrá que volver a descargarlo desde PetDB."), p(
        "<b>Unidades y formas distintas para un mismo elemento.</b> Níquel, cobalto, cobre y zinc aparecen "
        "tanto en % en peso como en ppm (1 % equivale a 10.000 ppm), y el hierro se informa de cuatro "
        "maneras (FeO, Fe2O3, FeOT y Fe2O3T). Antes de comparar hay que llevar todo a una misma unidad."), p(
        f"<b>Sesgos de origen.</b> Los datos reflejan lo que la comunidad científica decidió estudiar y "
        f"publicar a lo largo de casi un siglo: hay muchos más basaltos de fondo oceánico que rocas "
        f"continentales, y los métodos de laboratorio cambiaron con el tiempo. El ambiente tectónico más "
        f"frecuente, <i>{tec.index[0].lower()}</i>, reúne {miles(int(tec.iloc[0]))} muestras, mientras "
        "que otros tienen apenas unas decenas; algunas categorías además combinan dos ambientes y "
        "conviene agruparlas antes de usarlas como clases en un modelo."), p(
        "<b>Información descriptiva incompleta.</b> La ubicación está prácticamente siempre, pero la edad "
        "geológica figura solo en alrededor del 10 % de las muestras y la alteración en una de cada cinco.")]

    h += [p("7. Acceso y cita", H2), p(
        "La base limpia está en el repositorio del proyecto, en "
        "<font face='Courier'>data/earthchem_limpio.csv.gz</font> (github.com/DalemberV/geoquimica-earthchem-ml). "
        "El archivo está comprimido; para abrirlo en Excel hay que descomprimirlo primero (por ejemplo con "
        "7-Zip) e importarlo desde <i>Datos &gt; Desde texto/CSV</i> con codificación UTF-8 y configuración "
        "regional Inglés (Estados Unidos), para que el punto se lea como separador decimal. La página "
        "dalemberv.github.io/geoquimica-earthchem-ml muestra un resumen visual de los datos."), p(
        "Cita sugerida: <i>Datos descargados de EarthChem PetDB / Astromaterials Data Synthesis "
        "(https://search.astromat.org/) el 13 de octubre de 2026, con los parámetros: material analizado = "
        "roca total; variables = elementos mayores, trazas, tierras raras, edades, miembros extremos, moda, "
        "gases nobles y volátiles. Licencia CC BY 4.0.</i>")]

    h += [p("Anexo. Diccionario de variables", H2), tabla(
        [["Columna", "Tipo", "% con dato"]]
        + [[c, TIPOS.get(c, "continua"), f"{100 * df[c].notna().mean():.1f}".replace(".", ",")] for c in df.columns],
        [7 * cm, 6 * cm, 3 * cm])]

    def pie(canvas, doc):
        canvas.setFont("Arial", 8)
        canvas.setFillColor(colors.HexColor("#898781"))
        canvas.drawString(2 * cm, 1.2 * cm, "Base de datos de geoquímica de rocas · EarthChem / PetDB")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, str(doc.page))

    salida = RAIZ / "docs" / "reporte_base_datos.pdf"
    SimpleDocTemplate(str(salida), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm,
                      bottomMargin=2 * cm, title="Base de datos de geoquímica de rocas",
                      author="Equipo del proyecto").build(h, onFirstPage=pie, onLaterPages=pie)
    print(salida)


if __name__ == "__main__":
    main()
