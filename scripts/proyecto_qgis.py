"""Crea data/gis/mapa_ubicacion.qgz: proyecto QGIS con las capas de mapa_ubicacion.gpkg, la misma
simbología del mapa de la web y una composición de impresión con el formato de la plantilla del docente
(marco, cuadrícula con coordenadas, leyenda, norte, escala gráfica y membrete con logo UCE).

Requiere QGIS. Ejecutar con su Python (no con el Python normal), después de scripts/mapa.py:
    "C:\\Program Files\\QGIS 3.44.8\\bin\\python-qgis-ltr.bat" scripts/proyecto_qgis.py
"""
import sys
from datetime import date
from pathlib import Path

from qgis.core import (
    QgsApplication, QgsCategorizedSymbolRenderer, QgsCoordinateReferenceSystem, QgsFillSymbol,
    QgsLayoutExporter, QgsLayoutItemLabel, QgsLayoutItemLegend, QgsLayoutItemMap, QgsLayoutItemMapGrid,
    QgsLayoutItemPicture, QgsLayoutItemScaleBar, QgsLayoutItemShape, QgsLayoutPoint, QgsLayoutSize, QgsLegendStyle,
    QgsLineSymbol, QgsMarkerSymbol, QgsPrintLayout, QgsProject, QgsRectangle, QgsRendererCategory, QgsTextFormat,
    QgsUnitTypes, QgsVectorLayer,
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QFont

RAIZ = Path(__file__).resolve().parent.parent
GIS = RAIZ / "data" / "gis"
GPKG = GIS / "mapa_ubicacion.gpkg"
LOGO = GIS / "UCE.png"  # copiado de referencias_curso/QGIS/1.- Mapa de Ubicacion/UCE.png
WGS84 = QgsCoordinateReferenceSystem("EPSG:4326")
GRUPOS = [("dorsal y corteza oceanica", "Dorsal y corteza oceánica", "#2a78d6"),
          ("intraplaca y rift", "Intraplaca y rift", "#1baf7a"),
          ("margen convergente", "Margen convergente", "#eb6834"),
          ("mixto", "Mixto", "#898781")]
AUTORES = "Rumiguano C., Fernández A., Bustamante E., Haro J., Ligña J."
MM = QgsUnitTypes.LayoutMillimeters


def capa(nombre):
    c = QgsVectorLayer(f"{GPKG}|layername={nombre}", nombre, "ogr")
    assert c.isValid(), nombre
    return c


def formato(tam, negrita=False, color="#0b0b0b"):
    fuente = QFont("Arial")
    fuente.setBold(negrita)
    f = QgsTextFormat()
    f.setFont(fuente)
    f.setSize(tam)
    f.setColor(QColor(color))
    return f


def ubicar(layout, item, x, y, w=None, h=None):
    item.attemptMove(QgsLayoutPoint(x, y, MM))
    if w is not None:
        item.attemptResize(QgsLayoutSize(w, h, MM))
    layout.addLayoutItem(item)
    return item


def etiqueta(layout, texto, x, y, w, h, tam, negrita=False, color="#0b0b0b", centro=True):
    item = QgsLayoutItemLabel(layout)
    item.setText(texto)
    item.setTextFormat(formato(tam, negrita, color))
    if centro:
        item.setHAlign(Qt.AlignHCenter)
        item.setVAlign(Qt.AlignVCenter)
    return ubicar(layout, item, x, y, w, h)


def caja(layout, x, y, w, h, grosor=0.3):
    r = QgsLayoutItemShape(layout)
    r.setShapeType(QgsLayoutItemShape.Rectangle)
    r.setSymbol(QgsFillSymbol.createSimple({"style": "no", "outline_color": "#0b0b0b", "outline_width": str(grosor)}))
    return ubicar(layout, r, x, y, w, h)


def cuadricula(mapa):
    """Cuadrícula de 30° con las coordenadas en el borde (O/E, S/N) y marco cebra, como la plantilla del docente."""
    g = QgsLayoutItemMapGrid("Cuadrícula", mapa)
    g.setCrs(WGS84)
    g.setIntervalX(30)
    g.setIntervalY(30)
    g.setLineSymbol(QgsLineSymbol.createSimple({"line_color": "#9a9990", "line_width": "0.15"}))
    g.setFrameStyle(QgsLayoutItemMapGrid.Zebra)
    g.setFrameWidth(1.2)
    g.setAnnotationEnabled(True)
    g.setAnnotationFormat(QgsLayoutItemMapGrid.CustomFormat)
    g.setAnnotationExpression(
        "CASE WHEN abs(@grid_number) IN (90, 180) THEN '' "  # sin rótulos en las esquinas: se encimarían
        "ELSE concat(abs(@grid_number), '°', CASE WHEN @grid_number = 0 THEN '' WHEN @grid_axis = 'x' "
        "THEN if(@grid_number < 0, 'O', 'E') ELSE if(@grid_number < 0, 'S', 'N') END) END")
    g.setAnnotationTextFormat(formato(7))
    g.setAnnotationFrameDistance(1)
    for lado in (QgsLayoutItemMapGrid.Left, QgsLayoutItemMapGrid.Right, QgsLayoutItemMapGrid.Top,
                 QgsLayoutItemMapGrid.Bottom):
        g.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, lado)
        vertical = lado in (QgsLayoutItemMapGrid.Left, QgsLayoutItemMapGrid.Right)
        g.setAnnotationDirection(QgsLayoutItemMapGrid.Vertical if vertical else QgsLayoutItemMapGrid.Horizontal, lado)
    mapa.grids().addGrid(g)


