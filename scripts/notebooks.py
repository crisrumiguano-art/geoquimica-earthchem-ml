"""Unidad 4 (L18–L20): dos notebooks de Google Colab con redes neuronales (Keras), como el proyecto modelo del docente:
regresión (níquel a partir de los óxidos mayores, hiperparámetros con Optuna) y clasificación (ambiente tectónico de
rocas volcánicas). Los problemas se eligieron probando (ver openwiki): son los que dan buenos resultados y se pueden
comparar con los modelos de la Unidad 3.

Uso (con TensorFlow y Optuna instalados, p. ej. el venv C:/Users/dalem/venv-geoml):
    venv-geoml/Scripts/python.exe scripts/notebooks.py          # escribe y ejecuta los notebooks
Salidas: notebooks/*.ipynb (con resultados), docs/img/ml/*.png, docs/data/ml.json
"""
import subprocess
import sys
from pathlib import Path

import nbformat as nbf

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "notebooks"
REPO = "crisrumiguano-art/geoquimica-earthchem-ml"

COMUN_INICIO = f'''import os, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

tf.keras.utils.set_random_seed(2026)        # semilla: los resultados se pueden repetir

# Base de datos: si se corre en el repositorio usa la copia local; en Colab la descarga de GitHub (26 MB)
local = "../data/earthchem_limpio.csv.gz"
url = "https://github.com/{REPO}/raw/main/data/earthchem_limpio.csv.gz"
base = pd.read_csv(local if os.path.exists(local) else url, low_memory=False)
print(base.shape)

# Las figuras se guardan para la web solo cuando se corre dentro del repositorio
WEB = "../docs/img/ml" if os.path.isdir("../docs") else None
if WEB:
    os.makedirs(WEB, exist_ok=True)
def guardar(nombre):
    if WEB:
        plt.savefig(f"{{WEB}}/{{nombre}}.png", dpi=130, bbox_inches="tight")'''

OXIDOS = '["SiO2 (wt%)", "Al2O3 (wt%)", "MgO (wt%)", "CaO (wt%)", "Na2O (wt%)", "K2O (wt%)", "P2O5 (wt%)", "MnO (wt%)"]'


def md(t):
    return nbf.v4.new_markdown_cell(t)


def code(t):
    return nbf.v4.new_code_cell(t)


def cabecera(titulo, problema):
    return md(f"""# {titulo}

**Unidad 4 · Machine Learning** · Geoquímica de rocas con datos de EarthChem PetDB · Estadística y Probabilidades,
FIGEMPA – UCE. Proyecto estrictamente académico.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/{REPO}/blob/main/notebooks/{{archivo}})

{problema}

**Cómo usarlo:** en Colab, *Entorno de ejecución → Ejecutar todas*. Tarda unos minutos.""")


