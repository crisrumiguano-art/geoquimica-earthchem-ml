"""Mapa de ubicación (Lección 3) con geopandas + matplotlib, y capas GIS para QGIS.

Uso: python scripts/mapa.py
Salidas:
  data/gis/mapa_ubicacion.gpkg   capas muestras, paises, graticula y contorno (WGS84)
  docs/img/mapa_ubicacion.png    mapa con título, leyenda, escala, norte, grilla y fuente
"""
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry import LineString, Polygon

RAIZ = Path(__file__).resolve().parent.parent
GPKG = RAIZ / "data" / "gis" / "mapa_ubicacion.gpkg"
PAISES_URL = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
ROBINSON = "ESRI:54030"
# Mismos colores que la web (paleta validada; <= 3 categorías + gris para "mixto").
COLORES = {"dorsal y corteza oceanica": "#2a78d6", "intraplaca y rift": "#1baf7a",
           "margen convergente": "#eb6834", "mixto": "#898781"}
ETIQUETAS = {"dorsal y corteza oceanica": "Dorsal y corteza oceánica", "intraplaca y rift": "Intraplaca y rift",
             "margen convergente": "Margen convergente", "mixto": "Mixto"}
CAMPOS = {  # columna de la base -> nombre corto y sin espacios para la tabla de atributos de QGIS
    "Sample Name": "muestra", "Sample Type": "tipo", "Sample SubType": "roca", "Tectonic Setting": "ambiente",
    "Tectonic Group": "grupo_tec", "SiO2 Class": "clase_sio2", "Alteration Grade": "alteracion",
    "Publication Year": "anio_pub", "SiO2 (wt%)": "sio2_wt", "Al2O3 (wt%)": "al2o3_wt", "MgO (wt%)": "mgo_wt",
    "CaO (wt%)": "cao_wt", "Na2O (wt%)": "na2o_wt", "K2O (wt%)": "k2o_wt", "Ni (ppm)": "ni_ppm",
    "Cr (ppm)": "cr_ppm", "Cu (ppm)": "cu_ppm", "La (ppm)": "la_ppm",
}


def linea(lons, lats, n=200):
    """Línea densificada para que se curve bien al proyectar."""
    return LineString(zip(np.interp(np.linspace(0, 1, n), [0, 1], lons), np.interp(np.linspace(0, 1, n), [0, 1], lats)))


def capas():
    df = pd.read_csv(RAIZ / "data" / "earthchem_limpio.csv.gz", low_memory=False,
                     usecols=list(CAMPOS) + ["Latitude", "Longitude"]).dropna(subset=["Latitude", "Longitude"])
    muestras = gpd.GeoDataFrame(df[list(CAMPOS)].rename(columns=CAMPOS),
                                geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]), crs=4326)
    paises = gpd.read_file(PAISES_URL)[["NAME_ES", "CONTINENT", "geometry"]].rename(
        columns={"NAME_ES": "pais", "CONTINENT": "continente"})
    grat = [(f"{lat}°", linea([-180, 180], [lat, lat])) for lat in range(-60, 61, 30)]
    grat += [(f"{lon}°", linea([lon, lon], [-90, 90])) for lon in range(-180, 181, 60)]
    graticula = gpd.GeoDataFrame({"etiqueta": [g[0] for g in grat]}, geometry=[g[1] for g in grat], crs=4326)
    borde = list(zip([-180] * 181, np.linspace(-90, 90, 181))) + list(zip([180] * 181, np.linspace(90, -90, 181)))
    contorno = gpd.GeoDataFrame({"nombre": ["globo"]}, geometry=[Polygon(borde)], crs=4326)
    # Puntos para rotular la grilla en QGIS: latitudes en el borde izquierdo, longitudes sobre el ecuador
    # (QGIS no logra ubicar etiquetas junto al polo en Robinson).
    # cuad = cuadrante de la etiqueta respecto del punto (3 = a la izquierda, 8 = abajo a la derecha).
    rotulos = [(f"{abs(lat)}°{'N' if lat > 0 else 'S' if lat < 0 else ''}", 3, -180, lat) for lat in range(-60, 61, 30)]
    rotulos += [(f"{abs(lon)}°{'E' if lon > 0 else 'O' if lon < 0 else ''}", 8, lon, 0) for lon in range(-180, 181, 60)]
    etiquetas_grilla = gpd.GeoDataFrame({"texto": [r[0] for r in rotulos], "cuad": [r[1] for r in rotulos]},
                                        geometry=gpd.points_from_xy([r[2] for r in rotulos], [r[3] for r in rotulos]), crs=4326)

    GPKG.parent.mkdir(parents=True, exist_ok=True)
    GPKG.unlink(missing_ok=True)
    for nombre, capa in [("contorno", contorno), ("paises", paises), ("graticula", graticula), ("etiquetas_grilla", etiquetas_grilla),
                         ("muestras", muestras)]:
        capa.to_file(GPKG, layer=nombre, driver="GPKG")
    return muestras, paises, graticula, contorno


