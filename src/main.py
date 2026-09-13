# -*- coding: utf-8 -*-
"""
main.py
--------
PROYECTO DE OPTIMIZACIÓN DE RUTAS - Modelamiento y Optimización
Estrategia: Vecino Más Cercano + 2-opt aplicada al problema del
comprador que necesita visitar varias viviendas en un mismo suburbio
de Perth, Australia.

Este script es el punto de entrada del programa. Orquesta las
siguientes etapas:
    1. Carga del dataset.
    2. Limpieza de datos.
    3. Selección de suburbio y de un subconjunto de viviendas.
    4. Selección de la vivienda inicial.
    5. Cálculo de la matriz de distancias (geopy).
    6. Ejecución de Vecino Más Cercano (solución inicial).
    7. Ejecución de 2-opt (mejora local).
    8. Comparación de resultados y validaciones.
    9. Generación de tablas, gráficos y archivos de salida en `results/`.

Ejecución:
    Desde la carpeta raíz del proyecto (proyecto_optimizacion/):
        python src/main.py
"""

import os
import sys
from datetime import datetime

import pandas as pd

# Permite ejecutar el script tanto desde la raíz del proyecto como desde
# dentro de la carpeta src/, resolviendo las importaciones relativas.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import (
    load_dataset,
    clean_dataset,
    show_available_suburbs,
    select_suburb_data,
    select_houses_subset,
)
from distances import build_distance_matrix, print_distance_matrix
from nearest_neighbor import nearest_neighbor, validate_route
from two_opt import two_opt
from visualization import plot_route, plot_comparison


# =============================================================================
# CONFIGURACIÓN DEL PROGRAMA
# Estas son las variables que el usuario puede modificar para cada ejecución.
# =============================================================================

# Ruta al archivo CSV con los datos inmobiliarios de Perth.
DATASET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "perth_houses.csv"
)

# Suburbio a utilizar. Si se deja en None, el programa mostrará los
# suburbios disponibles y se detendrá para que el usuario elija uno
# editando esta variable.
SELECTED_SUBURB = "Bertram"

# Cantidad de viviendas a utilizar dentro del suburbio seleccionado.
# Recomendado entre 10 y 30 para una primera validación del algoritmo.
NUM_HOUSES = 20

# Índice (dentro del subconjunto seleccionado, 0-based) de la vivienda
# desde la que se inicia el recorrido.
START_INDEX = 0

# Si es True, se muestra la matriz de distancias y el progreso de 2-opt
# en la consola (recomendado desactivar para conjuntos grandes).
VERBOSE = True

# Carpeta donde se guardarán los resultados (CSV, TXT y gráficos).
RESULTS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "results"
)


# =============================================================================
# FUNCIONES DE APOYO PARA REPORTES Y EXPORTACIÓN
# =============================================================================

def print_route_table(df_houses: pd.DataFrame, route: list, distance_matrix, title: str):
    """
    Imprime en consola una tabla detallada del recorrido: orden, índice,
    dirección, suburbio, coordenadas y distancia hacia el siguiente punto.
    """
    print(f"\n{title}")
    print("-" * 100)
    print(f"{'Orden':>5} {'Índice':>7} {'ADDRESS':<35} {'SUBURB':<15} "
          f"{'LATITUDE':>10} {'LONGITUDE':>11} {'Dist. sig. (km)':>16}")
    print("-" * 100)

    for order, idx in enumerate(route):
        row = df_houses.iloc[idx]
        if order < len(route) - 1:
            next_idx = route[order + 1]
            dist_to_next = distance_matrix[idx, next_idx]
            dist_str = f"{dist_to_next:16.4f}"
        else:
            dist_str = f"{'--':>16}"

        address = str(row["ADDRESS"])[:34]
        print(f"{order:>5} {idx:>7} {address:<35} {str(row['SUBURB']):<15} "
              f"{row['LATITUDE']:>10.6f} {row['LONGITUDE']:>11.6f} {dist_str}")
    print("-" * 100 + "\n")


def build_route_dataframe(df_houses: pd.DataFrame, route: list) -> pd.DataFrame:
    """
    Construye un DataFrame exportable con el detalle de una ruta:
    orden, índice, dirección, suburbio, latitud y longitud.
    """
    records = []
    for order, idx in enumerate(route):
        row = df_houses.iloc[idx]
        records.append({
            "orden": order,
            "indice": idx,
            "address": row["ADDRESS"],
            "suburb": row["SUBURB"],
            "latitude": row["LATITUDE"],
            "longitude": row["LONGITUDE"],
        })
    return pd.DataFrame(records)