REGRESION = [
    None,  # cabecera
    md("""## 0. De la regresión clásica a la red neuronal

En la Unidad 3 el níquel se explicó con **una** variable (MgO) y una curva elegida a mano. Una **red neuronal** es una
regresión con muchas variables a la vez y sin elegir la forma de la curva: aprende la forma sola.

- Una **neurona** hace lo mismo que una regresión lineal múltiple, y = w₁x₁ + w₂x₂ + … + b, y después aplica una
  **función de activación** (ReLU: si el resultado es negativo da 0). La activación es lo que permite curvas.
- Muchas neuronas en **capas** forman la red. La idea viene de McCulloch y Pitts (1943) y del perceptrón de Rosenblatt
  (1958); la **retropropagación** (1986) es el método para entrenarla: se calcula el error, se ve cuánto aporta cada peso
  y se lo corrige un poco (**descenso del gradiente**). Cada pasada completa por los datos es una **época**.

**Problema:** el níquel es un metal crítico. ¿Se puede estimar el Ni de una roca a partir de sus óxidos mayores, que se
miden en casi todos los análisis?"""),
    md("## 1. Librerías y carga de datos"),
    code(COMUN_INICIO),
    md("""## 2. Preprocesamiento

- Variables de entrada: los 8 óxidos mayores. Salida: **log10(Ni)**, porque el níquel va de menos de 1 a miles de ppm
  (igual que en la Unidad 3, los logaritmos hacen que todos los órdenes de magnitud pesen igual).
- Solo filas con todo completo: no se inventa ningún dato.
- **División**: 70 % entrenamiento, 15 % validación (para elegir hiperparámetros y parar a tiempo) y 15 % prueba (solo
  al final, para medir el resultado con datos que la red nunca vio).
- **Normalización**: cada variable se lleva a media 0 y desviación 1 con los datos de entrenamiento."""),
    code(f'''ENTRADAS = {OXIDOS}
datos = base[ENTRADAS + ["Ni (ppm)"]].dropna()
datos = datos[datos["Ni (ppm)"] > 0]
X = datos[ENTRADAS].values
y = np.log10(datos["Ni (ppm)"].values)
print("filas completas:", len(datos))

X_ent, X_resto, y_ent, y_resto = train_test_split(X, y, test_size=0.30, random_state=2026)
X_val, X_prueba, y_val, y_prueba = train_test_split(X_resto, y_resto, test_size=0.50, random_state=2026)
escala = StandardScaler().fit(X_ent)              # se ajusta SOLO con entrenamiento
X_ent, X_val, X_prueba = escala.transform(X_ent), escala.transform(X_val), escala.transform(X_prueba)
print("entrenamiento:", len(y_ent), " validación:", len(y_val), " prueba:", len(y_prueba))'''),
    md("""## 3. Optimización de hiperparámetros con Optuna

Los **hiperparámetros** son las decisiones de diseño: cuántas capas, cuántas neuronas, qué tan rápido aprende. En vez de
probar a mano, **Optuna** prueba combinaciones y se queda con la que da menor error en validación (prueba y error
automático)."""),
    code('''%pip install -q optuna
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

def crear_red(capas, neuronas, tasa, abandono):
    red = keras.Sequential([layers.Input(shape=(X_ent.shape[1],))])
    for i in range(capas):
        red.add(layers.Dense(max(neuronas // (2 ** i), 8), activation="relu"))   # cada capa con la mitad de neuronas
        red.add(layers.Dropout(abandono))            # apaga neuronas al azar: evita memorizar (sobreajuste)
    red.add(layers.Dense(1))                         # una salida: log10(Ni)
    red.compile(optimizer=keras.optimizers.Adam(tasa), loss="mse", metrics=["mae"])
    return red

def objetivo(prueba):
    capas = prueba.suggest_int("capas", 1, 3)
    neuronas = prueba.suggest_categorical("neuronas", [32, 64, 128])
    tasa = prueba.suggest_float("tasa_aprendizaje", 1e-4, 1e-2, log=True)
    abandono = prueba.suggest_float("abandono", 0.0, 0.3)
    red = crear_red(capas, neuronas, tasa, abandono)
    h = red.fit(X_ent, y_ent, validation_data=(X_val, y_val), epochs=40, batch_size=256, verbose=0,
                callbacks=[keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)])
    return min(h.history["val_loss"])

estudio = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=2026))
estudio.optimize(objetivo, n_trials=20)
print("mejores hiperparámetros:", estudio.best_params)
print("error de validación (MSE):", round(estudio.best_value, 4))'''),
    code('''pruebas = estudio.trials_dataframe()
plt.figure(figsize=(8, 4))
plt.plot(pruebas["number"], pruebas["value"], "o", color="#3987e5", label="cada prueba")
plt.plot(pruebas["number"], pruebas["value"].cummin(), color="#d95926", lw=2, label="mejor hasta ahí")
plt.xlabel("Prueba de Optuna"); plt.ylabel("Error de validación (MSE)"); plt.legend()
plt.title("Gráfica N° 1: Búsqueda de hiperparámetros con Optuna")
guardar("reg_optuna"); plt.show()'''),
    md("## 4. Entrenamiento con los mejores hiperparámetros"),
    code('''p = estudio.best_params
red = crear_red(p["capas"], p["neuronas"], p["tasa_aprendizaje"], p["abandono"])
red.summary()
historia = red.fit(X_ent, y_ent, validation_data=(X_val, y_val), epochs=150, batch_size=256, verbose=0,
                   callbacks=[keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)])
print("épocas entrenadas:", len(historia.history["loss"]))'''),
    code('''plt.figure(figsize=(8, 4))
plt.plot(historia.history["loss"], color="#3987e5", lw=2, label="entrenamiento")
plt.plot(historia.history["val_loss"], color="#d95926", lw=2, label="validación")
plt.xlabel("Época"); plt.ylabel("Error (MSE)"); plt.legend()
plt.title("Gráfica N° 2: Curvas de aprendizaje")
guardar("reg_curvas"); plt.show()'''),
    md("""Si las dos curvas bajan juntas y se estabilizan, la red aprendió sin **sobreajuste** (memorizar el entrenamiento).
Si la de validación subiera mientras la de entrenamiento baja, habría sobreajuste; si las dos quedaran altas,
**subajuste** (la red es demasiado simple)."""),
    md("## 5. Evaluación con los datos de prueba"),
    code('''from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
pred = red.predict(X_prueba, verbose=0).ravel()
r2 = r2_score(y_prueba, pred)
rmse = mean_squared_error(y_prueba, pred) ** 0.5
mae = mean_absolute_error(y_prueba, pred)
print(f"R² = {r2:.3f}   RMSE = {rmse:.3f} (log10)   MAE = {mae:.3f} (log10)")
print(f"En ppm, el error típico es un factor de {10 ** mae:.2f} (el Ni estimado suele estar entre /{10 ** mae:.2f} y x{10 ** mae:.2f} del real)")

plt.figure(figsize=(6, 6))
plt.scatter(10 ** y_prueba, 10 ** pred, s=4, alpha=0.3, color="#3987e5")
lim = [1, 10 ** max(y_prueba.max(), pred.max())]
plt.plot(lim, lim, color="#d95926", lw=2)
plt.xscale("log"); plt.yscale("log")
plt.xlabel("Ni real (ppm)"); plt.ylabel("Ni estimado por la red (ppm)")
plt.title(f"Gráfica N° 3: Real vs estimado (R² = {r2:.2f})")
guardar("reg_real_vs_estimado"); plt.show()'''),
    md("""## 6. Comparación con la Unidad 3

El mismo problema con los modelos clásicos: el mejor modelo de **una** variable (Ni en función de MgO, como en la
Unidad 3) y una regresión lineal múltiple con los 8 óxidos. Se evalúan con los mismos datos de prueba."""),
    code('''from sklearn.linear_model import LinearRegression
i_mgo = ENTRADAS.index("MgO (wt%)")
una = LinearRegression().fit(X_ent[:, [i_mgo]], y_ent)          # log Ni = a + b·MgO (modelo exponencial)
multiple = LinearRegression().fit(X_ent, y_ent)                # regresión lineal múltiple
comparacion = pd.DataFrame({
    "modelo": ["Exponencial: Ni ~ MgO (Unidad 3)", "Lineal múltiple: 8 óxidos", "Red neuronal: 8 óxidos"],
    "R2": [r2_score(y_prueba, una.predict(X_prueba[:, [i_mgo]])), r2_score(y_prueba, multiple.predict(X_prueba)), r2]})
print(comparacion.round(3).to_string(index=False))
plt.figure(figsize=(7, 3.5))
plt.barh(comparacion["modelo"], comparacion["R2"], color=["gray", "#86b6ef", "#d95926"])
plt.xlim(0, 1); plt.xlabel("R² en los datos de prueba")
plt.title("Gráfica N° 4: La red frente a la regresión clásica")
guardar("reg_comparacion"); plt.show()'''),
    md("## 7. Predicción interactiva"),
    code('''import ipywidgets as widgets
from IPython.display import display
valores_basalto = [50.0, 15.0, 8.0, 11.0, 2.5, 0.3, 0.2, 0.17]          # un basalto típico de dorsal
casillas = [widgets.FloatText(value=v, description=n.split(" ")[0], layout=widgets.Layout(width="200px"))
            for n, v in zip(ENTRADAS, valores_basalto)]
boton = widgets.Button(description="Estimar Ni", button_style="warning")
salida = widgets.Output()
def estimar(_):
    with salida:
        salida.clear_output()
        x = escala.transform([[c.value for c in casillas]])
        print(f"Ni estimado: {10 ** red.predict(x, verbose=0)[0, 0]:.0f} ppm")
boton.on_click(estimar)
display(widgets.VBox(casillas + [boton, salida]))
estimar(None)'''),
    code('''# Ejemplos sin widgets: un basalto y una peridotita
ejemplos = pd.DataFrame([valores_basalto, [44.0, 2.0, 42.0, 1.5, 0.1, 0.02, 0.01, 0.12]], columns=ENTRADAS,
                        index=["basalto", "peridotita"])
ejemplos["Ni estimado (ppm)"] = 10 ** red.predict(escala.transform(ejemplos[ENTRADAS].values), verbose=0).ravel()
print(ejemplos.round(1).to_string())
if WEB:
    json.dump({"regresion": {"n": int(len(datos)), "r2": round(float(r2), 3), "rmse_log": round(float(rmse), 3),
                             "mae_log": round(float(mae), 3), "hiperparametros": {k: (round(v, 5) if isinstance(v, float) else v) for k, v in p.items()},
                             "comparacion": comparacion.round(3).to_dict("records"),
                             "ejemplos": ejemplos["Ni estimado (ppm)"].round(0).to_dict()}},
              open("../docs/data/ml_regresion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)'''),
    md("""## 8. Conclusión

La red neuronal estima el **log10 del níquel** a partir de los ocho óxidos mayores con un R² cercano a 0,8 en datos que
nunca vio, bastante más que el mejor modelo de una sola variable de la Unidad 3 y que la regresión lineal múltiple. La
diferencia viene de que la red combina los óxidos de forma no lineal: el Ni depende sobre todo del olivino (MgO), pero el
SiO₂, el CaO y el Al₂O₃ ayudan a separar peridotitas, basaltos y rocas evolucionadas. Límites: solo vale para rocas
parecidas a las de PetDB (sobre todo oceánicas) y su error típico es de un factor cercano a 1,5–2 en ppm."""),
]

