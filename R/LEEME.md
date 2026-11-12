# Código R del proyecto: qué abrir

Abrir RStudio en la carpeta del repositorio (Session → Set Working Directory) y ejecutar con Ctrl + Enter.
Una vez: `install.packages(c("e1071", "openxlsx"))`.

## Para estudiar y exponer (código simple, paso a paso, sin funciones propias)

| Archivo | Qué hace |
|---|---|
| `graficos/01…15_*.R` | Un archivo por gráfico de la página, en el mismo orden. Lee la base, arma la tabla de frecuencias, dibuja el gráfico y calcula los indicadores. Es el mismo código del botón «Código R» de la web. |
| `04_muestreo.R` | Muestreo aleatorio simple, sistemático y estratificado (Lección 3) y sus dos gráficos. |
| `rpubs/NN_*.Rmd` | Un documento R Markdown por variable (como el proyecto modelo en RPubs): código + resultado + conclusión. Abrir en RStudio, **Knit**, y **Publish → RPubs**. Instalar una vez `install.packages(c("rmarkdown", "knitr"))`. |
| `05_paso_a_paso.R` | SiO2 y ambiente tectónico explicados línea por línea, con el estilo de la plantilla del docente. |

## Para regenerar toda la web de una vez (versión automática)

`funciones.R` + `01_cualitativas.R`, `02_discretas.R`, `03_continuas.R` hacen los mismos cálculos para todas las
variables en un bucle y además escriben las tablas de la web (`docs/data/tdf/`) y los Excel (`R/salidas/`).
Usan funciones para no repetir el mismo código 15 veces. No hace falta abrirlos para entender el proyecto: cada
gráfico de `graficos/` produce exactamente la misma imagen.