def run_validations(initial_route, optimized_route, n, initial_distance,
                     optimized_distance, distance_matrix, df_houses):
    """
    Ejecuta las 5 validaciones exigidas por el proyecto y muestra el
    resultado de cada una en consola.
    """
    print("=" * 60)
    print("VALIDACIONES")
    print("=" * 60)

    # Validación 1 y 2: rutas visitan cada vivienda exactamente una vez y
    # cierran en el punto de partida. Se reutiliza validate_route, que ya
    # lanza una excepción clara si algo falla.
    validate_route(initial_route, n)
    print("Validación 1 y 2 (ruta inicial): OK - visita cada vivienda una "
          "vez y cierra en el punto de partida.")

    validate_route(optimized_route, n)
    print("Validación 1 y 2 (ruta optimizada): OK - visita cada vivienda "
          "una vez y cierra en el punto de partida.")

    # Validación 3: la distancia optimizada no debe ser mayor que la inicial.
    if optimized_distance > initial_distance:
        print("ADVERTENCIA: La solución 2-opt no produjo una mejora.")
    else:
        print(f"Validación 3: OK - la distancia optimizada "
              f"({optimized_distance:.4f} km) no es mayor que la inicial "
              f"({initial_distance:.4f} km).")

    # Validación 4: no deben existir NaN en las coordenadas utilizadas.
    coords_have_nan = df_houses[["LATITUDE", "LONGITUDE"]].isna().any().any()
    if coords_have_nan:
        raise ValueError("ERROR: existen valores NaN en las coordenadas utilizadas.")
    print("Validación 4: OK - no existen valores NaN en las coordenadas utilizadas.")

    # Validación 5: todas las distancias deben ser >= 0.
    if (distance_matrix < 0).any():
        raise ValueError("ERROR: existen distancias negativas en la matriz de costos.")
    print("Validación 5: OK - todas las distancias son mayores o iguales a cero.")

    print("=" * 60 + "\n")