CLASIFICACION = [
    None,
    md("""## 0. Clasificación con una red neuronal

En la clasificación la salida no es un número sino una **categoría**. La última capa tiene una neurona por clase y la
función **softmax** convierte sus salidas en probabilidades que suman 1; la red elige la más probable. Es la extensión de
la regresión logística (una neurona con activación sigmoide) a varias clases.

**Problema:** los geólogos usan diagramas de discriminación para saber en qué ambiente tectónico se formó una roca
volcánica antigua cuyo contexto se perdió. ¿Puede una red reconocer el ambiente (**dorsal**, **intraplaca** o **margen
convergente**) solo con los óxidos mayores?"""),
    md("## 1. Librerías y carga de datos"),
    code(COMUN_INICIO),
    md("""## 2. Preprocesamiento

- Rocas **volcánicas** con los 8 óxidos mayores completos; sin la clase «mixto» (ambiente ambiguo).
- **Codificación**: cada clase se convierte en un número (0, 1, 2).
- **Balance de clases**: las tres clases no tienen el mismo tamaño; se da más peso a las menos frecuentes para que la red
  no aprenda solo la mayoritaria.
- División 70 / 15 / 15 estratificada (cada parte con las mismas proporciones de clase) y normalización."""),
    code(f'''ENTRADAS = {OXIDOS}
volcanicas = base["Sample Type"].astype(str).str.startswith("igneous:volcanic")
datos = base.loc[volcanicas, ENTRADAS + ["Tectonic Group"]].dropna()
datos = datos[datos["Tectonic Group"] != "mixto"]
CLASES = sorted(datos["Tectonic Group"].unique())
y = datos["Tectonic Group"].map({{c: i for i, c in enumerate(CLASES)}}).values
X = datos[ENTRADAS].values
print(datos["Tectonic Group"].value_counts())

X_ent, X_resto, y_ent, y_resto = train_test_split(X, y, test_size=0.30, random_state=2026, stratify=y)
X_val, X_prueba, y_val, y_prueba = train_test_split(X_resto, y_resto, test_size=0.50, random_state=2026, stratify=y_resto)
escala = StandardScaler().fit(X_ent)
X_ent, X_val, X_prueba = escala.transform(X_ent), escala.transform(X_val), escala.transform(X_prueba)
pesos = {{i: len(y_ent) / (len(CLASES) * np.sum(y_ent == i)) for i in range(len(CLASES))}}   # balance de clases
print("pesos por clase:", {{CLASES[i]: round(w, 2) for i, w in pesos.items()}})'''),
    md("""## 3. Arquitectura de la red

Tres capas ocultas (128, 64 y 32 neuronas, ReLU) con *dropout* y una salida softmax de 3 neuronas. Antes de fijarla se
probaron otras con Optuna; esta es la mejor de las probadas, con un buen equilibrio entre exactitud y tiempo."""),
    code('''%pip install -q optuna
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

def crear_red(neuronas, tasa, abandono):
    red = keras.Sequential([layers.Input(shape=(X_ent.shape[1],)),
                            layers.Dense(neuronas, activation="relu"), layers.Dropout(abandono),
                            layers.Dense(neuronas // 2, activation="relu"), layers.Dropout(abandono),
                            layers.Dense(neuronas // 4, activation="relu"),
                            layers.Dense(len(CLASES), activation="softmax")])
    red.compile(optimizer=keras.optimizers.Adam(tasa), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return red

def objetivo(prueba):
    red = crear_red(prueba.suggest_categorical("neuronas", [64, 128, 256]),
                    prueba.suggest_float("tasa_aprendizaje", 1e-4, 1e-2, log=True),
                    prueba.suggest_float("abandono", 0.0, 0.3))
    h = red.fit(X_ent, y_ent, validation_data=(X_val, y_val), epochs=30, batch_size=256, verbose=0, class_weight=pesos,
                callbacks=[keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)])
    return max(h.history["val_accuracy"])

estudio = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=2026))
estudio.optimize(objetivo, n_trials=15)
p = estudio.best_params
print("mejores hiperparámetros:", p, " exactitud de validación:", round(estudio.best_value, 3))
red = crear_red(p["neuronas"], p["tasa_aprendizaje"], p["abandono"])
red.summary()'''),
    md("## 4. Entrenamiento"),
    code('''historia = red.fit(X_ent, y_ent, validation_data=(X_val, y_val), epochs=150, batch_size=256, verbose=0,
                   class_weight=pesos, callbacks=[keras.callbacks.EarlyStopping(patience=12, restore_best_weights=True)])
print("épocas entrenadas:", len(historia.history["loss"]))
fig, ejes = plt.subplots(1, 2, figsize=(11, 4))
ejes[0].plot(historia.history["loss"], color="#3987e5", lw=2, label="entrenamiento")
ejes[0].plot(historia.history["val_loss"], color="#d95926", lw=2, label="validación")
ejes[0].set_xlabel("Época"); ejes[0].set_ylabel("Pérdida (entropía cruzada)"); ejes[0].legend()
ejes[1].plot(historia.history["accuracy"], color="#3987e5", lw=2, label="entrenamiento")
ejes[1].plot(historia.history["val_accuracy"], color="#d95926", lw=2, label="validación")
ejes[1].set_xlabel("Época"); ejes[1].set_ylabel("Exactitud"); ejes[1].legend()
fig.suptitle("Gráfica N° 1: Curvas de aprendizaje")
guardar("clas_curvas"); plt.show()'''),
    md("## 5. Evaluación con los datos de prueba"),
    code('''from sklearn.metrics import accuracy_score, cohen_kappa_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
pred = red.predict(X_prueba, verbose=0).argmax(axis=1)
exactitud = accuracy_score(y_prueba, pred)
kappa = cohen_kappa_score(y_prueba, pred)          # acuerdo descontando el azar: > 0,6 es bueno, > 0,8 muy bueno
print(f"Exactitud = {exactitud:.3f}   Kappa de Cohen = {kappa:.3f}\\n")
print(classification_report(y_prueba, pred, target_names=CLASES, digits=3))
fig, eje = plt.subplots(figsize=(6.5, 5.5))
ConfusionMatrixDisplay(confusion_matrix(y_prueba, pred, normalize="true"), display_labels=["dorsal", "intraplaca", "convergente"]).plot(
    ax=eje, cmap="Blues", values_format=".2f", colorbar=False)
eje.set_title("Gráfica N° 2: Matriz de confusión (proporción por clase real)")
eje.set_xlabel("Clase estimada por la red"); eje.set_ylabel("Clase real")
guardar("clas_confusion"); plt.show()'''),
    md("""**Cómo leer la matriz:** cada fila es la clase real y suma 1; la diagonal es la proporción bien clasificada. Lo que
queda fuera de la diagonal muestra qué ambientes se confunden entre sí."""),
    md("""## 6. Comparación con la regresión logística

La regresión logística multiclase (de la plantilla del curso) es una red sin capas ocultas: una sola capa de neuronas con
softmax. Se compara con los mismos datos de prueba."""),
    code('''from sklearn.linear_model import LogisticRegression
logistica = LogisticRegression(max_iter=2000, class_weight="balanced").fit(X_ent, y_ent)
p_log = logistica.predict(X_prueba)
comparacion = pd.DataFrame({"modelo": ["Regresión logística", "Red neuronal"],
                            "exactitud": [accuracy_score(y_prueba, p_log), exactitud],
                            "kappa": [cohen_kappa_score(y_prueba, p_log), kappa]})
print(comparacion.round(3).to_string(index=False))
comparacion.set_index("modelo").plot.barh(figsize=(7, 3), color=["#86b6ef", "#d95926"], xlim=(0, 1))
plt.title("Gráfica N° 3: Red neuronal frente a regresión logística"); plt.xlabel("Valor en los datos de prueba")
guardar("clas_comparacion"); plt.show()'''),
    md("## 7. Predicción interactiva"),
    code('''import ipywidgets as widgets
from IPython.display import display
valores = [50.0, 15.0, 8.0, 11.0, 2.5, 0.3, 0.2, 0.17]
casillas = [widgets.FloatText(value=v, description=n.split(" ")[0], layout=widgets.Layout(width="200px"))
            for n, v in zip(ENTRADAS, valores)]
boton = widgets.Button(description="Clasificar", button_style="warning")
salida = widgets.Output()
def clasificar(_):
    with salida:
        salida.clear_output()
        prob = red.predict(escala.transform([[c.value for c in casillas]]), verbose=0)[0]
        for c, pr in sorted(zip(CLASES, prob), key=lambda t: -t[1]):
            print(f"{c:28s} {pr * 100:5.1f} %")
boton.on_click(clasificar)
display(widgets.VBox(casillas + [boton, salida]))
clasificar(None)'''),
    code('''# Ejemplos sin widgets: un basalto de dorsal, un basalto de isla oceánica y una andesita de arco
ejemplos = pd.DataFrame([[50.0, 15.0, 8.0, 11.0, 2.5, 0.15, 0.12, 0.17],
                         [47.0, 13.5, 8.5, 10.5, 2.8, 1.1, 0.5, 0.18],
                         [59.0, 17.0, 3.0, 6.5, 3.5, 1.5, 0.2, 0.12]], columns=ENTRADAS,
                        index=["basalto de dorsal (MORB)", "basalto de isla oceánica", "andesita de arco"])
prob = red.predict(escala.transform(ejemplos[ENTRADAS].values), verbose=0)
for nombre, pr in zip(ejemplos.index, prob):
    print(f"{nombre:28s} -> {CLASES[pr.argmax()]} ({pr.max() * 100:.0f} %)")
if WEB:
    reporte = classification_report(y_prueba, pred, target_names=CLASES, output_dict=True)
    json.dump({"clasificacion": {"n": int(len(datos)), "exactitud": round(float(exactitud), 3), "kappa": round(float(kappa), 3),
                                 "hiperparametros": {k: (round(v, 5) if isinstance(v, float) else v) for k, v in p.items()},
                                 "por_clase": {c: round(reporte[c]["f1-score"], 3) for c in CLASES},
                                 "comparacion": comparacion.round(3).to_dict("records"),
                                 "ejemplos": {n: CLASES[pr.argmax()] for n, pr in zip(ejemplos.index, prob)}}},
              open("../docs/data/ml_clasificacion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)'''),
    md("""## 8. Conclusión

Con solo los ocho óxidos mayores, la red reconoce el ambiente tectónico de una roca volcánica en más de 8 de cada 10
casos que nunca vio, con un kappa que indica un acuerdo bueno, por encima de la regresión logística. Los márgenes
convergentes se distinguen mejor (más K₂O y Al₂O₃, menos MgO); dorsal e intraplaca se confunden más porque los dos son
basaltos de manto. Límite: la base tiene más rocas oceánicas que continentales, así que la red refleja ese sesgo."""),
]