def main(exportar_png=None):
    proyecto = QgsProject.instance()
    proyecto.setCrs(WGS84)  # geográficas: la cuadrícula toca el marco en los cuatro lados
    proyecto.setTitle("Mapa de ubicación — Geoquímica de rocas EarthChem PetDB")

    contorno, paises, muestras = (capa(n) for n in ("contorno", "paises", "muestras"))
    contorno.setName("Océanos")
    paises.setName("Países")
    muestras.setName("Muestras de roca total")
    contorno.setRenderer(contorno.renderer().__class__(QgsFillSymbol.createSimple(
        {"color": "#eaf2f8", "outline_style": "no"})))
    paises.setRenderer(paises.renderer().__class__(QgsFillSymbol.createSimple(
        {"color": "#dcdbd3", "outline_color": "#ffffff", "outline_width": "0.1"})))
    categorias = []
    for valor, texto, color in GRUPOS:
        n = sum(1 for _ in muestras.getFeatures(f"\"grupo_tec\" = '{valor}'"))
        simbolo = QgsMarkerSymbol.createSimple({"name": "circle", "color": color, "size": "0.6", "outline_style": "no"})
        simbolo.setOpacity(0.6)
        categorias.append(QgsRendererCategory(valor, simbolo, f"{texto} ({n:,})".replace(",", ".")))
    muestras.setRenderer(QgsCategorizedSymbolRenderer("grupo_tec", categorias))
    for c in (contorno, paises, muestras):  # el orden de agregado = de abajo hacia arriba
        proyecto.addMapLayer(c)

    # A4 horizontal. El mapa es mundial (2:1): va arriba a lo ancho, y leyenda, escala y membrete en una franja abajo.
    layout = QgsPrintLayout(proyecto)
    layout.initializeDefaults()
    layout.setName("Mapa de ubicación A4")
    proyecto.layoutManager().addLayout(layout)
    pagina = layout.pageCollection().page(0)
    pagina.setPageSize("A4", pagina.Landscape)
    caja(layout, 6, 6, 285, 198, 0.5)

    mapa = QgsLayoutItemMap(layout)
    mapa.setCrs(WGS84)
    mapa.setLayers([muestras, paises, contorno])
    mapa.setFrameEnabled(True)
    ubicar(layout, mapa, 17, 13, 264, 132)
    mapa.zoomToExtent(QgsRectangle(-180, -90, 180, 90))
    cuadricula(mapa)

    y0, alto = 154, 47
    # Leyenda
    caja(layout, 9, y0, 88, alto)
    etiqueta(layout, "LEYENDA", 9, y0 + 1.5, 88, 6, 11, True)
    leyenda = QgsLayoutItemLegend(layout)
    leyenda.setTitle("Ambiente tectónico (n.º de análisis)")
    leyenda.setLinkedMap(mapa)
    leyenda.setAutoUpdateModel(False)
    raiz = leyenda.model().rootGroup()
    for nodo in list(raiz.children()):
        if nodo.layerId() != muestras.id():
            raiz.removeChildNode(nodo)
    raiz.findLayer(muestras.id()).setCustomProperty("legend/title-style", "hidden")
    leyenda.rstyle(QgsLegendStyle.Title).setTextFormat(formato(8, True))
    leyenda.rstyle(QgsLegendStyle.SymbolLabel).setTextFormat(formato(8))
    leyenda.setMinimumSymbolSize(3)
    leyenda.setBackgroundEnabled(False)
    ubicar(layout, leyenda, 13, y0 + 8)

    # Norte y escala gráfica
    caja(layout, 99, y0, 72, alto)
    norte = QgsLayoutItemPicture(layout)
    norte.setPicturePath(":/images/north_arrows/layout_default_north_arrow.svg")
    ubicar(layout, norte, 130, y0 + 3, 10, 14)
    etiqueta(layout, "N", 99, y0 + 17, 72, 5, 10, True)
    etiqueta(layout, "Escala gráfica", 99, y0 + 23, 72, 5, 9, True)
    escala = QgsLayoutItemScaleBar(layout)
    escala.setStyle("Single Box")
    escala.setLinkedMap(mapa)
    escala.setUnits(QgsUnitTypes.DistanceKilometers)
    escala.setUnitLabel("km")
    escala.setNumberOfSegments(2)
    escala.setNumberOfSegmentsLeft(0)
    escala.setUnitsPerSegment(2500)
    escala.setTextFormat(formato(7))
    ubicar(layout, escala, 112, y0 + 29)
    etiqueta(layout, "Distancias válidas sobre el ecuador", 99, y0 + 41, 72, 4, 6.5, color="#52514e")

    # Membrete, con las filas de la plantilla del docente
    x, w = 173, 115
    filas = [(14, ""), (5, "PROYECCIÓN GEOGRÁFICA (LATITUD / LONGITUD)"), (5, "DATUM: WGS84  ·  SRC: EPSG:4326"),
             (6, "MAPA DE UBICACIÓN DE LAS MUESTRAS DE ROCA TOTAL — EARTHCHEM PETDB"),
             (8, f"Elaborado por: {AUTORES}\nDocente: Dr. Christian Mejía E., Ph.D. · Estadística y Probabilidades"),
             (5, ""), (4, "")]
    y = y0
    for h, texto in filas:
        caja(layout, x, y, w, h)
        if texto:
            etiqueta(layout, texto, x + 1, y, w - 2, h, 6.5 if "\n" in texto else 7, texto.startswith("MAPA"))
        y += h
    etiqueta(layout, "UNIVERSIDAD CENTRAL DEL ECUADOR", x + 2, y0 + 1, w - 18, 6, 10, True)
    etiqueta(layout, "Facultad de Ingeniería en Geología, Minas, Petróleos y Ambiental\nCarrera de Minas",
             x + 2, y0 + 7, w - 18, 6.5, 6.5)
    logo = QgsLayoutItemPicture(layout)
    logo.setPicturePath(str(LOGO))
    ubicar(layout, logo, x + w - 14, y0 + 1, 12, 12)
    y_fecha = y0 + sum(h for h, _ in filas[:5])
    caja(layout, x + w / 2, y_fecha, 0, 5)  # divisor fecha | escala
    escala_num = f"{round(mapa.scale(), -7):,.0f}".replace(",", ".")
    etiqueta(layout, f"FECHA: {date.today():%d/%m/%Y}", x, y_fecha, w / 2, 5, 7)
    etiqueta(layout, f"ESCALA: 1 : {escala_num} (en el ecuador)", x + w / 2, y_fecha, w / 2, 5, 7)
    etiqueta(layout, "Fuente: EarthChem PetDB (13/10/2026, CC BY 4.0) y Natural Earth  ·  Proyecto estrictamente académico",
             x, y_fecha + 5, w, 4, 5.5, color="#52514e")

    proyecto.writeEntryBool("Paths", "/Absolute", False)  # rutas relativas: el .qgz viaja con el .gpkg y el logo
    salida = GIS / "mapa_ubicacion.qgz"
    assert proyecto.write(str(salida)), "no se pudo guardar el proyecto"
    print(salida)
    if exportar_png:
        r = QgsLayoutExporter(layout).exportToImage(exportar_png, QgsLayoutExporter.ImageExportSettings())
        print("export", r, exportar_png)


if __name__ == "__main__":
    app = QgsApplication([], False)
    app.initQgis()
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else str(RAIZ / "docs" / "img" / "mapa_qgis.png"))
    finally:
        app.exitQgis()
