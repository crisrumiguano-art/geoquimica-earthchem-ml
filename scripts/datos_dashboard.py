"""Resume data/earthchem_limpio.csv.gz en docs/data/resumen.json para la web: cifras de portada, mapa
interactivo, ambientes tectónicos y diagrama TAS. Las TDF y gráficas estadísticas las genera R (carpeta R/).

Uso: python scripts/datos_dashboard.py
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
MUESTRA = 6000  # puntos por gráfico de dispersión/mapa: más satura el navegador
TIPOS = {  # tipo estadístico de cada columna no química (las químicas son continuas)
    "Sample Name": "identificador", "Sample URL": "identificador", "Citation": "nominal",
    "Publication Year": "discreta", "Analyzed Material": "nominal (binaria)",
    "Sample Type": "nominal", "Sample SubType": "nominal", "Latitude": "continua",
    "Longitude": "continua", "Geographic Features": "nominal", "Tectonic Setting": "nominal",
    "Rock Texture": "nominal", "Sample Alteration": "ordinal (texto original)",
    "Elevation Min (m)": "continua", "Elevation Max (m)": "continua",
    "Geologic Age": "ordinal", "Geologic Age Max (Ma)": "continua",
    "Geologic Age Min (Ma)": "continua", "Expedition": "nominal",
    "Tectonic Group": "nominal", "Alteration Grade": "ordinal", "SiO2 Class": "ordinal", "N Analytes": "discreta",
}


def conteo(s, top=None):
    c = s.dropna().value_counts()
    return {"labels": [str(k) for k in c.index[:top]], "values": c.values[:top].tolist()}


def main():
    df = pd.read_csv(RAIZ / "data" / "earthchem_limpio.csv.gz", low_memory=False)
    n = len(df)

    tas = df[["SiO2 (wt%)", "Na2O (wt%)", "K2O (wt%)", "Sample Type"]].dropna()
    tas = tas[tas["Sample Type"].isin(["igneous:volcanic:mafic", "igneous:volcanic:intermediate",
                                       "igneous:volcanic:felsic"])]
    tas = tas[(tas["SiO2 (wt%)"].between(30, 85))]
    tas = tas.sample(min(MUESTRA, len(tas)), random_state=0)

    geo = df[["Latitude", "Longitude", "Tectonic Setting"]].dropna().sample(MUESTRA, random_state=0)

    resumen = {
        "filas": n, "columnas": df.shape[1],
        "articulos": int(df["Citation"].nunique()),
        "anios": [int(df["Publication Year"].min()), int(df["Publication Year"].max())],
        "tectonica": conteo(df["Tectonic Setting"], 12),
        "tas": {t: {"x": g["SiO2 (wt%)"].round(2).tolist(),
                    "y": (g["Na2O (wt%)"] + g["K2O (wt%)"]).round(2).tolist()}
                for t, g in tas.groupby("Sample Type")},
        "mapa": {"lat": geo["Latitude"].round(3).tolist(), "lon": geo["Longitude"].round(3).tolist(),
                 "tec": geo["Tectonic Setting"].tolist()},
    }
    salida = RAIZ / "docs" / "data" / "resumen.json"
    salida.write_text(json.dumps(resumen, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{salida} ({salida.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