def escribir(nombre, titulo, problema, celdas):
    nb = nbf.v4.new_notebook()
    nb.cells = [cabecera(titulo, problema)] + celdas[1:]
    nb.cells[0].source = nb.cells[0].source.replace("{archivo}", nombre)
    nb.metadata = {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                   "language_info": {"name": "python"}, "colab": {"provenance": []}}
    ruta = CARPETA / nombre
    nbf.write(nb, ruta)
    return ruta


def main():
    CARPETA.mkdir(exist_ok=True)
    rutas = [
        escribir("01_regresion_niquel.ipynb", "Red neuronal de regresión: níquel a partir de los óxidos mayores",
                 "Estimar la concentración de **níquel (ppm)**, un metal crítico, con los 8 óxidos mayores de la roca.", REGRESION),
        escribir("02_clasificacion_ambiente.ipynb", "Red neuronal de clasificación: ambiente tectónico de rocas volcánicas",
                 "Reconocer el **ambiente tectónico** (dorsal, intraplaca o margen convergente) de una roca volcánica con sus 8 óxidos mayores.",
                 CLASIFICACION),
    ]
    solo = sys.argv[1:]
    for ruta in rutas:
        if solo and ruta.stem not in solo:
            continue
        subprocess.run([sys.executable, "-m", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                        "--ExecutePreprocessor.timeout=3600", str(ruta)], cwd=CARPETA, check=True)
        print("ejecutado:", ruta.name)


if __name__ == "__main__":
    main()
