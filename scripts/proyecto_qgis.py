"""Crea data/gis/mapa_ubicacion.qgz: proyecto QGIS con las capas de mapa_ubicacion.gpkg, la misma
simbología del mapa de la web y una composición de impresión (título, leyenda, escala, norte, grilla, fuente).

Requiere QGIS. Ejecutar con su Python (no con el Python normal), después de scripts/mapa.py:
    "C:\\Program Files\\QGIS 3.44.8\\bin\\python-qgis-ltr.bat" scripts/proyecto_qgis.py
"""
import sys
from pathlib import Path

from qgis.core import (
    Qgis, QgsApplication, QgsCategorizedSymbolRenderer, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsFillSymbol,
    QgsLayoutExporter, QgsLayoutItemLabel, QgsLayoutItemLegend, QgsLayoutItemMap, QgsLayoutItemPicture,
    QgsLayoutItemScaleBar, QgsLayoutPoint, QgsLayoutSize, QgsLegendStyle, QgsLineSymbol, QgsMarkerSymbol,
    QgsPalLayerSettings, QgsPrintLayout, QgsProject, QgsProperty, QgsRendererCategory, QgsTextFormat, QgsUnitTypes,
    QgsVectorLayer, QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtGui import QColor, QFont

RAIZ = Path(__file__).resolve().parent.parent
GIS = RAIZ / "data" / "gis"
GPKG = GIS / "mapa_ubicacion.gpkg"
GRUPOS = [("dorsal y corteza oceanica", "Dorsal y corteza oceánica", "#2a78d6"),
          ("intraplaca y rift", "Intraplaca y rift", "#1baf7a"),
          ("margen convergente", "Margen convergente", "#eb6834"),
          ("mixto", "Mixto", "#898781")]


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


def etiqueta(layout, texto, x, y, w, h, tam, negrita=False, color="#0b0b0b"):
    item = QgsLayoutItemLabel(layout)
    item.setText(texto)
    item.setTextFormat(formato(tam, negrita, color))
    item.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    item.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(item)
    return item


def main(exportar_png=None):
    proyecto = QgsProject.instance()
    proyecto.setCrs(QgsCoordinateReferenceSystem("ESRI:54030"))  # Robinson
    proyecto.setTitle("Mapa de ubicación — Geoquímica de rocas EarthChem PetDB")

    contorno, paises, graticula, rotulos, muestras = (capa(n) for n in
                                                      ("contorno", "paises", "graticula", "etiquetas_grilla", "muestras"))
    rotulos.setName("Coordenadas")
    rotulos.setRenderer(rotulos.renderer().__class__(QgsMarkerSymbol.createSimple({"size": "0"})))
    rot = QgsPalLayerSettings()
    rot.fieldName = "texto"
    rot.placement = Qgis.LabelPlacement.OverPoint
    rot.dist = 1.2
    rot.placementSettings().setOverlapHandling(Qgis.LabelOverlapHandling.AllowOverlapIfRequired)
    rot.setFormat(formato(7, color="#52514e"))
    rot.dataDefinedProperties().setProperty(QgsPalLayerSettings.OffsetQuad, QgsProperty.fromField("cuad"))
    rotulos.setLabeling(QgsVectorLayerSimpleLabeling(rot))
    rotulos.setLabelsEnabled(True)
    contorno.setName("Océanos")
    paises.setName("Países")
    graticula.setName("Grilla 30°")
    muestras.setName("Muestras de roca total")
    contorno.setRenderer(contorno.renderer().__class__(QgsFillSymbol.createSimple(
        {"color": "#f6f6f3", "outline_color": "#898781", "outline_width": "0.3"})))
    paises.setRenderer(paises.renderer().__class__(QgsFillSymbol.createSimple(
        {"color": "#dcdbd3", "outline_color": "#ffffff", "outline_width": "0.1"})))
    graticula.setRenderer(graticula.renderer().__class__(QgsLineSymbol.createSimple(
        {"line_color": "#c3c2b7", "line_width": "0.15"})))
    categorias = []
    for valor, texto, color in GRUPOS:
        n = sum(1 for _ in muestras.getFeatures(f"\"grupo_tec\" = '{valor}'"))
        simbolo = QgsMarkerSymbol.createSimple({"name": "circle", "color": color, "size": "0.6", "outline_style": "no"})
        simbolo.setOpacity(0.6)
        categorias.append(QgsRendererCategory(valor, simbolo, f"{texto} ({n:,})".replace(",", ".")))
    muestras.setRenderer(QgsCategorizedSymbolRenderer("grupo_tec", categorias))
    for c in (contorno, graticula, paises, muestras, rotulos):  # el orden de agregado = de abajo hacia arriba
        proyecto.addMapLayer(c)

    # Composición de impresión A4 horizontal.
    layout = QgsPrintLayout(proyecto)
    layout.initializeDefaults()
    layout.setName("Mapa de ubicación A4")
    proyecto.layoutManager().addLayout(layout)
    pagina = layout.pageCollection().page(0)
    pagina.setPageSize("A4", pagina.Landscape)

    mapa = QgsLayoutItemMap(layout)
    mapa.attemptMove(QgsLayoutPoint(12, 24, QgsUnitTypes.LayoutMillimeters))
    mapa.attemptResize(QgsLayoutSize(273, 150, QgsUnitTypes.LayoutMillimeters))
    mapa.setCrs(proyecto.crs())
    mapa.setLayers([rotulos, muestras, paises, graticula, contorno])
    extension = contorno.extent()
    extension = QgsCoordinateTransform(contorno.crs(), proyecto.crs(), proyecto).transformBoundingBox(extension)
    extension.scale(1.08)
    mapa.zoomToExtent(extension)
    mapa.setFrameEnabled(True)
    layout.addLayoutItem(mapa)

    etiqueta(layout, "Mapa de ubicación de las muestras de roca total — EarthChem PetDB", 12, 6, 273, 9, 16, True)
    etiqueta(layout, "Proyección Robinson (ESRI:54030) · Datum WGS84 · Estadística y Probabilidades, FIGEMPA – "
                     "Universidad Central del Ecuador", 12, 15, 273, 6, 9, color="#52514e")
    etiqueta(layout, "Fuente: EarthChem PetDB / Astromaterials Data Synthesis (descarga 13/10/2026, CC BY 4.0); límites: "
                     "Natural Earth. Elaboración: Rumiguano, Fernández, Bustamante y Haro, 2026.", 12, 198, 273, 6, 7,
             color="#52514e")

    leyenda = QgsLayoutItemLegend(layout)
    leyenda.setTitle("Ambiente tectónico (n.º de análisis)")
    leyenda.setLinkedMap(mapa)
    leyenda.setAutoUpdateModel(False)
    raiz = leyenda.model().rootGroup()
    for nodo in list(raiz.children()):
        if nodo.layerId() != muestras.id():
            raiz.removeChildNode(nodo)
    nodo_muestras = raiz.findLayer(muestras.id())
    nodo_muestras.setCustomProperty("legend/title-style", "hidden")
    leyenda.rstyle(QgsLegendStyle.Title).setTextFormat(formato(10, True))
    leyenda.rstyle(QgsLegendStyle.SymbolLabel).setTextFormat(formato(8))
    leyenda.setMinimumSymbolSize(3)
    leyenda.attemptMove(QgsLayoutPoint(15, 133, QgsUnitTypes.LayoutMillimeters))
    leyenda.setFrameEnabled(True)
    leyenda.setBackgroundColor(QColor(255, 255, 255, 235))
    layout.addLayoutItem(leyenda)

    escala = QgsLayoutItemScaleBar(layout)
    escala.setStyle("Single Box")
    escala.setLinkedMap(mapa)
    escala.setUnits(QgsUnitTypes.DistanceKilometers)
    escala.setUnitLabel("km")
    escala.setNumberOfSegments(2)
    escala.setNumberOfSegmentsLeft(0)
    escala.setUnitsPerSegment(2000)
    escala.attemptMove(QgsLayoutPoint(222, 180, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(escala)
    etiqueta(layout, "Escala válida sobre el ecuador", 222, 192, 60, 5, 7, color="#52514e")

    norte = QgsLayoutItemPicture(layout)
    norte.setPicturePath(":/images/north_arrows/layout_default_north_arrow.svg")
    norte.attemptMove(QgsLayoutPoint(270, 27, QgsUnitTypes.LayoutMillimeters))
    norte.attemptResize(QgsLayoutSize(11, 16, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(norte)

    proyecto.writeEntryBool("Paths", "/Absolute", False)  # rutas relativas: el .qgz viaja con el .gpkg
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
