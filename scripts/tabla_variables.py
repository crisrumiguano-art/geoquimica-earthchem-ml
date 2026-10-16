"""Tabla de variables del proyecto (Lección 4), con el formato de la plantilla del curso
(BD_LITOGEOQUIMICA.xlsx): nombre, descripción, tipo, subtipo, dominio (definición y conjunto), rango,
instrumento, sistema de unidades y escala de medición.

Uso: python scripts/tabla_variables.py [carpeta_cruda]   (por defecto data/raw/crudos)
El instrumento (método analítico) solo está en el CSV crudo; el rango sale de la base limpia.
Salidas: data/tabla_variables.xlsx y docs/data/variables.json
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

from limpiar import PREFIJO

RAIZ = Path(__file__).resolve().parent.parent
csv.field_size_limit(2**31 - 1)

NOMBRES = {  # nombre en español de cada analito
    "SiO2": "óxido de silicio (sílice)", "Al2O3": "óxido de aluminio", "Fe2O3": "óxido férrico",
    "Fe2O3T": "hierro total como Fe2O3", "FeO": "óxido ferroso", "FeOT": "hierro total como FeO",
    "MgO": "óxido de magnesio", "MnO": "óxido de manganeso", "CaO": "óxido de calcio",
    "Na2O": "óxido de sodio", "K2O": "óxido de potasio", "P2O5": "pentóxido de fósforo",
    "LOI": "pérdida por calcinación (volátiles)", "Co": "cobalto", "Cu": "cobre", "Ni": "níquel",
    "Zn": "zinc", "Rb": "rubidio", "Sr": "estroncio", "Ba": "bario", "Cs": "cesio", "Pb": "plomo",
    "Y": "itrio", "Zr": "circonio", "Hf": "hafnio", "Nb": "niobio", "Ta": "tantalio", "Th": "torio",
    "U": "uranio", "V": "vanadio", "Cr": "cromo", "Sc": "escandio", "Ga": "galio", "Li": "litio",
    "La": "lantano", "Ce": "cerio", "Pr": "praseodimio", "Nd": "neodimio", "Sm": "samario",
    "Eu": "europio", "Gd": "gadolinio", "Tb": "terbio", "Dy": "disprosio", "Ho": "holmio",
    "Er": "erbio", "Tm": "tulio", "Yb": "iterbio", "Lu": "lutecio",
}
TIERRAS_RARAS = {"La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"}
METODOS = {  # siglas de PetDB -> nombre legible
    "XRF": "fluorescencia de rayos X (XRF)", "EMP": "microsonda electrónica (EMP)",
    "ICPMS": "espectrometría de masas con plasma (ICP-MS)", "ICPAES": "espectrometría de emisión con plasma (ICP-AES)",
    "ICP-OES": "espectrometría de emisión óptica con plasma (ICP-OES)", "INAA": "activación neutrónica (INAA)",
    "LA-ICPMS": "ablación láser ICP-MS", "AAS": "absorción atómica (AAS)", "WET": "química húmeda",
    "IGN": "calcinación (gravimetría)", "MS-ID": "dilución isotópica (MS-ID)", "HR-ICP-MS": "ICP-MS de alta resolución",
}

# Variables no químicas: (descripción, tipo, subtipo, escala, instrumento, unidad)
OTRAS = {
    "Sample Name": ("Código de la muestra asignado por el autor", "identificador", "—", "nominal", "registro del autor", "—"),
    "Sample URL": ("Enlace a la ficha de la muestra en PetDB", "identificador", "—", "nominal", "PetDB", "—"),
    "Citation": ("Artículo científico que publicó el análisis", "cualitativa", "nominal", "nominal", "revisión bibliográfica", "—"),
    "Publication Year": ("Año de publicación del artículo", "cuantitativa", "discreta", "intervalo", "extraído de la cita", "año"),
    "Analyzed Material": ("Material analizado", "cualitativa", "nominal (binaria)", "nominal", "registro PetDB", "—"),
    "Sample Type": ("Clase de roca (ígnea, metamórfica, sedimentaria…)", "cualitativa", "nominal", "nominal", "descripción petrográfica", "—"),
    "Sample SubType": ("Nombre de la roca (basalto, gabro, peridotita…)", "cualitativa", "nominal", "nominal", "descripción petrográfica", "—"),
    "Latitude": ("Latitud del sitio de muestreo (sur negativo)", "cuantitativa", "continua", "intervalo", "GPS / navegación del buque", "grados decimales"),
    "Longitude": ("Longitud del sitio de muestreo (oeste negativo)", "cuantitativa", "continua", "intervalo", "GPS / navegación del buque", "grados decimales"),
    "Geographic Features": ("Océano, país o región geológica", "cualitativa", "nominal", "nominal", "registro PetDB", "—"),
    "Tectonic Setting": ("Ambiente tectónico de formación", "cualitativa", "nominal", "nominal", "interpretación geológica", "—"),
    "Rock Texture": ("Textura de la roca", "cualitativa", "nominal", "nominal", "descripción petrográfica", "—"),
    "Sample Alteration": ("Alteración informada por el autor (texto)", "cualitativa", "ordinal", "ordinal", "descripción petrográfica", "—"),
    "Elevation Min (m)": ("Elevación o profundidad mínima (negativo = bajo el nivel del mar)", "cuantitativa", "continua", "intervalo", "altímetro / ecosonda", "m"),
    "Elevation Max (m)": ("Elevación o profundidad máxima", "cuantitativa", "continua", "intervalo", "altímetro / ecosonda", "m"),
    "Geologic Age": ("Edad geológica (período o época)", "cualitativa", "ordinal", "ordinal", "estratigrafía", "—"),
    "Geologic Age Max (Ma)": ("Edad máxima", "cuantitativa", "continua", "razón", "geocronología", "millones de años (Ma)"),
    "Geologic Age Min (Ma)": ("Edad mínima", "cuantitativa", "continua", "razón", "geocronología", "millones de años (Ma)"),
    "Expedition": ("Expedición o campaña de muestreo", "cualitativa", "nominal", "nominal", "registro PetDB", "—"),
    "Tectonic Group": ("Ambiente tectónico agrupado en tres clases (o mixto)", "cualitativa", "nominal", "nominal", "derivada de Tectonic Setting", "—"),
    "Alteration Grade": ("Grado de alteración: 0 fresca, 1 leve, 2 moderada, 3 extensa, 4 casi total, 5 total", "cualitativa", "ordinal", "ordinal", "derivada de Sample Alteration", "—"),
    "SiO2 Class": ("Clase por sílice: ultrabásica < 45 ≤ básica < 52 ≤ intermedia < 63 ≤ ácida", "cualitativa", "ordinal", "ordinal", "derivada de SiO2 (wt%)", "—"),
    "N Analytes": ("Número de analitos químicos medidos en la muestra", "cuantitativa", "discreta", "razón", "conteo", "analitos"),
}


# Dominio en notación de conjuntos, como la plantilla: (definición, conjunto al que pertenece x).
# Los conjuntos numéricos se escriben con su símbolo (R, Z+…); los cualitativos, con el nombre del conjunto.
DOMINIOS = {
    "Sample Name": ("D={x/x es identificación ^ Pertenencia(x)=Muestra}", "Identificador"),
    "Sample URL": ("D={x/x es enlace web ^ Pertenencia(x)=Muestra}", "URL"),
    "Citation": ("D={x/x es artículo científico ^ Revisión(x)=por pares}", "Artículo"),
    "Publication Year": ("D={x/x es tiempo ^ x ∈ N ^ Tipo(x)=años}", "Z+"),
    "Analyzed Material": ("D={x/x es material analizado ^ Tipo(x)=roca total}", "Material"),
    "Sample Type": ("D={x/x es roca ^ Clasificación(x)=petrográfica}", "Clase de roca"),
    "Sample SubType": ("D={x/x es roca ^ Tipo(x)=nombre de la roca}", "Nombre de roca"),
    "Latitude": ("D={x/x es coordenada ^ x ∈ R ^ Distancia angular(x)=Latitud}", "R ^ -90 ≤ x ≤ 90"),
    "Longitude": ("D={x/x es coordenada ^ x ∈ R ^ Distancia angular(x)=Longitud}", "R ^ -180 ≤ x ≤ 180"),
    "Geographic Features": ("D={x/x es lugar ^ Tipo(x)=océano, país o región}", "Ubicación"),
    "Tectonic Setting": ("D={x/x es ambiente tectónico ^ Tipo(x)=geológico}", "Ambiente tectónico"),
    "Rock Texture": ("D={x/x es textura ^ Tipo(x)=petrográfica}", "Textura"),
    "Sample Alteration": ("D={x/x es alteración ^ Referencia(x)=descripción del autor}", "Alteración"),
    "Elevation Min (m)": ("D={x/x es distancia ^ x ∈ R ^ Referencia(x)=nivel del mar}", "R"),
    "Elevation Max (m)": ("D={x/x es distancia ^ x ∈ R ^ Referencia(x)=nivel del mar}", "R"),
    "Geologic Age": ("D={x/x es edad ^ Tipo(x)=geológica ^ Referencia(x)=Tabla Cronoestratigráfica Internacional}", "Edad geológica"),
    "Geologic Age Max (Ma)": ("D={x/x es tiempo ^ x ∈ R ^ Unidad(x)=millones de años}", "R+ ∪ {0}"),
    "Geologic Age Min (Ma)": ("D={x/x es tiempo ^ x ∈ R ^ Unidad(x)=millones de años}", "R+ ∪ {0}"),
    "Expedition": ("D={x/x es campaña de muestreo}", "Expedición"),
    "Tectonic Group": ("D={x/x es ambiente tectónico ^ Agrupación(x)=tres grupos}", "Grupo tectónico"),
    "Alteration Grade": ("D={x/x es grado de alteración ^ x ∈ N ^ 0 ≤ x ≤ 5}", "Z+ ∪ {0}"),
    "SiO2 Class": ("D={x/x es clase de roca ^ Criterio(x)=contenido de SiO2}", "Clase SiO2"),
    "N Analytes": ("D={x/x es cantidad de analitos ^ x ∈ N}", "Z+ ∪ {0}"),
}
# Rangos cualitativos con pocas categorías: se enumeran.
ENUMERADOS = {
    "Analyzed Material": "{roca total, roca total o vidrio sin especificar}",
    "Tectonic Group": "{dorsal y corteza oceánica, intraplaca y rift, margen convergente, mixto}",
    "Alteration Grade": "{0, 1, 2, 3, 4, 5}",
    "SiO2 Class": "{ultrabásica, básica, intermedia, ácida}",
}


def metodos_crudos(cruda, columnas):
    """Método analítico más frecuente de cada variable química, con su porcentaje."""
    with open(cruda / f"{PREFIJO}.csv", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        h = next(r)
        idx = {c: h.index(c + " Method") for c in columnas if c + " Method" in h}
        cuentas = {c: Counter() for c in idx}
        for fila in r:
            for c, i in idx.items():
                if fila[i]:
                    cuentas[c][fila[i]] += 1
    salida = {}
    for c, k in cuentas.items():
        total = sum(k.values())
        salida[c] = "; ".join(f"{METODOS.get(m, m)} {100 * v / total:.0f} %" for m, v in k.most_common(2)) if total else ""
    return salida


def dominio_conjunto(conjunto):
    return f"D={{x/x ∈ {conjunto}}}"


def rango(s, subtipo, conjunto):
    """R={y/ min ≤ y ≤ max} para numéricas; R={y/y ∈ conjunto} para cualitativas, como la plantilla."""
    s = s.dropna()
    if subtipo in ("continua", "discreta"):
        return f"R={{y/ {s.min():g} ≤ y ≤ {s.max():g}}}"
    if s.name in ENUMERADOS:
        return f"R={{y/y ∈ {ENUMERADOS[s.name]}}}"
    return f"R={{y/y ∈ {conjunto}}} ({s.nunique()} categorías)"


def main(cruda):
    df = pd.read_csv(RAIZ / "data" / "earthchem_limpio.csv.gz", low_memory=False)
    quimicas = [c for c in df.columns if c not in OTRAS]
    met = metodos_crudos(cruda, quimicas)
    filas = []
    for c in df.columns:
        if c in OTRAS:
            desc, tipo, sub, escala, inst, unidad = OTRAS[c]
            definicion, conjunto = DOMINIOS[c]
        else:
            simbolo, unidad = c.split(" (")[0], c.split("(")[1].rstrip(")")
            grupo = ("elemento mayor" if unidad == "wt%" and simbolo not in ("Co", "Cu", "Ni", "Zn")
                     else "tierra rara" if simbolo in TIERRAS_RARAS else "elemento traza")
            desc = f"Concentración de {NOMBRES[simbolo]} ({grupo})"
            tipo, sub, escala, inst = "cuantitativa", "continua", "razón", met.get(c, "")
            unidad = "% en peso" if unidad == "wt%" else "partes por millón"
            # La pérdida por calcinación puede ser negativa (la roca gana peso al oxidarse el hierro).
            definicion = "D={x/x es concentración ^ x ∈ R}"
            conjunto = "R" if simbolo == "LOI" else "R+ ∪ {0}"
        filas.append({"Variable": c, "Descripción": desc, "Tipo": tipo, "Subtipo": sub,
                      "Dominio (definición)": definicion, "Dominio (conjunto)": dominio_conjunto(conjunto),
                      "Rango": rango(df[c], sub, conjunto) if tipo != "identificador" else f"R={{y/y ∈ {conjunto}}}",
                      "Instrumento / método": inst, "Unidad": unidad, "Escala de medición": escala,
                      "% con dato": round(100 * df[c].notna().mean(), 1)})
    tabla = pd.DataFrame(filas)
    excel = tabla.rename(columns={"Variable": "Nombre", "Unidad": "Sistema de unidades de medida"})
    for col in ("Tipo", "Subtipo", "Escala de medición"):
        excel[col] = excel[col].str.capitalize()
    excel.to_excel(RAIZ / "data" / "tabla_variables.xlsx", index=False, sheet_name="Variables")
    (RAIZ / "docs" / "data" / "variables.json").write_text(
        json.dumps(filas, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(tabla.groupby(["Tipo", "Subtipo"]).size().to_string())


if __name__ == "__main__":
    cruda = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "data" / "raw" / "crudos"
    if not (cruda / f"{PREFIJO}.csv").exists():
        sys.exit(f"No están los CSV crudos en {cruda}\n\n{__doc__}")
    main(cruda)
