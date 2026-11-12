"""Tabla de variables del proyecto (Lección 4), con el formato que pidió el docente (tabla del proyecto modelo
"geoquimicaglobal"): N°, nombre, nombre corto, nombre en español, descripción, tipo, subtipo, dominio (una sola
columna), rango, instrumento, sistema de unidades, escala de medición, variable de interés y variable de individuo.

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

# Qué indica cada analito. La descripción no repite el nombre de la variable (observación del docente):
# dice qué mide y para qué sirve.
PAPEL = {
    "SiO2": "componente principal de los silicatos; separa las rocas en ultrabásicas, básicas, intermedias y ácidas",
    "Al2O3": "forma feldespatos y micas; alto en rocas félsicas y bajo en peridotitas",
    "Fe2O3": "hierro en estado oxidado (Fe³⁺); aumenta con la alteración",
    "Fe2O3T": "todo el hierro de la roca expresado como si estuviera oxidado (Fe³⁺)",
    "FeO": "hierro en estado reducido (Fe²⁺), propio del olivino y el piroxeno",
    "FeOT": "todo el hierro expresado como Fe²⁺ (FeOT = FeO + 0,8998·Fe2O3)",
    "MgO": "abunda en olivino y piroxeno; indica qué tan primitivo (máfico) es el magma",
    "MnO": "acompaña al hierro en los minerales ferromagnesianos; casi siempre menos de 1 %",
    "CaO": "presente en plagioclasa, piroxeno y carbonatos",
    "Na2O": "álcali de la plagioclasa sódica; sube en rocas evolucionadas y con la alteración por agua de mar",
    "K2O": "álcali del feldespato potásico y las micas; alto en granitos, muy bajo en basaltos de dorsal",
    "P2O5": "se aloja en el apatito; suele estar en décimas de por ciento",
    "LOI": "masa que pierde la roca al calentarla a unos 1 000 °C (agua y CO2); indica alteración y puede ser negativa",
    "Co": "metal que acompaña al magnesio en el olivino",
    "Cu": "metal ligado a los sulfuros; de interés minero",
    "Ni": "metal que entra en el olivino; alto en peridotitas",
    "Zn": "metal ligado a sulfuros y óxidos de hierro y titanio",
    "Rb": "álcali que reemplaza al potasio; se concentra en rocas félsicas",
    "Sr": "reemplaza al calcio en la plagioclasa",
    "Ba": "reemplaza al potasio en feldespatos y micas; se mueve con la alteración",
    "Cs": "álcali muy incompatible y móvil",
    "Pb": "metal de los sulfuros; también se forma por el decaimiento del uranio y el torio",
    "Y": "se comporta como las tierras raras pesadas",
    "Zr": "se aloja en el circón; inmóvil, sirve para clasificar rocas alteradas",
    "Hf": "gemelo geoquímico del Zr, también en el circón",
    "Nb": "elemento de alta carga; bajo en los arcos volcánicos",
    "Ta": "gemelo del Nb; marcador del ambiente tectónico",
    "Th": "radiactivo e incompatible; se enriquece en la corteza continental",
    "U": "radiactivo e incompatible; móvil en condiciones oxidantes",
    "V": "metal de transición que entra en la magnetita y el piroxeno",
    "Cr": "metal que se concentra en la cromita y el piroxeno; alto en rocas ultrabásicas",
    "Sc": "metal de transición que entra en el piroxeno",
    "Ga": "reemplaza al aluminio en los feldespatos",
    "Li": "álcali liviano, móvil con los fluidos",
    "La": "tierra rara liviana, la más incompatible",
    "Ce": "tierra rara liviana más abundante; puede oxidarse a Ce⁴⁺",
    "Pr": "tierra rara liviana", "Nd": "tierra rara liviana; su isótopo 143 sirve para rastrear el origen del magma",
    "Sm": "tierra rara liviana a media", "Eu": "tierra rara que entra en la plagioclasa (anomalía de Eu)",
    "Gd": "tierra rara media", "Tb": "tierra rara media", "Dy": "tierra rara pesada", "Ho": "tierra rara pesada",
    "Er": "tierra rara pesada", "Tm": "tierra rara pesada, de las menos abundantes",
    "Yb": "tierra rara pesada; la retiene el granate", "Lu": "tierra rara pesada más compatible; la retiene el granate",
}

# Variables no químicas:
# nombre corto, nombre en español, descripción, tipo, subtipo, escala, instrumento, unidad, dominio, ¿de interés?
OTRAS = {
    "Sample Name": ("NOMBRE_MUESTRA", "Nombre de la muestra",
                    "Código alfanumérico que el autor del estudio dio al fragmento de roca para reconocerlo",
                    "cualitativa", "nominal", "nominal", "registro del autor", "—",
                    "D={x/x es código de identificación ^ Pertenencia(x)=muestra}", False),
    "Sample URL": ("ENLACE_MUESTRA", "Enlace de la muestra",
                   "Dirección web de la ficha del ejemplar en PetDB, con todos sus metadatos",
                   "cualitativa", "nominal", "nominal", "PetDB", "—",
                   "D={x/x es dirección web ^ Sitio(x)=PetDB}", False),
    "Citation": ("CITA", "Cita bibliográfica",
                 "Autores, revista y año del trabajo donde se publicaron los resultados del análisis",
                 "cualitativa", "nominal", "nominal", "revisión bibliográfica", "—",
                 "D={x/x es artículo científico ^ Revisión(x)=por pares}", False),
    "Publication Year": ("ANIO_PUB", "Año de publicación",
                         "Momento en que salió el trabajo que reportó los resultados; mide la antigüedad del dato",
                         "cuantitativa", "discreta", "intervalo", "extraído de la cita", "año",
                         "D={x/x es año ^ x ∈ Z+}", True),
    "Analyzed Material": ("MATERIAL", "Material analizado",
                          "Fracción de la roca que entró al laboratorio: la roca entera molida, o roca o vidrio sin precisar",
                          "cualitativa", "nominal (binaria)", "nominal", "registro PetDB", "—",
                          "D={x/x es fracción de roca ^ Uso(x)=análisis químico}", False),
    "Sample Type": ("TIPO_ROCA", "Tipo de roca",
                    "Clasificación general por origen: ígnea volcánica o plutónica, metamórfica, xenolito, etc.",
                    "cualitativa", "nominal", "nominal", "descripción petrográfica", "—",
                    "D={x/x es clase de roca ^ Clasificación(x)=genética}", True),
    "Sample SubType": ("NOMBRE_ROCA", "Nombre de la roca",
                       "Denominación petrográfica específica: basalto, gabro, peridotita, andesita…",
                       "cualitativa", "nominal", "nominal", "descripción petrográfica", "—",
                       "D={x/x es nombre de roca ^ Clasificación(x)=petrográfica}", True),
    "Latitude": ("LATITUD", "Latitud",
                 "Distancia angular al norte (+) o al sur (−) del ecuador del punto de recolección",
                 "cuantitativa", "continua", "intervalo", "GPS / navegación del buque", "grados decimales",
                 "D={x/x ∈ R ^ -90 ≤ x ≤ 90}", True),
    "Longitude": ("LONGITUD", "Longitud",
                  "Distancia angular al este (+) o al oeste (−) del meridiano de Greenwich del punto de recolección",
                  "cuantitativa", "continua", "intervalo", "GPS / navegación del buque", "grados decimales",
                  "D={x/x ∈ R ^ -180 ≤ x ≤ 180}", True),
    "Geographic Features": ("RASGO_GEOGRAFICO", "Rasgo geográfico",
                            "Océano, país, dorsal o provincia donde está el punto de recolección, según PetDB",
                            "cualitativa", "nominal", "nominal", "registro PetDB", "—",
                            "D={x/x es océano, país o región de la Tierra}", False),
    "Tectonic Setting": ("AMBIENTE_TECT", "Ambiente tectónico",
                         "Contexto de placas donde se formó la roca: dorsal, arco volcánico, rift, isla oceánica…",
                         "cualitativa", "nominal", "nominal", "interpretación geológica", "—",
                         "D={x/x es contexto de placas tectónicas}", True),
    "Rock Texture": ("TEXTURA", "Textura de la roca",
                     "Tamaño, forma y arreglo de los cristales (afírica, porfirítica, granular…) según el autor",
                     "cualitativa", "nominal", "nominal", "descripción petrográfica", "—",
                     "D={x/x es textura ^ Tipo(x)=petrográfica}", True),
    "Sample Alteration": ("ALTERACION_TXT", "Alteración de la muestra",
                          "Texto original con el que el autor calificó cuánto cambió la roca por el agua o la intemperie",
                          "cualitativa", "ordinal", "ordinal", "descripción petrográfica", "—",
                          "D={x/x es calificación de alteración ^ Fuente(x)=autor del estudio}", False),
    "Elevation Min (m)": ("ELEV_MIN_M", "Elevación mínima (m)",
                          "Cota más baja del punto de recolección respecto al nivel del mar; negativa en el fondo marino",
                          "cuantitativa", "continua", "razón", "altímetro / ecosonda", "m",
                          "D={x/x es distancia vertical ^ x ∈ R ^ Referencia(x)=nivel del mar}", True),
    "Elevation Max (m)": ("ELEV_MAX_M", "Elevación máxima (m)",
                          "Cota más alta del punto de recolección respecto al nivel del mar; negativa en el fondo marino",
                          "cuantitativa", "continua", "razón", "altímetro / ecosonda", "m",
                          "D={x/x es distancia vertical ^ x ∈ R ^ Referencia(x)=nivel del mar}", True),
    "Geologic Age": ("EDAD_GEOL", "Edad geológica",
                     "Período o época de la escala del tiempo geológico en que se formó la roca",
                     "cualitativa", "ordinal", "intervalo", "estratigrafía", "—",
                     "D={x/x es unidad de tiempo geológico ^ Referencia(x)=Tabla Cronoestratigráfica Internacional}", True),
    "Geologic Age Max (Ma)": ("EDAD_MAX_MA", "Edad máxima (Ma)",
                              "Límite más antiguo estimado para la formación de la roca, contado hacia atrás desde hoy",
                              "cuantitativa", "continua", "intervalo", "geocronología", "millones de años (Ma)",
                              "D={x/x ∈ R ^ 0 ≤ x ≤ 4567}", True),
    "Geologic Age Min (Ma)": ("EDAD_MIN_MA", "Edad mínima (Ma)",
                              "Límite más reciente estimado para la formación de la roca, contado hacia atrás desde hoy",
                              "cuantitativa", "continua", "intervalo", "geocronología", "millones de años (Ma)",
                              "D={x/x ∈ R ^ 0 ≤ x ≤ 4567}", True),
    "Expedition": ("EXPEDICION", "Expedición",
                   "Crucero, campaña de perforación (DSDP, ODP) o salida de campo en que se recolectó el ejemplar",
                   "cualitativa", "nominal", "nominal", "registro PetDB", "—",
                   "D={x/x es campaña de muestreo}", False),
    "Tectonic Group": ("GRUPO_TECT", "Grupo tectónico",
                       "Reagrupación del contexto de placas en tres clases (dorsal, intraplaca, margen convergente) más mixto",
                       "cualitativa", "nominal", "nominal", "derivada de Tectonic Setting", "—",
                       "D={dorsal y corteza oceánica, intraplaca y rift, margen convergente, mixto}", True),
    "Alteration Grade": ("GRADO_ALTER", "Grado de alteración",
                         "Escala derivada del texto del autor: 0 fresca, 1 leve, 2 moderada, 3 extensa, 4 casi total, 5 total",
                         "cualitativa", "ordinal", "ordinal", "derivada de Sample Alteration", "—",
                         "D={0, 1, 2, 3, 4, 5}", True),
    "SiO2 Class": ("CLASE_SIO2", "Clase según SiO2",
                   "Categoría por contenido de sílice (wt%): ultrabásica < 45 ≤ básica < 52 ≤ intermedia < 63 ≤ ácida",
                   "cualitativa", "ordinal", "ordinal", "derivada de SiO2 (wt%)", "—",
                   "D={ultrabásica, básica, intermedia, ácida}", True),
    "N Analytes": ("N_ANALITOS", "Número de analitos",
                   "Cuántos óxidos o elementos distintos se midieron en el ejemplar; indica qué tan completo es el análisis",
                   "cuantitativa", "discreta", "razón", "conteo", "analitos",
                   "D={x/x ∈ Z ^ x ≥ 0}", True),
}

# Rangos cualitativos con pocas categorías: se enumeran (en español).
ENUMERADOS = {
    "Analyzed Material": "{roca total, roca total o vidrio sin especificar}",
    "Tectonic Group": "{dorsal y corteza oceánica, intraplaca y rift, margen convergente, mixto}",
    "Alteration Grade": "{0, 1, 2, 3, 4, 5}",
    "SiO2 Class": "{ultrabásica, básica, intermedia, ácida}",
}
INDIVIDUO = "de cada uno de los análisis químicos de roca total de la base EarthChem PetDB"


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


def rango(s, subtipo):
    """Valores que la variable toma de verdad en la base (el dominio es lo que podría tomar en teoría)."""
    s = s.dropna()
    if subtipo == "continua":
        return f"R={{x/x ∈ R ^ {s.min():g} ≤ x ≤ {s.max():g}}}"
    if subtipo == "discreta":
        return f"R={{x/x ∈ Z ^ {s.min():g} ≤ x ≤ {s.max():g}}}"
    if s.name in ENUMERADOS:
        return f"R={ENUMERADOS[s.name]}"
    rango_ = f"R={{x/x ∈ D ^ x está en la base}}: {s.nunique()} valores distintos"
    top = [str(v).strip('"') for v in s.value_counts().index[:3]]
    if max(map(len, top)) > 40:  # citas y enlaces: ejemplos demasiado largos para la tabla
        return rango_
    return f"{rango_} (más frecuentes: {', '.join(top)})"


def main(cruda):
    df = pd.read_csv(RAIZ / "data" / "earthchem_limpio.csv.gz", low_memory=False)
    quimicas = [c for c in df.columns if c not in OTRAS]
    met = metodos_crudos(cruda, quimicas)
    filas = []
    for n, c in enumerate(df.columns, 1):
        if c in OTRAS:
            corto, espanol, desc, tipo, sub, escala, inst, unidad, dominio, interes = OTRAS[c]
        else:
            simbolo, unidad = c.split(" (")[0], c.split("(")[1].rstrip(")")
            corto = f"{simbolo.upper()}_{'PCT' if unidad == 'wt%' else 'PPM'}"
            espanol = f"{NOMBRES[simbolo][0].upper()}{NOMBRES[simbolo][1:]}, {unidad}"  # p. ej. "Cromo, ppm"
            if unidad == "wt%":
                desc = ("Gramos por cada 100 g de roca" if simbolo not in ("Co", "Cu", "Ni", "Zn")
                        else "Gramos por cada 100 g de roca (la misma medida que la columna en ppm: 1 wt% = 10 000 ppm)")
                dominio = "D={x/x ∈ R ^ x ≤ 100}" if simbolo == "LOI" else "D={x/x ∈ R ^ 0 ≤ x ≤ 100}"
            else:
                desc = "Gramos por tonelada de roca"
                dominio = "D={x/x ∈ R ^ 0 ≤ x ≤ 1 000 000}"
            desc = f"{desc}; {PAPEL[simbolo]}"
            tipo, sub, escala, inst, interes = "cuantitativa", "continua", "razón", met.get(c, ""), True
            unidad = "% en peso" if unidad == "wt%" else "partes por millón"
        filas.append({"N°": n, "Variable": c, "Nombre corto": corto, "Variable (español)": espanol,
                      "Descripción": desc, "Tipo": tipo, "Subtipo": sub, "Dominio": dominio,
                      "Rango": rango(df[c], sub), "Instrumento / método": inst, "Unidad": unidad,
                      "Escala de medición": escala, "Variable de interés": "SI" if interes else "NO",
                      "Variable de individuo": f"{c} {INDIVIDUO}",
                      "% con dato": round(100 * df[c].notna().mean(), 1)})
    tabla = pd.DataFrame(filas)
    excel = tabla.rename(columns={"Variable": "Nombre", "Variable (español)": "Nombre en español",
                                  "Instrumento / método": "Instrumento", "Unidad": "Sistema de unidades de medida"})
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
