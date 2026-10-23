"""Crea el proyecto QGIS del mapa de ubicación (data/gis/mapa_ubicacion.qgz) con capas en shapefile
(data/gis/shp/), la misma simbología del mapa de la web y dos composiciones de impresión, A4 y A3, con el
formato de la plantilla del docente (marco, cuadrícula con coordenadas, leyenda, norte, escala gráfica y
membrete con logo UCE). Exporta el PNG de la web y los PDF para imprimir a escala.

Requiere QGIS. Ejecutar con su Python (no con el Python normal), después de scripts/mapa.py:
    "C:\\Program Files\\QGIS 3.44.8\\bin\\python-qgis-ltr.bat" scripts/proyecto_qgis.py
"""
import zipfile
from datetime import date
from pathlib import Path

from osgeo import gdal

gdal.UseExceptions()
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
SHP = GIS / "shp"
LOGO = GIS / "UCE.png"  # copiado de referencias_curso/QGIS/1.- Mapa de Ubicacion/UCE.png
WGS84 = QgsCoordinateReferenceSystem("EPSG:4326")
GRUPOS = [("dorsal y corteza oceanica", "Dorsal y corteza oceánica", "#2a78d6"),
          ("intraplaca y rift", "Intraplaca y rift", "#1baf7a"),
          ("margen convergente", "Margen convergente", "#eb6834"),
          ("mixto", "Mixto", "#898781")]
AUTORES = "Rumiguano C., Fernández A., Bustamante E., Haro J., Ligña J."
MM = QgsUnitTypes.LayoutMillimeters
# Shapefiles: solo lo que el mapa usa, con anchos de campo fijos. Sin el CAST, el .dbf de muestras pesa 70 MB
# (campos de texto de 254 caracteres y números de 24 dígitos); así queda en ~20 MB.
CAPAS_SHP = {
    "muestras": "SELECT CAST(muestra AS character(38)) AS muestra, CAST(roca AS character(23)) AS roca, "
                "CAST(grupo_tec AS character(25)) AS grupo_tec, CAST(clase_sio2 AS character(11)) AS clase_sio2, "
                "CAST(anio_pub AS integer(4)) AS anio_pub, CAST(sio2_wt AS numeric(6,2)) AS sio2_wt, "
                "CAST(mgo_wt AS numeric(6,2)) AS mgo_wt, CAST(ni_ppm AS numeric(8,1)) AS ni_ppm, "
                "CAST(cr_ppm AS numeric(8,1)) AS cr_ppm FROM muestras",
    "paises": "SELECT CAST(pais AS character(40)) AS pais, CAST(continente AS character(25)) AS continente FROM paises",
    "oceanos": "SELECT CAST(nombre AS character(10)) AS nombre FROM contorno",
}
# Papel -> (factor de tamaño respecto de A4, escala). A3 = A4 con cada lado multiplicado por raíz de 2. Escalas
# redondas: el ancho del marco se calcula para que los 360° del ecuador midan exactamente ECUADOR / escala.
# 1:100 000 000 no entra en A3 (el mapa mediría 40,1 cm en una hoja de 42 cm, sin lugar para marco y coordenadas).
PAPELES = {"A4": (1.0, 150_000_000), "A3": (2 ** 0.5, 110_000_000)}
ECUADOR_MM = 40_075_016_686  # longitud del ecuador en el elipsoide WGS84


def shapefiles():
    """data/gis/shp/*.shp desde el GeoPackage, con índice espacial .qix para que QGIS dibuje rápido."""
    SHP.mkdir(parents=True, exist_ok=True)
    for viejo in SHP.glob("*"):
        viejo.unlink()
    for nombre, sql in CAPAS_SHP.items():
        r = gdal.VectorTranslate(str(SHP / f"{nombre}.shp"), str(GPKG), format="ESRI Shapefile", SQLStatement=sql, SQLDialect="OGRSQL",
                                 layerName=nombre, layerCreationOptions=["ENCODING=UTF-8", "SPATIAL_INDEX=YES"])
        assert r is not None, nombre
        r = None  # cierra y escribe el archivo


def capa(nombre):
    c = QgsVectorLayer(str(SHP / f"{nombre}.shp"), nombre, "ogr")
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


