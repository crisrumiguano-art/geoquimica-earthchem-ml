"""Limpia la exportación cruda de EarthChem/PetDB y genera data/earthchem_limpio.csv.gz.

Uso:
    python scripts/limpiar.py [carpeta_cruda] [salida]

<carpeta_cruda> debe contener earthchem_export_oct13_26_142339.csv y
earthchem_export_oct13_26_142339_sample_metadata.csv (no están en el repo: pesan ~600 MB). Por defecto
es data/raw/crudos, un enlace al respaldo en Google Drive (ver AGENTS.md).
"""
import csv
import gzip
import re
import sys
from pathlib import Path

PREFIJO = "earthchem_export_oct13_26_142339"
MIN_LLENADO = 0.05  # columnas químicas con datos en >= 5 % de las filas
SUFIJOS_TEXTO = (" Method", " (comment)", " Lab")
META = ["Geographic Features", "Tectonic Setting", "Rock Texture", "Sample Alteration",
        "Elevation Min (m)", "Elevation Max (m)", "Geologic Age",
        "Geologic Age Max (Ma)", "Geologic Age Min (Ma)", "Expedition"]

# Grado de alteración (ordinal 0-5). PetDB usa el texto completo o su inicial.
ALTERACION = {"FRESH": 0, "F": 0, "SLIGHTLY ALTERED": 1, "S": 1, "MODERATELY ALTERED": 2, "M": 2,
              "EXTENSIVELY ALTERED": 3, "E": 3, "ALMOST COMPLETELY ALTERED": 4, "A": 4,
              "TOTALLY ALTERED": 5, "T": 5}  # "N" y "N/A" son ambiguos: quedan vacíos
# Los 59 ambientes tectónicos de PetDB agrupados en tres grandes clases (nominal, para mapa y ML).
GRUPO_TECTONICO = {
    "dorsal y corteza oceanica": {"SPREADING CENTER", "OLD OCEANIC CRUST", "FRACTURE ZONE", "OFF-AXIS SPREADING CENTER",
                                  "OPHIOLITE", "ABYSSAL HILL", "TRANSFORM FAULT", "OCEAN BASIN", "FOSSIL RIDGE",
                                  "TRIPLE JUNCTION", "OCEANIC SPREADING CENTER"},
    "margen convergente": {"CONVERGENT MARGIN", "VOLCANIC ARC", "BACK-ARC BASIN", "FOREARC", "TRENCH",
                           "ISLAND ARC ACCRETED", "CONTINENTAL COLLISION ZONE"},
    "intraplaca y rift": {"CONTINENTAL RIFT", "INTRAPLATE CRATON", "INTRAPLATE OFF-CRATON", "OCEAN ISLAND", "SEAMOUNT",
                          "ASEISMIC RIDGE", "OCEANIC PLATEAU", "RIFT VALLEY", "INCIPIENT RIFT", "FAILED RIFT"},
}
NUMERO = re.compile(r"-?\d+(\.\d+)?([eE]-?\d+)?|-?\.\d+")
csv.field_size_limit(2**31 - 1)


def sin_formula(s):
    """Excel-safe export envuelve nombres como ="FS-42"."""
    return s[2:-1] if s.startswith('="') and s.endswith('"') else s


def coordenada(s):
    m = re.match(r"\s*([\d.]+)\D*([NSEW])", s)
    if not m:
        return ""
    v = float(m.group(1))
    return -v if m.group(2) in "SW" else v


def es_numero(v):
    return bool(v) and NUMERO.fullmatch(v) is not None


def valor_quimico(v, columna):
    """Concentraciones negativas son lecturas bajo el límite de detección: quedan vacías.
    LOI sí puede ser negativa (la roca gana peso al oxidarse el hierro)."""
    if not es_numero(v) or (float(v) < 0 and not columna.startswith("LOI")):
        return ""
    return v


def lat_lon(lat, lon):
    """Unas pocas muestras (dorsal de Gakkel) vienen con latitud y longitud invertidas en PetDB."""
    lat, lon = coordenada(lat), coordenada(lon)
    if lat != "" and abs(lat) > 90 and lon != "" and abs(lon) <= 90:
        lat, lon = lon, lat
    return [lat, lon]


def clase_sio2(v):
    """Clasificación por SiO2 (wt%): ultrabásica < 45 <= básica < 52 <= intermedia < 63 <= ácida."""
    if not es_numero(v) or not 0 < float(v) <= 100:
        return ""
    x = float(v)
    return "ultrabasica" if x < 45 else "basica" if x < 52 else "intermedia" if x < 63 else "acida"