def export_results(df_houses, suburb, num_available, num_used, start_index,
                    initial_route, initial_distance,
                    optimized_route, optimized_distance,
                    results_dir):
    """
    Genera todos los archivos de salida exigidos por el proyecto dentro
    de la carpeta `results/`: ruta_inicial.csv, ruta_optimizada.csv,
    comparacion_resultados.csv y resumen_resultados.txt.
    """
    os.makedirs(results_dir, exist_ok=True)

    # --- ruta_inicial.csv ---
    df_initial = build_route_dataframe(df_houses, initial_route)
    path_initial = os.path.join(results_dir, "ruta_inicial.csv")
    df_initial.to_csv(path_initial, index=False)

    # --- ruta_optimizada.csv ---
    df_optimized = build_route_dataframe(df_houses, optimized_route)
    path_optimized = os.path.join(results_dir, "ruta_optimizada.csv")
    df_optimized.to_csv(path_optimized, index=False)

    # --- comparacion_resultados.csv ---
    df_comparison = pd.DataFrame({
        "metodo": ["Vecino Más Cercano", "Vecino Más Cercano + 2-opt"],
        "distancia_km": [initial_distance, optimized_distance],
    })
    path_comparison = os.path.join(results_dir, "comparacion_resultados.csv")
    df_comparison.to_csv(path_comparison, index=False)

    # --- resumen_resultados.txt ---
    reduction = initial_distance - optimized_distance
    improvement_pct = (reduction / initial_distance) * 100 if initial_distance > 0 else 0.0
    start_address = df_houses.iloc[start_index]["ADDRESS"]

    summary_text = f"""PROYECTO DE OPTIMIZACIÓN DE RUTAS
====================================

Dataset:
{DATASET_PATH}

Suburbio:
{suburb}

Viviendas disponibles:
{num_available}

Viviendas utilizadas:
{num_used}

Método inicial:
Vecino Más Cercano

Distancia inicial:
{initial_distance:.4f} km

Método de optimización:
2-opt

Distancia optimizada:
{optimized_distance:.4f} km

Reducción:
{reduction:.4f} km

Porcentaje de mejora:
{improvement_pct:.2f} %

Vivienda inicial:
{start_address}

Fecha/hora de ejecución:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    path_summary = os.path.join(results_dir, "resumen_resultados.txt")
    with open(path_summary, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print("Archivos de resultados generados en:", results_dir)
    print(f"  - {os.path.basename(path_initial)}")
    print(f"  - {os.path.basename(path_optimized)}")
    print(f"  - {os.path.basename(path_comparison)}")
    print(f"  - {os.path.basename(path_summary)}")
    print()


# =============================================================================
# FLUJO PRINCIPAL DEL PROGRAMA
# =============================================================================

def main():
    # ---- 1. Carga del dataset ----
    df_raw = load_dataset(DATASET_PATH)

    # ---- 2. Limpieza de datos ----
    df_clean = clean_dataset(df_raw)

    # ---- 3. Selección del suburbio ----
    suburb_counts = show_available_suburbs(df_clean)

    if SELECTED_SUBURB is None:
        print("SELECTED_SUBURB está en None. Edita esta variable en main.py "
              "con uno de los suburbios listados arriba y vuelve a ejecutar "
              "el programa.")
        return

    df_suburb = select_suburb_data(df_clean, SELECTED_SUBURB)
    num_available = len(df_suburb)

    # ---- 4. Selección del número de viviendas ----
    df_houses = select_houses_subset(df_suburb, NUM_HOUSES)
    num_used = len(df_houses)

    print("=" * 60)
    print("SELECCIÓN DE VIVIENDAS")
    print("=" * 60)
    print(f"Suburbio seleccionado: {SELECTED_SUBURB}")
    print(f"Viviendas disponibles: {num_available}")
    print(f"Viviendas utilizadas: {num_used}")
    print("=" * 60 + "\n")

    # ---- 5. Selección de la vivienda inicial ----
    if not (0 <= START_INDEX < num_used):
        raise ValueError(
            f"ERROR: START_INDEX={START_INDEX} está fuera de rango para "
            f"{num_used} viviendas seleccionadas."
        )

    start_row = df_houses.iloc[START_INDEX]
    print("Vivienda inicial:")
    print(f"ADDRESS: {start_row['ADDRESS']}")
    print(f"LATITUDE: {start_row['LATITUDE']}")
    print(f"LONGITUDE: {start_row['LONGITUDE']}\n")

    # ---- 6. Cálculo de la matriz de distancias ----
    print("Calculando matriz de distancias con geopy (esto puede tardar unos "
          "segundos)...\n")
    distance_matrix = build_distance_matrix(df_houses)

    if VERBOSE:
        print_distance_matrix(distance_matrix)

    # ---- 7. Vecino Más Cercano ----
    initial_route, initial_distance = nearest_neighbor(distance_matrix, START_INDEX)
    validate_route(initial_route, num_used)

    print(f"Ruta inicial (Vecino Más Cercano): {initial_route}")
    print(f"Distancia inicial: {initial_distance:.4f} km\n")

    # ---- 8. 2-opt ----
    optimized_route, optimized_distance = two_opt(
        initial_route, distance_matrix, verbose=VERBOSE
    )
    validate_route(optimized_route, num_used)

    print(f"Ruta optimizada (2-opt): {optimized_route}")
    print(f"Distancia optimizada: {optimized_distance:.4f} km\n")

    # ---- 9. Validaciones formales ----
    run_validations(
        initial_route, optimized_route, num_used,
        initial_distance, optimized_distance,
        distance_matrix, df_houses,
    )

    # ---- 10. Comparación de resultados ----
    reduction = initial_distance - optimized_distance
    improvement_pct = (reduction / initial_distance) * 100 if initial_distance > 0 else 0.0

    print("RESULTADOS")
    print("=" * 60)
    print(f"{'Método':<30}{'Distancia (km)':>20}")
    print("-" * 60)
    print(f"{'Vecino Más Cercano':<30}{initial_distance:>20.4f}")
    print(f"{'Vecino Más Cercano + 2-opt':<30}{optimized_distance:>20.4f}")
    print("-" * 60)
    print(f"Reducción de distancia:      {reduction:>10.4f} km")
    print(f"Porcentaje de mejora:        {improvement_pct:>10.2f} %")
    print("=" * 60 + "\n")

    # ---- 11. Tablas detalladas de las rutas ----
    print_route_table(df_houses, initial_route, distance_matrix,
                       "TABLA DETALLADA - Ruta inicial (Vecino Más Cercano)")
    print_route_table(df_houses, optimized_route, distance_matrix,
                       "TABLA DETALLADA - Ruta optimizada (Vecino Más Cercano + 2-opt)")

    # ---- 12. Visualización ----
    os.makedirs(RESULTS_DIR, exist_ok=True)

    plot_route(
        df_houses, initial_route, initial_distance,
        "Ruta inicial — Vecino Más Cercano",
        os.path.join(RESULTS_DIR, "ruta_inicial.png"),
        color="tab:orange",
    )
    plot_route(
        df_houses, optimized_route, optimized_distance,
        "Ruta optimizada — Vecino Más Cercano + 2-opt",
        os.path.join(RESULTS_DIR, "ruta_optimizada.png"),
        color="tab:green",
    )
    plot_comparison(
        df_houses, initial_route, initial_distance,
        optimized_route, optimized_distance,
        os.path.join(RESULTS_DIR, "comparacion_rutas.png"),
    )
    print()

    # ---- 13. Exportación de resultados ----
    export_results(
        df_houses, SELECTED_SUBURB, num_available, num_used, START_INDEX,
        initial_route, initial_distance,
        optimized_route, optimized_distance,
        RESULTS_DIR,
    )

    print("Programa finalizado correctamente.")


if __name__ == "__main__":
    main()