class Lamina:
    """Composición de impresión. Las medidas se escriben en milímetros de A4 y se multiplican por el factor del
    papel, así la versión A3 es la misma lámina ampliada (con letras más grandes y mapa a mayor escala)."""

    def __init__(self, proyecto, papel):
        self.f, self.escala = PAPELES[papel]
        self.layout = QgsPrintLayout(proyecto)
        self.layout.initializeDefaults()
        self.layout.setName(f"Mapa de ubicación {papel}")
        proyecto.layoutManager().addLayout(self.layout)
        pagina = self.layout.pageCollection().page(0)
        pagina.setPageSize(papel, pagina.Landscape)

    def ubicar(self, item, x, y, w=None, h=None):
        f = self.f
        item.attemptMove(QgsLayoutPoint(x * f, y * f, MM))
        if w is not None:
            item.attemptResize(QgsLayoutSize(w * f, h * f, MM))
        self.layout.addLayoutItem(item)
        return item

    def texto(self, tam, negrita=False, color="#0b0b0b"):
        return formato(tam * self.f, negrita, color)

    def etiqueta(self, texto, x, y, w, h, tam, negrita=False, color="#0b0b0b"):
        item = QgsLayoutItemLabel(self.layout)
        item.setText(texto)
        item.setTextFormat(self.texto(tam, negrita, color))
        item.setHAlign(Qt.AlignHCenter)
        item.setVAlign(Qt.AlignVCenter)
        return self.ubicar(item, x, y, w, h)

    def caja(self, x, y, w, h, grosor=0.3):
        r = QgsLayoutItemShape(self.layout)
        r.setShapeType(QgsLayoutItemShape.Rectangle)
        r.setSymbol(QgsFillSymbol.createSimple({"style": "no", "outline_color": "#0b0b0b",
                                                "outline_width": str(grosor * self.f)}))
        return self.ubicar(r, x, y, w, h)

    def cuadricula(self, mapa):
        """Cuadrícula de 30° con las coordenadas en el borde (O/E, S/N) y marco cebra, como la plantilla del docente."""
        g = QgsLayoutItemMapGrid("Cuadrícula", mapa)
        g.setCrs(WGS84)
        g.setIntervalX(30)
        g.setIntervalY(30)
        g.setLineSymbol(QgsLineSymbol.createSimple({"line_color": "#9a9990", "line_width": str(0.15 * self.f)}))
        g.setFrameStyle(QgsLayoutItemMapGrid.Zebra)
        g.setFrameWidth(1.2 * self.f)
        g.setAnnotationEnabled(True)
        g.setAnnotationFormat(QgsLayoutItemMapGrid.CustomFormat)
        g.setAnnotationExpression(
            "CASE WHEN abs(@grid_number) = if(@grid_axis = 'x', 180, 90) THEN '' "  # sin rótulos en las esquinas: se encimarían
            "ELSE concat(abs(@grid_number), '°', CASE WHEN @grid_number = 0 THEN '' WHEN @grid_axis = 'x' "
            "THEN if(@grid_number < 0, 'O', 'E') ELSE if(@grid_number < 0, 'S', 'N') END) END")
        g.setAnnotationTextFormat(self.texto(7))
        g.setAnnotationFrameDistance(1 * self.f)
        for lado in (QgsLayoutItemMapGrid.Left, QgsLayoutItemMapGrid.Right, QgsLayoutItemMapGrid.Top,
                     QgsLayoutItemMapGrid.Bottom):
            g.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, lado)
            vertical = lado in (QgsLayoutItemMapGrid.Left, QgsLayoutItemMapGrid.Right)
            g.setAnnotationDirection(QgsLayoutItemMapGrid.Vertical if vertical else QgsLayoutItemMapGrid.Horizontal, lado)
        mapa.grids().addGrid(g)

    def armar(self, oceanos, paises, muestras):
        # El mapa es mundial (2:1): va arriba a lo ancho, y leyenda, escala y membrete en una franja abajo.
        self.caja(6, 6, 285, 198, 0.5)
        mapa = QgsLayoutItemMap(self.layout)
        mapa.setCrs(WGS84)
        mapa.setLayers([muestras, paises, oceanos])
        mapa.setFrameEnabled(True)
        ancho = ECUADOR_MM / self.escala / self.f  # en mm de A4 (ubicar() multiplica por el factor)
        self.layout.addLayoutItem(mapa)
        for _ in range(2):  # 2.ª vuelta: corrige el ancho con la escala que mide QGIS (su ecuador difiere ~0,7 %)
            mapa.attemptMove(QgsLayoutPoint((148.5 - ancho / 2) * self.f, (13 + (132 - ancho / 2) / 2) * self.f, MM))
            mapa.attemptResize(QgsLayoutSize(ancho * self.f, ancho / 2 * self.f, MM))
            mapa.zoomToExtent(QgsRectangle(-180, -90, 180, 90))
            ancho *= mapa.scale() / self.escala
        self.cuadricula(mapa)

        y0, alto = 154, 47
        # Leyenda
        self.caja(9, y0, 88, alto)
        self.etiqueta("LEYENDA", 9, y0 + 1.5, 88, 6, 11, True)
        leyenda = QgsLayoutItemLegend(self.layout)
        leyenda.setTitle("Ambiente tectónico (n.º de análisis)")
        leyenda.setLinkedMap(mapa)
        leyenda.setAutoUpdateModel(False)
        raiz = leyenda.model().rootGroup()
        for nodo in list(raiz.children()):
            if nodo.layerId() != muestras.id():
                raiz.removeChildNode(nodo)
        raiz.findLayer(muestras.id()).setCustomProperty("legend/title-style", "hidden")
        leyenda.rstyle(QgsLegendStyle.Title).setTextFormat(self.texto(8, True))
        leyenda.rstyle(QgsLegendStyle.SymbolLabel).setTextFormat(self.texto(8))
        leyenda.setSymbolWidth(7 * self.f)
        leyenda.setSymbolHeight(4 * self.f)
        leyenda.setMinimumSymbolSize(3 * self.f)
        leyenda.setBackgroundEnabled(False)
        self.ubicar(leyenda, 13, y0 + 8)

        # Norte y escala gráfica
        self.caja(99, y0, 72, alto)
        norte = QgsLayoutItemPicture(self.layout)
        norte.setPicturePath(":/images/north_arrows/layout_default_north_arrow.svg")
        self.ubicar(norte, 130, y0 + 3, 10, 14)
        self.etiqueta("N", 99, y0 + 17, 72, 5, 10, True)
        self.etiqueta("Escala gráfica", 99, y0 + 23, 72, 5, 9, True)
        escala = QgsLayoutItemScaleBar(self.layout)
        escala.setStyle("Single Box")
        escala.setLinkedMap(mapa)
        escala.setUnits(QgsUnitTypes.DistanceKilometers)
        escala.setUnitLabel("km")
        escala.setNumberOfSegments(2)
        escala.setNumberOfSegmentsLeft(0)
        escala.setUnitsPerSegment(2500)
        escala.setHeight(3 * self.f)
        escala.setTextFormat(self.texto(7))
        self.ubicar(escala, 112, y0 + 29)
        self.etiqueta("Distancias válidas sobre el ecuador", 99, y0 + 41, 72, 4, 6.5, color="#52514e")

        # Membrete, con las filas de la plantilla del docente
        x, w = 173, 115
        filas = [(14, ""), (5, "PROYECCIÓN GEOGRÁFICA (LATITUD / LONGITUD)"), (5, "DATUM: WGS84  ·  SRC: EPSG:4326"),
                 (6, "MAPA DE UBICACIÓN DE LAS MUESTRAS DE ROCA TOTAL — EARTHCHEM PETDB"),
                 (8, f"Elaborado por: {AUTORES}\nDocente: Dr. Christian Mejía E., Ph.D. · Estadística y Probabilidades"),
                 (5, ""), (4, "")]
        y = y0
        for h, texto in filas:
            self.caja(x, y, w, h)
            if texto:
                self.etiqueta(texto, x + 1, y, w - 2, h, 6.5 if "\n" in texto else 7, texto.startswith("MAPA"))
            y += h
        self.etiqueta("UNIVERSIDAD CENTRAL DEL ECUADOR", x + 2, y0 + 1, w - 18, 6, 10, True)
        self.etiqueta("Facultad de Ingeniería en Geología, Minas, Petróleos y Ambiental\nCarrera de Minas",
                      x + 2, y0 + 7, w - 18, 6.5, 6.5)
        logo = QgsLayoutItemPicture(self.layout)
        logo.setPicturePath(str(LOGO))
        self.ubicar(logo, x + w - 14, y0 + 1, 12, 12)
        y_fecha = y0 + sum(h for h, _ in filas[:5])
        self.caja(x + w / 2, y_fecha, 0, 5)  # divisor fecha | escala
        # QGIS calcula la escala por su cuenta: tiene que coincidir con la elegida (tolerancia 0,5 %).
        assert abs(mapa.scale() / self.escala - 1) < 0.005, (self.layout.name(), mapa.scale())
        escala_num = f"{self.escala:,.0f}".replace(",", ".")
        self.etiqueta(f"FECHA: {date.today():%d/%m/%Y}", x, y_fecha, w / 2, 5, 7)
        self.etiqueta(f"ESCALA: 1 : {escala_num} (en el ecuador)", x + w / 2, y_fecha, w / 2, 5, 7)
        self.etiqueta("Fuente: EarthChem PetDB (13/10/2026, CC BY 4.0) y Natural Earth  ·  Proyecto estrictamente "
                      "académico", x, y_fecha + 5, w, 4, 5.5, color="#52514e")
        print(self.layout.name(), "escala 1 :", escala_num)

    def pdf(self, ruta):
        """PDF vectorial para imprimir a escala (tamaño real, sin "ajustar a la página")."""
        ajustes = QgsLayoutExporter.PdfExportSettings()
        ajustes.dpi = 300
        r = QgsLayoutExporter(self.layout).exportToPdf(str(ruta), ajustes)
        assert r == QgsLayoutExporter.Success, (ruta, r)
        print(ruta)