def grupo_tectonico(ambiente):
    """Valores combinados ("FRACTURE ZONE,SPREADING CENTER") toman el grupo común; si difieren, 'mixto'."""
    if not ambiente:
        return ""
    grupos = {g for a in ambiente.upper().split(",") for g, miembros in GRUPO_TECTONICO.items() if a.strip() in miembros}
    return grupos.pop() if len(grupos) == 1 else "mixto"


def anio(cita):
    m = re.search(r"\((\d{4})\)", cita)
    return m.group(1) if m else ""


def main(cruda, salida):
    datos, meta = cruda / f"{PREFIJO}.csv", cruda / f"{PREFIJO}_sample_metadata.csv"
    with open(meta, encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        mh = next(r)
        filas_meta = list(r)
    mi = [mh.index(k) for k in META]

    # Pasada 1: cuántos valores numéricos tiene cada columna química.
    with open(datos, encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        h = next(r)
        valor = [i for i in range(9, len(h)) if not h[i].endswith(SUFIJOS_TEXTO)]
        cuenta = dict.fromkeys(valor, 0)
        n = 0
        for fila, m in zip(r, filas_meta):
            n += 1
            # Los dos archivos vienen en el mismo orden; si no, el cruce estaría mal.
            assert not m[0] or sin_formula(fila[0]) == m[0], f"fila {n}: {fila[0]} != {m[0]}"
            for i in valor:
                if es_numero(fila[i]):
                    cuenta[i] += 1
    assert n == len(filas_meta), (n, len(filas_meta))
    quimica = [i for i in valor if cuenta[i] >= MIN_LLENADO * n]
    isio2 = h.index("SiO2 (wt%)")

    cab = (["Sample Name", "Sample URL", "Citation", "Publication Year", "Analyzed Material",
            "Sample Type", "Sample SubType", "Latitude", "Longitude"] + META
           + ["Tectonic Group", "Alteration Grade", "SiO2 Class", "N Analytes"] + [h[i] for i in quimica])
    itec = mh.index("Tectonic Setting")

    # Pasada 2: escribir.
    salida.parent.mkdir(parents=True, exist_ok=True)
    with open(datos, encoding="utf-8-sig", newline="") as f, \
            gzip.open(salida, "wt", encoding="utf-8", newline="") as o:
        r = csv.reader(f)
        next(r)
        w = csv.writer(o)
        w.writerow(cab)
        for fila, m in zip(r, filas_meta):
            w.writerow(
                [sin_formula(fila[0]), fila[1], fila[2], anio(fila[2]), fila[4], fila[7], fila[8]]
                + lat_lon(fila[5], fila[6])
                + [m[i] for i in mi]
                + [grupo_tectonico(m[itec]), ALTERACION.get(m[mh.index("Sample Alteration")], ""), clase_sio2(fila[isio2]),
                   sum(es_numero(fila[i]) for i in valor)]
                + [valor_quimico(fila[i], h[i]) for i in quimica])
    print(f"{n} filas, {len(cab)} columnas ({len(quimica)} químicas) -> {salida}")


if __name__ == "__main__":
    assert coordenada("39.244°N") == 39.244 and coordenada("34.414°W") == -34.414
    assert clase_sio2("44.9") == "ultrabasica" and clase_sio2("52") == "intermedia" and clase_sio2("x") == ""
    assert lat_lon("99.850°N", "84.900°E") == [84.9, 99.85] and lat_lon("10°S", "20°W") == [-10, -20]
    assert valor_quimico("-0.03", "Na2O (wt%)") == "" and valor_quimico("-0.5", "LOI (wt%)") == "-0.5"
    assert grupo_tectonico("FRACTURE ZONE,SPREADING CENTER") == "dorsal y corteza oceanica"
    assert grupo_tectonico("CONTINENTAL RIFT,OCEAN BASIN") == "mixto" and grupo_tectonico("Ophiolite") == "dorsal y corteza oceanica"
    assert anio("Liu, J. (2011). TITLE") == "2011" and sin_formula('="FS-42"') == "FS-42"
    raiz = Path(__file__).resolve().parent.parent
    cruda = Path(sys.argv[1]) if len(sys.argv) > 1 else raiz / "data" / "raw" / "crudos"
    if not (cruda / f"{PREFIJO}.csv").exists():
        sys.exit(f"No están los CSV crudos en {cruda}\n\n{__doc__}")
    main(cruda, Path(sys.argv[2]) if len(sys.argv) > 2 else raiz / "data" / "earthchem_limpio.csv.gz")
