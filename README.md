# Proyecto de Optimización de Rutas — Vecino Más Cercano + 2-opt

Proyecto académico de **Modelamiento y Optimización**. Resuelve, mediante una
estrategia heurística híbrida, el problema de un comprador que necesita
visitar varias viviendas ubicadas en un mismo suburbio de **Perth, Australia**,
minimizando la distancia total recorrida (TSP).

---

## 1. Estructura del proyecto

```text
proyecto_optimizacion/
│
├── data/
│   └── perth_houses.csv          <- Dataset real (33.656 registros originales)
│
├── results/                      <- Se genera automáticamente al ejecutar
│   ├── ruta_inicial.csv
│   ├── ruta_optimizada.csv
│   ├── comparacion_resultados.csv
│   ├── resumen_resultados.txt
│   ├── ruta_inicial.png
│   ├── ruta_optimizada.png
│   └── comparacion_rutas.png
│
├── src/
│   ├── data_loader.py            <- Carga y limpieza de datos, selección de suburbio/viviendas
│   ├── distances.py              <- Cálculo de distancias geodésicas (geopy) y matriz de costos
│   ├── nearest_neighbor.py       <- Algoritmo Vecino Más Cercano + validación de rutas
│   ├── two_opt.py                <- Algoritmo de mejora local 2-opt
│   ├── visualization.py          <- Gráficos de las rutas (matplotlib)
│   └── main.py                   <- Script principal: orquesta todo el flujo
│
├── requirements.txt
└── README.md
```

---

## 2. Instalación

Requisitos: **Python 3.11** (probado también en 3.9+).

1. Clona o descomprime el proyecto y ubícate en la carpeta raíz:

   ```bash
   cd proyecto_optimizacion
   ```

2. (Recomendado) crea un entorno virtual:

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS / Linux:
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

---

## 3. Ejecución

Desde la carpeta raíz del proyecto:

```bash
python src/main.py
```

El programa imprimirá en consola, en orden:

1. Información de carga del dataset.
2. Resultados de la limpieza de datos.
3. Lista de suburbios disponibles con su cantidad de viviendas válidas.
4. Confirmación del suburbio y del número de viviendas seleccionadas.
5. Datos de la vivienda inicial.
6. (Opcional) matriz de distancias, si el conjunto es pequeño.
7. Ruta y distancia obtenidas por Vecino Más Cercano.
8. Progreso e iteraciones de 2-opt.
9. Resultados de las 5 validaciones automáticas.
10. Tabla comparativa de distancias y porcentaje de mejora.
11. Tablas detalladas de ambas rutas (orden, dirección, coordenadas, distancia al siguiente punto).
12. Confirmación de los gráficos y archivos generados en `results/`.

### Variables configurables (editar en `src/main.py`)

```python
DATASET_PATH   = "../data/perth_houses.csv"  # Ruta al CSV (ya resuelta automáticamente)
SELECTED_SUBURB = "Bertram"                   # Nombre exacto de un suburbio del dataset
NUM_HOUSES      = 20                          # Cantidad de viviendas a usar (2 a N disponibles)
START_INDEX     = 0                           # Índice de la vivienda inicial dentro del subconjunto
VERBOSE         = True                        # Mostrar matriz de distancias e iteraciones de 2-opt
```

Si `SELECTED_SUBURB = None`, el programa mostrará la lista de suburbios
disponibles y se detendrá para que el usuario elija uno y vuelva a ejecutar.

> **Nota sobre el dataset real:** se verificó que `all_perth_310121.csv`
> contiene las 33.656 filas y las columnas `ADDRESS`, `SUBURB`, `LATITUDE`
> y `LONGITUDE` sin valores nulos, por lo que el programa puede ejecutarse
> directamente sin adaptaciones adicionales. El suburbio con más viviendas
> válidas es **Bertram (231 viviendas)**, usado como valor por defecto en
> `SELECTED_SUBURB`.

---

## 4. Formato esperado del CSV

El archivo debe ser un CSV delimitado por comas, con al menos estas columnas
(pueden existir columnas adicionales, que simplemente se ignoran):

```text
ADDRESS,SUBURB,PRICE,BEDROOMS,BATHROOMS,GARAGE,LAND_AREA,FLOOR_AREA,BUILD_YEAR,CBD_DIST,NEAREST_STN,NEAREST_STN_DIST,DATE_SOLD,POSTCODE,LATITUDE,LONGITUDE,NEAREST_SCH,NEAREST_SCH_DIST,NEAREST_SCH_RANK
1 Example St,Bertram,350000,4,2,2,400,180,2015,35000,Kwinana,3200,12-2018,6167,-32.276,115.827,Bertram Primary School,0.8,120
```

Si el archivo no contiene `ADDRESS`, `SUBURB`, `LATITUDE` o `LONGITUDE`, el
programa se detiene mostrando exactamente qué columna falta, sin inventar
valores ni continuar con datos incompletos.

---

## 5. Ejemplo del formato de resultados

Los valores numéricos exactos dependen del suburbio, del número de viviendas
y de la vivienda inicial elegidos; el formato mostrado a continuación es
representativo:

```text
RESULTADOS
============================================================
Método                          Distancia (km)
------------------------------------------------------------
Vecino Más Cercano                        XX.XXXX
Vecino Más Cercano + 2-opt                XX.XXXX
------------------------------------------------------------
Reducción de distancia:            X.XXXX km
Porcentaje de mejora:              X.XX %
============================================================
```

---

## 6. Explicación de cada etapa del algoritmo

1. **Carga y limpieza de datos**: se valida la existencia de las columnas
   necesarias, se eliminan registros incompletos o con coordenadas inválidas
   y se reporta cuántos registros se eliminaron.