def mapa(muestras, paises, graticula, contorno):
    m, p, g, c = (x.to_crs(ROBINSON) for x in (muestras, paises, graticula, contorno))
    fig, ax = plt.subplots(figsize=(14, 8.2), dpi=200)
    fig.patch.set_facecolor("white")
    c.plot(ax=ax, color="#f6f6f3", edgecolor="#898781", linewidth=0.8, zorder=0)
    g.plot(ax=ax, color="#c3c2b7", linewidth=0.35, zorder=1)
    p.plot(ax=ax, color="#dcdbd3", edgecolor="white", linewidth=0.3, zorder=2)
    for grupo in ["mixto", "dorsal y corteza oceanica", "intraplaca y rift", "margen convergente"]:
        sub = m[m["grupo_tec"] == grupo]
        sub.plot(ax=ax, markersize=1.6, color=COLORES[grupo], alpha=0.55, linewidth=0, zorder=3,
                 label=f"{ETIQUETAS[grupo]} ({len(sub):,})".replace(",", "."))
    sin = m["grupo_tec"].isna().sum()

    # Etiquetas de la grilla: latitudes a la izquierda, longitudes abajo.
    for lat in range(-60, 61, 30):
        x, y = gpd.GeoSeries.from_xy([-180], [lat], crs=4326).to_crs(ROBINSON).iloc[0].coords[0]
        ax.text(x - 4e5, y, f"{abs(lat)}°{'N' if lat > 0 else 'S' if lat < 0 else ''}", ha="right", va="center", fontsize=8, color="#52514e")
    for lon in range(-180, 181, 60):
        x, y = gpd.GeoSeries.from_xy([lon], [-90], crs=4326).to_crs(ROBINSON).iloc[0].coords[0]
        ax.text(x, y - 5e5, f"{abs(lon)}°{'E' if lon > 0 else 'O' if lon < 0 else ''}", ha="center", va="top", fontsize=8, color="#52514e")

    leg = ax.legend(title="Ambiente tectónico (n.º de análisis)", loc="lower left", bbox_to_anchor=(0.0, 0.02),
                    markerscale=7, fontsize=9, title_fontsize=9.5, frameon=True, framealpha=0.95, edgecolor="#c3c2b7")
    leg._legend_box.align = "left"
    for h in leg.legend_handles:
        h.set_alpha(1)
    ax.add_artist(ScaleBar(1, "m", location="lower right", fixed_value=4000, fixed_units="km", box_alpha=0.9, font_properties={"size": 8},
                           label="escala válida sobre el ecuador", label_loc="bottom", color="#0b0b0b"))
    ax.annotate("N", xy=(0.965, 0.95), xytext=(0.965, 0.86), xycoords="axes fraction", ha="center", va="center",
                fontsize=12, fontweight="bold", arrowprops=dict(facecolor="#0b0b0b", width=4, headwidth=11, headlength=10))
    ax.set_title("Mapa de ubicación de las muestras de roca total — EarthChem PetDB", fontsize=15, fontweight="bold", pad=22)
    ax.text(0.5, 1.012, f"{len(m):,} análisis con coordenadas ({sin} sin ambiente tectónico no se dibujan) · "
            "Proyección Robinson (ESRI:54030) · Datum WGS84".replace(",", "."),
            transform=ax.transAxes, ha="center", fontsize=9.5, color="#52514e")
    ax.text(0.5, -0.07, "Fuente: EarthChem PetDB / Astromaterials Data Synthesis (descarga 13/10/2026, CC BY 4.0); "
             "límites de países: Natural Earth. Elaboración: Rumiguano, Fernández, Bustamante y Haro — "
             "Estadística y Probabilidades, FIGEMPA-UCE, 2026.", transform=ax.transAxes, ha="center", fontsize=7.5, color="#52514e")
    ax.set_axis_off()
    ax.margins(0.03)
    salida = RAIZ / "docs" / "img" / "mapa_ubicacion.png"
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, bbox_inches="tight", pad_inches=0.25)
    print(salida, "|", GPKG)


if __name__ == "__main__":
    mapa(*capas())