def main():
    shapefiles()
    proyecto = QgsProject.instance()
    proyecto.setCrs(WGS84)  # geográficas: la cuadrícula toca el marco en los cuatro lados
    proyecto.setTitle("Mapa de ubicación — Geoquímica de rocas EarthChem PetDB")

    oceanos, paises, muestras = (capa(n) for n in ("oceanos", "paises", "muestras"))
    oceanos.setName("Océanos")
    paises.setName("Países")
    muestras.setName("Muestras de roca total")
    oceanos.setRenderer(oceanos.renderer().__class__(QgsFillSymbol.createSimple(
        {"color": "#eaf2f8", "outline_style": "no"})))
    paises.setRenderer(paises.renderer().__class__(QgsFillSymbol.createSimple(
        {"color": "#dcdbd3", "outline_color": "#ffffff", "outline_width": "0.1"})))
    categorias = []
    for valor, texto, color in GRUPOS:
        n = sum(1 for _ in muestras.getFeatures(f"trim(\"grupo_tec\") = '{valor}'"))
        simbolo = QgsMarkerSymbol.createSimple({"name": "circle", "color": color, "size": "0.6", "outline_style": "no"})
        simbolo.setOpacity(0.6)
        categorias.append(QgsRendererCategory(valor, simbolo, f"{texto} ({n:,})".replace(",", ".")))
    muestras.setRenderer(QgsCategorizedSymbolRenderer("grupo_tec", categorias))
    for c in (oceanos, paises, muestras):  # el orden de agregado = de abajo hacia arriba
        proyecto.addMapLayer(c)

    laminas = {}
    for papel in PAPELES:
        laminas[papel] = Lamina(proyecto, papel)
        laminas[papel].armar(oceanos, paises, muestras)

    proyecto.writeEntryBool("Paths", "/Absolute", False)  # rutas relativas: el .qgz viaja con shp/ y el logo
    salida = GIS / "mapa_ubicacion.qgz"
    assert proyecto.write(str(salida)), "no se pudo guardar el proyecto"
    print(salida)

    png = RAIZ / "docs" / "img" / "mapa_qgis.png"
    r = QgsLayoutExporter(laminas["A4"].layout).exportToImage(str(png), QgsLayoutExporter.ImageExportSettings())
    assert r == QgsLayoutExporter.Success, r
    for papel, lamina in laminas.items():
        lamina.pdf(RAIZ / "docs" / f"mapa_ubicacion_{papel}.pdf")

    # Paquete para trabajar con QGIS de la forma tradicional: descomprimir y abrir el .qgz.
    paquete = RAIZ / "docs" / "mapa_qgis_shapefiles.zip"
    with zipfile.ZipFile(paquete, "w", zipfile.ZIP_DEFLATED) as z:
        for archivo in [salida, LOGO, *sorted(SHP.glob("*"))]:
            z.write(archivo, Path("mapa_qgis") / archivo.relative_to(GIS))
    print(paquete)


if __name__ == "__main__":
    app = QgsApplication([], False)
    app.initQgis()
    try:
        main()
    finally:
        app.exitQgis()