2. **Selección de suburbio y viviendas**: se filtra el dataset a un único
   suburbio (para que el escenario sea geográficamente coherente) y se toma
   un subconjunto de tamaño configurable.
3. **Cálculo de distancias**: se construye una matriz N×N de distancias
   geodésicas reales (en kilómetros) entre cada par de viviendas, usando
   `geopy.distance.geodesic`.
4. **Vecino Más Cercano**: construye una ruta inicial completa, moviéndose
   siempre hacia la vivienda no visitada más cercana.
5. **2-opt**: toma la ruta anterior y prueba intercambios de segmentos que
   reduzcan la distancia total, repitiendo hasta que no haya más mejoras.
6. **Comparación y validación**: se calculan la reducción absoluta y el
   porcentaje de mejora, y se verifica formalmente que ambas rutas sean
   ciclos válidos.
7. **Visualización y exportación**: se generan gráficos 2D (longitud vs.
   latitud) y archivos CSV/TXT con todos los resultados obtenidos.

---

## 7. Explicación académica

### 7.1 Representación del TSP en este proyecto

El problema se modela como un **Problema del Agente Viajero (TSP)** sobre un
grafo completo no dirigido:

- **Nodos**: cada nodo representa una vivienda seleccionada del suburbio
  (identificada por su índice 0..N-1 dentro del subconjunto, y asociada a su
  `ADDRESS`, `LATITUDE` y `LONGITUDE`).
- **Aristas**: existe una arista entre cada par de viviendas i, j; representa
  el desplazamiento directo entre ambas.
- **Costo**: el costo asociado a cada arista es la distancia geodésica real
  (en kilómetros) entre las coordenadas de las dos viviendas, calculada con
  `geopy.distance.geodesic`.
- **Función objetivo**: minimizar la distancia total del recorrido que visita
  todas las viviendas seleccionadas exactamente una vez y regresa al punto de
  partida:

  ```text
  Minimizar   Z = Σᵢ Σⱼ dᵢⱼ · xᵢⱼ
  ```

  sujeta a que cada vivienda tenga exactamente una arista de entrada y una de
  salida (`Σⱼ xᵢⱼ = 1` para cada i, `Σᵢ xᵢⱼ = 1` para cada j), con
  `xᵢⱼ ∈ {0,1}` indicando si la ruta va directamente de i a j, además de las
  restricciones de eliminación de subtours propias de la formulación clásica
  del TSP.

### 7.2 Funcionamiento de Vecino Más Cercano

Es un algoritmo constructivo y goloso (*greedy*): parte de una vivienda
inicial y, en cada paso, se desplaza hacia la vivienda no visitada más
cercana a la posición actual. Repite este proceso hasta visitar todas las
viviendas y finalmente regresa al punto de partida. Su complejidad es
O(N²), por lo que construye una solución inicial muy rápidamente, aunque
sin ninguna garantía de optimalidad: decisiones "buenas" a corto plazo
pueden dejar viviendas aisladas que obligan a recorridos largos al final.

### 7.3 Funcionamiento de 2-opt

Es un algoritmo de **búsqueda local**: examina pares de aristas de la ruta
actual y evalúa si invertir el segmento entre ellas reduce la distancia
total. Si la reducción existe, el cambio se conserva; si no, se descarta.
El proceso se repite sobre toda la ruta hasta que ninguna inversión produce
mejora (óptimo local respecto a este tipo de movimiento). Este mecanismo es
particularmente eficaz para eliminar cruces entre segmentos de la ruta, que
son comunes en las soluciones de Vecino Más Cercano.

### 7.4 Por qué Vecino Más Cercano + 2-opt es una alternativa adecuada

Combina lo mejor de dos enfoques complementarios: una construcción muy
rápida (Vecino Más Cercano) con un refinamiento posterior (2-opt) que
corrige buena parte de las ineficiencias de esa construcción inicial. Es
una alternativa apropiada cuando se busca una solución de buena calidad en
un tiempo razonable, sin incurrir en el costo computacional de una
enumeración exhaustiva o de un modelo exacto, que crece de forma factorial
con el número de viviendas.

### 7.5 Limitaciones del método

- No garantiza encontrar el óptimo global: ambos algoritmos son heurísticos.
- El resultado de Vecino Más Cercano depende del nodo inicial elegido.
- 2-opt solo garantiza un óptimo *local* respecto a intercambios de dos
  aristas; existen movimientos más complejos (3-opt, Lin-Kernighan) que
  podrían mejorar aún más la solución.
- La complejidad de 2-opt es O(N²) por iteración, lo que puede volverse
  costoso para conjuntos muy grandes de viviendas.

### 7.6 Comparación futura contra una solución exacta con Pyomo

El mismo problema podría formularse como un modelo de programación lineal
entera (variables binarias `xᵢⱼ`, función objetivo de minimización de
distancia y restricciones de grado de entrada/salida más eliminación de
subtours) y resolverse con **Pyomo** junto a un solver exacto (por ejemplo,
CBC o Gurobi). Esto permitiría obtener el óptimo global para conjuntos
pequeños de viviendas y así cuantificar, mediante el porcentaje de mejora
respecto al óptimo, qué tan cerca queda la solución heurística
Vecino Más Cercano + 2-opt de la solución exacta.

---

## 8. Referencias

- Croes, G. A. (1958). *A method for solving traveling-salesman problems*.
  Operations Research, 6(6), 791–812.
- Hillier, F. S., Lieberman, G. J., & Osuna, M. A. G. (1998).
  *Introducción a la investigación de operaciones*. McGraw-Hill.
- Taha, H. A. (2004). *Investigación de operaciones*. Pearson Education.
- Bynum, M. L. et al. (2021). *Pyomo—Optimization modeling in Python* (3rd ed.). Springer.
