"""Informe del proceso de muestreo (Lección 3): docs/informe_muestreo.docx y .pdf.

Explica el muestreo aleatorio simple, sistemático y estratificado, cómo se aplicó a la base PetDB con
R/04_muestreo.R, compara las tres muestras con la población y cierra con el cálculo de la escala del mapa
y cómo imprimirlo. Requiere haber corrido antes R/04_muestreo.R (lee sus tablas de docs/data/tdf/).

Uso: python scripts/informe_muestreo.py      (sin -I: importa las utilidades de informe.py)
"""
import pandas as pd
from docx.shared import Pt

from informe import AZUL, GRIS, RAIZ, WEB, Informe, a_pdf, miles

DOCX = RAIZ / "docs" / "informe_muestreo.docx"
PDF = RAIZ / "docs" / "informe_muestreo.pdf"
TDF = RAIZ / "docs" / "data" / "tdf"
IMG = RAIZ / "docs" / "img"


def leer(nombre):
    return pd.read_csv(TDF / f"muestreo_{nombre}.csv")


def num(x, dec=2):
    """Número con coma decimal y punto de miles, como en el resto del informe."""
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    tam = dict(zip(*leer("tamano").T.values))
    afij, estratos, medias, rep = leer("afijacion"), leer("estratos"), leer("medias"), leer("repeticiones")
    N, n, k = int(tam["N (población)"]), int(tam["n"]), int(tam["k (sistemático)"])
    ee = dict(zip(rep.metodo, rep.error_estandar))
    peor = estratos.loc[(estratos.aleatoria - estratos.poblacion).abs().idxmax()]  # estrato más desbalanceado

    I = Informe()
    t = I.p(("Informe del proceso de muestreo", "b"))
    t.runs[0].font.size, t.runs[0].font.color.rgb = Pt(24), AZUL
    s = I.p("Muestreo aleatorio simple, sistemático y estratificado aplicado a la base EarthChem PetDB")
    s.runs[0].font.size, s.runs[0].font.color.rgb = Pt(13), GRIS
    I.p("Lección 3 · Estadística y Probabilidades · FIGEMPA – Universidad Central del Ecuador · Docente: Dr. Christian "
        "Mejía E., Ph.D. · Equipo: Rumiguano C., Fernández A., Bustamante E., Haro J., Ligña J. · Proyecto "
        "estrictamente académico.")

    I.h("1. Qué es muestrear y por qué importa", 1)
    I.p("La ", ("población", "b"), " es el conjunto completo de individuos que nos interesa; la ", ("muestra", "b"),
        " es la parte que realmente analizamos. Muestrear bien significa elegir esa parte de modo que se parezca a la "
        "población, para que lo que calculemos en la muestra (una media, un porcentaje) sirva para hablar de toda la "
        "población. Eso es lo que hace después la estadística inferencial (Unidad 2).")
    I.p("Un muestreo es ", ("probabilístico", "b"), " cuando cada individuo tiene una probabilidad conocida (y en los "
        "métodos de este informe, igual) de ser elegido, y la elección la hace el azar, no la persona. Es la única forma "
        "de garantizar representatividad y de medir el error. El muestreo ", ("no probabilístico", "b"),
        " o circunstancial (tomar lo que está a mano, lo que conviene o lo que alguien elige) no debe usarse para "
        "inferir, porque no se puede saber cuánto se aparta de la población.")
    I.p(("En nuestro proyecto: ", "b"), "el marco muestral es la base limpia de PetDB, con N = ", miles(N),
        " análisis de roca total. Las tres muestras de este informe se sacan de ese marco con el programa ",
        ("R/04_muestreo.R", "c"), ". Ojo: la base en sí no es una muestra probabilística de todas las rocas del "
        "planeta (reúne lo que los investigadores decidieron publicar, con más fondo oceánico que continente), así que "
        "las conclusiones valen para la población de análisis publicados en PetDB.")

    I.h("2. Tamaño de la muestra", 1)
    I.p("Para estimar una proporción con un error máximo e y un nivel de confianza dado se usa:")
    I.codigo("n0 = z² · p · q / e²          n = n0 / (1 + (n0 − 1) / N)")
    I.p("La segunda fórmula es la corrección por población finita. Valores usados:")
    I.tabla([["Dato", "Valor", "Por qué"],
             ["N", miles(N), "filas de la base limpia (marco muestral)"],
             ["Confianza", "95 % (z = 1,96)", "el valor habitual"],
             ["p = q", "0,5", "la peor varianza posible: da el n más grande, el más seguro"],
             ["e", "3 %", "con 5 % saldrían 384 filas y el estrato más chico tendría apenas 5"],
             ["n0", num(float(tam["n0"]), 1), "sin corregir"],
             ["n", miles(n), "tamaño final de cada una de las tres muestras"]], [3, 3.5, 9.5])
    I.p("Las tres muestras tienen el mismo tamaño para poder compararlas en igualdad de condiciones. Se usa una "
        "semilla fija (", ("set.seed(2026)", "c"), "), así cualquiera que corra el script obtiene exactamente las mismas "
        "muestras.")

    I.h("3. Muestreo aleatorio simple", 1)
    I.p(("Idea: ", "b"), "un sorteo. Todas las filas tienen la misma probabilidad de salir (n/N) y cualquier conjunto de "
        "n filas tiene la misma chance de ser la muestra. Es como meter los ", miles(N), " análisis en una ánfora y "
        "sacar ", miles(n), " sin devolverlos.")
    I.p(("En R: ", "b"), ("sample(N, n)", "c"), " devuelve n números de fila al azar, sin repetir.")
    I.p(("Ventaja: ", "b"), "es el más simple y la base de todas las fórmulas de inferencia. ", ("Desventaja: ", "b"),
        "por azar puede salir desbalanceada; en nuestra muestra, ", peor.estrato, " quedó con ", num(peor.aleatoria, 1),
        " % cuando en la población es ", num(peor.poblacion, 1), " %.")

    I.h("4. Muestreo sistemático", 1)
    I.p(("Idea: ", "b"), "elegir a intervalos regulares. Se calcula el intervalo k = N / n, se sortea un arranque i entre "
        "1 y k, y se toman las filas i, i + k, i + 2k, …, i + (n − 1)k.")
    I.p("Con nuestros datos: k = ", miles(N), " / ", miles(n), " ≈ ", str(k), ". Si el arranque sale 37, la muestra es "
        "la fila 37, 187, 337, 487… hasta completar ", miles(n), ".")
    I.p(("En R: ", "b"), ("i <- sample(k, 1); i + (0:(n - 1)) * k", "c"))
    I.p(("Ventaja: ", "b"), "es fácil de aplicar en campo (una muestra cada 50 m en una trinchera, un sondaje cada "
        "100 m en una malla) y reparte la muestra a lo largo de toda la lista. ", ("Riesgo: ", "b"),
        "si la lista tiene un orden o un ciclo que coincide con k, la muestra se sesga. En PetDB las filas vienen "
        "agrupadas por publicación (muchas muestras seguidas del mismo artículo y la misma zona); por eso, al repetir "
        "el muestreo, el sistemático resultó el menos preciso de los tres (sección 6).")

    I.h("5. Muestreo estratificado", 1)
    I.p(("Idea: ", "b"), "dividir la población en ", ("estratos", "b"), " (grupos homogéneos por dentro y distintos entre "
        "sí) y hacer un muestreo aleatorio simple dentro de cada uno. Así ningún grupo importante queda fuera o "
        "sub-representado por mala suerte.")
    I.p(("Estratos elegidos: ", "b"), "el ambiente tectónico agrupado (", ("Tectonic Group", "c"), "). Es la variable que "
        "más cambia la química de la roca: los basaltos de dorsal, las rocas de arco volcánico y las de intraplaca "
        "tienen composiciones distintas, pero dentro de cada ambiente se parecen más entre sí. Las 304 filas sin "
        "ambiente forman su propio estrato para no perderlas.")
    I.p(("Afijación proporcional: ", "b"), "cada estrato recibe una parte de la muestra igual a su peso en la "
        "población, n_h = n · N_h / N (redondeando para que la suma dé exactamente n):")
    I.tabla([["Estrato", "N_h", "Peso (%)", "n_h"]] +
            [[r.estrato, miles(int(r.N_h)), num(r.peso), str(int(r.n_h))] for r in afij.itertuples()]
            + [["Total", miles(N), "100,00", str(n)]], [6, 3, 3, 2.5])
    I.p(("En R: ", "b"), "para cada estrato h se toman al azar n_h de sus filas con ", ("sample()", "c"),
        "; después se juntan.")

    I.h("6. Resultados: ¿qué muestra se parece más a la población?", 1)
    I.p(("Porcentaje de cada ambiente tectónico. ", "b"), "La muestra estratificada lo reproduce casi exacto, porque "
        "así fue construida; las otras dos se acercan pero con diferencias de hasta 2 puntos.")
    I.tabla([["Estrato", "Población", "Aleatoria", "Sistemática", "Estratificada"]] +
            [[r.estrato, num(r.poblacion), num(r.aleatoria), num(r.sistematica), num(r.estratificada)]
             for r in estratos.itertuples()], [5.5, 2.6, 2.6, 2.6, 2.8])
    I.imagen(IMG / "r" / "muestreo_estratos.png", 15, "Gráfica 1. Porcentaje por ambiente tectónico en la población "
             "y en cada muestra (R/04_muestreo.R).")
    I.p(("Medias de tres variables. ", "b"), "SiO2 y MgO solo están medidos en parte de las filas (el informe del "
        "proyecto explica por qué); la media se calcula con las filas que sí tienen dato.")
    I.tabla([["Variable", "Población", "Aleatoria", "Sistemática", "Estratificada"]] +
            [[r.variable] + [num(v) if r.variable != "Publication Year" else f"{v:.2f}".replace(".", ",")
                             for v in (r.poblacion, r.aleatoria, r.sistematica, r.estratificada)]
             for r in medias.itertuples()], [4.5, 2.8, 2.8, 2.8, 2.8])
    I.p(("Una sola muestra no alcanza para juzgar un método: ", "b"), "cualquier método puede tener suerte o mala "
        "suerte una vez. Por eso el script repite cada método 500 veces y mira cuánto varía la media de SiO2 de una "
        "muestra a otra. Esa variación es el ", ("error estándar", "b"), ": cuanto más chico, más preciso el método.")
    I.tabla([["Método", "Promedio de las 500 medias", "Error estándar", "Sesgo"]] +
            [[r.metodo, num(r.media_de_las_medias, 3), num(r.error_estandar, 4), num(r.sesgo, 4)]
             for r in rep.itertuples()], [3.5, 5, 3.5, 3])
    I.imagen(IMG / "r" / "muestreo_repeticiones.png", 15, "Gráfica 2. Media de SiO2 en 500 muestras de cada método; "
             "la línea punteada es la media de la población.")
    I.p(("Conclusión. ", "b"), "Los tres métodos están centrados en la media real (sesgo casi cero), pero el "
        "estratificado es el más preciso (error estándar ", num(ee["estratificada"], 2), " wt% frente a ",
        num(ee["aleatoria"], 2), " del aleatorio simple y ", num(ee["sistematica"], 2), " del sistemático): al "
        "fijar la proporción de cada ambiente tectónico elimina una fuente de variación. El sistemático queda último "
        "por el orden de la base por publicación. Por eso, para la Unidad 2 (inferencia) se usará la ",
        ("muestra estratificada", "b"), ".")

    I.h("7. ¿Se aplicó a la data?", 1)
    I.p("Sí, desde esta lección. Hasta ahora la estadística descriptiva se hizo con la base completa (no hacía falta "
        "muestrear para describir). Ahora las tres muestras están guardadas y se pueden abrir en Excel:")
    I.lista([(("data/muestras/muestra_aleatoria.csv", "c"),), (("data/muestras/muestra_sistematica.csv", "c"),),
             (("data/muestras/muestra_estratificada.csv", "c"), " — la que se usará en la Unidad 2"),
             (("R/salidas/Muestreo.xlsx", "c"), " — todas las tablas de este informe")])
    I.p("Para volver a generarlas: abrir ", ("R/04_muestreo.R", "c"), " en RStudio con la carpeta del repositorio como "
        "directorio de trabajo y ejecutar todo (o ", ("Rscript R/04_muestreo.R", "c"), "). Este informe se genera con ",
        ("python scripts/informe_muestreo.py", "c"), ".")

    I.h("8. Escala del mapa de ubicación y cómo imprimirlo", 1)
    I.p(("Cálculo de la escala. ", "b"), "El mapa muestra los 360° de longitud. Sobre el ecuador, 360° son 40 075 km = "
        "40 075 000 000 mm. La escala es esa distancia dividida para el ancho del marco del mapa en el papel. Hay dos "
        "versiones de la lámina, la A3 es la A4 ampliada:")
    I.codigo("A4: marco de 264 mm   →   40 075 000 000 / 264   ≈ 151 800 000   →   1 : 151 000 000\n"
             "A3: marco de 373 mm   →   40 075 000 000 / 373,4 ≈ 107 300 000   →   1 : 107 000 000")
    I.p("Es una escala ", ("válida sobre el ecuador", "b"), ": en un mapa mundial las distancias se deforman hacia los "
        "polos, por eso el membrete y la escala gráfica lo aclaran.")
    I.tabla([["", "A4", "A3"],
             ["Archivo", "docs/mapa_ubicacion_A4.pdf", "docs/mapa_ubicacion_A3.pdf"],
             ["Tamaño de la hoja", "297 × 210 mm", "420 × 297 mm"],
             ["Escala", "1 : 151 000 000", "1 : 107 000 000"],
             ["Ancho del marco del mapa (regla)", "26,4 cm", "37,3 cm"],
             ["Barra de 2 500 km (regla)", "≈ 1,6 cm", "≈ 2,3 cm"]], [6, 5, 5])
    I.p(("Cómo imprimirlo a escala:", "b"))
    I.lista(["Descargar el PDF del tamaño de papel que se va a usar (en la web: sección Mapa de ubicación o página "
             "Datos). Son vectoriales y miden exactamente el tamaño de la hoja.",
             "Papel del mismo tamaño que el PDF (A3 para el A3), orientación horizontal, a color.",
             "En el diálogo de impresión elegir «Tamaño real» o «Escala 100 %». NO usar «Ajustar a la página», "
             "«Ajustar al área imprimible» ni «Reducir páginas grandes»: cambian el tamaño y la escala deja de valer. "
             "No imprimir el PDF A4 en hoja A3 «ampliado»: para eso está el PDF A3.",
             "Verificar con una regla el ancho del marco y la barra de escala (tabla de arriba). Si da distinto, la "
             "impresora escaló la hoja.",
             "Desde QGIS también se puede: abrir mapa_ubicacion.qgz (del .zip de la web), Proyecto → Diseños → «Mapa "
             "de ubicación A3» (o A4) y Diseño → Imprimir o Exportar como PDF, con la página al 100 %."], numerada=True)
    I.p(("Web del proyecto: ", "b"), WEB)

    I.d.core_properties.title = "Informe del proceso de muestreo — Geoquímica de rocas PetDB"
    I.d.core_properties.author = "Rumiguano, Fernández, Bustamante, Haro, Ligña"
    I.d.save(DOCX)
    print("Word:", DOCX)
    a_pdf(DOCX, PDF)


if __name__ == "__main__":
    main()
