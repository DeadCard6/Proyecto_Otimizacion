# -*- coding: utf-8 -*-
"""
data_loader.py
----------------
Módulo encargado de:
  1. Cargar el dataset inmobiliario de Perth desde un archivo CSV.
  2. Limpiar los registros (eliminar filas incompletas o con coordenadas inválidas).
  3. Permitir la selección de un suburbio y de un subconjunto de viviendas
     dentro de ese suburbio para construir la instancia del problema TSP.

Todas las funciones devuelven DataFrames de pandas y no modifican el
archivo original en disco.
"""

import os
import pandas as pd
import numpy as np

# Columnas que el proyecto necesita obligatoriamente para poder ejecutarse.
REQUIRED_COLUMNS = ["ADDRESS", "SUBURB", "LATITUDE", "LONGITUDE"]


def load_dataset(dataset_path: str) -> pd.DataFrame:
    """
    Carga el archivo CSV indicado en `dataset_path`.

    Parámetros
    ----------
    dataset_path : str
        Ruta al archivo CSV con los datos inmobiliarios.

    Retorna
    -------
    pd.DataFrame
        DataFrame con el contenido íntegro del archivo.

    Lanza
    -----
    FileNotFoundError
        Si el archivo no existe en la ruta indicada.
    ValueError
        Si el archivo no contiene alguna de las columnas obligatorias.
    """
    if not os.path.isfile(dataset_path):
        raise FileNotFoundError(
            f"No se encontró el archivo del dataset en: '{dataset_path}'.\n"
            f"Verifica la variable DATASET_PATH en main.py."
        )

    df = pd.read_csv(dataset_path)

    print("=" * 60)
    print("CARGA DEL DATASET")
    print("=" * 60)
    print(f"Archivo cargado: {dataset_path}")
    print(f"Cantidad de registros: {len(df)}")
    print(f"Cantidad de columnas: {len(df.columns)}")
    print(f"Nombres de columnas: {list(df.columns)}")
    print("\nPrimeras filas del dataset:")
    print(df.head())

    # Verificación de columnas obligatorias.
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(
            "ERROR: El dataset no contiene las siguientes columnas "
            f"obligatorias: {missing_columns}.\n"
            "El programa no puede continuar sin estas columnas, ya que son "
            "necesarias para identificar las viviendas y sus coordenadas."
        )

    print("\nTodas las columnas requeridas (ADDRESS, SUBURB, LATITUDE, "
          "LONGITUDE) están presentes.")
    print("=" * 60 + "\n")

    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia el DataFrame eliminando registros incompletos o inválidos.

    Reglas de limpieza aplicadas:
      - Se eliminan filas sin ADDRESS.
      - Se eliminan filas sin SUBURB.
      - Se eliminan filas sin LATITUDE o LONGITUDE.
      - Se convierten LATITUDE y LONGITUDE a valores numéricos (float).
      - Se eliminan coordenadas fuera de rangos geográficos válidos
        (latitud entre -90 y 90, longitud entre -180 y 180) y coordenadas
        igual a (0, 0), que suelen representar datos faltantes.
      - Se eliminan duplicados exactos en ADDRESS + SUBURB.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame original devuelto por `load_dataset`.

    Retorna
    -------
    pd.DataFrame
        DataFrame limpio, con índice reiniciado.
    """
    original_count = len(df)
    df_clean = df.copy()

    # 1) Eliminar filas sin ADDRESS o SUBURB (valores nulos o cadenas vacías).
    df_clean = df_clean.dropna(subset=["ADDRESS", "SUBURB"])
    df_clean = df_clean[df_clean["ADDRESS"].astype(str).str.strip() != ""]
    df_clean = df_clean[df_clean["SUBURB"].astype(str).str.strip() != ""]

    # 2) Eliminar filas sin LATITUDE/LONGITUDE.
    df_clean = df_clean.dropna(subset=["LATITUDE", "LONGITUDE"])

    # 3) Convertir a numérico. Los valores no convertibles se marcan como NaN
    #    y luego se eliminan.
    df_clean["LATITUDE"] = pd.to_numeric(df_clean["LATITUDE"], errors="coerce")
    df_clean["LONGITUDE"] = pd.to_numeric(df_clean["LONGITUDE"], errors="coerce")
    df_clean = df_clean.dropna(subset=["LATITUDE", "LONGITUDE"])

    # 4) Eliminar coordenadas fuera de rango o iguales a (0, 0).
    valid_lat = df_clean["LATITUDE"].between(-90, 90)
    valid_lon = df_clean["LONGITUDE"].between(-180, 180)
    not_zero_zero = ~((df_clean["LATITUDE"] == 0) & (df_clean["LONGITUDE"] == 0))
    df_clean = df_clean[valid_lat & valid_lon & not_zero_zero]

    # 5) Eliminar duplicados (misma dirección dentro del mismo suburbio).
    df_clean = df_clean.drop_duplicates(subset=["ADDRESS", "SUBURB"])

    # Reiniciar índice para que sea 0..N-1 de forma consecutiva.
    df_clean = df_clean.reset_index(drop=True)

    cleaned_count = len(df_clean)
    removed_count = original_count - cleaned_count

    print("=" * 60)
    print("LIMPIEZA DE DATOS")
    print("=" * 60)
    print(f"Registros originales: {original_count}")
    print(f"Registros después de limpieza: {cleaned_count}")
    print(f"Registros eliminados: {removed_count}")
    print("=" * 60 + "\n")

    return df_clean


def show_available_suburbs(df: pd.DataFrame, top_n: int = 20) -> pd.Series:
    """
    Muestra en pantalla los suburbios disponibles y la cantidad de
    viviendas válidas (post-limpieza) que tiene cada uno.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame limpio.
    top_n : int
        Cantidad máxima de suburbios a mostrar (para no saturar la consola).

    Retorna
    -------
    pd.Series
        Conteo de viviendas por suburbio (índice = nombre del suburbio),
        ordenado de mayor a menor.
    """
    counts = df["SUBURB"].value_counts()

    print("=" * 60)
    print("SUBURBIOS DISPONIBLES")
    print("=" * 60)
    print(f"{'SUBURB':<25}{'VIVIENDAS':>10}")
    print("-" * 35)
    for suburb, count in counts.head(top_n).items():
        print(f"{suburb:<25}{count:>10}")
    if len(counts) > top_n:
        print(f"... ({len(counts) - top_n} suburbios adicionales no mostrados)")
    print("=" * 60 + "\n")

    return counts


def select_suburb_data(df: pd.DataFrame, suburb_name: str) -> pd.DataFrame:
    """
    Filtra el DataFrame para conservar únicamente las viviendas del
    suburbio indicado.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame limpio (todos los suburbios).
    suburb_name : str
        Nombre exacto del suburbio a seleccionar (debe existir en el dataset).

    Retorna
    -------
    pd.DataFrame
        Subconjunto de `df` correspondiente al suburbio, con índice reiniciado.

    Lanza
    -----
    ValueError
        Si el suburbio indicado no existe en el dataset.
    """
    available_suburbs = df["SUBURB"].unique()
    if suburb_name not in available_suburbs:
        raise ValueError(
            f"ERROR: El suburbio '{suburb_name}' no existe en el dataset.\n"
            "Usa show_available_suburbs() para ver los suburbios válidos."
        )

    df_suburb = df[df["SUBURB"] == suburb_name].reset_index(drop=True)
    return df_suburb


def select_houses_subset(df_suburb: pd.DataFrame, num_houses: int) -> pd.DataFrame:
    """
    Selecciona las primeras `num_houses` viviendas de un suburbio ya filtrado.

    Se toman las primeras filas en el orden en que aparecen en el dataset
    (no se realiza muestreo aleatorio, para que el resultado sea reproducible).

    Parámetros
    ----------
    df_suburb : pd.DataFrame
        DataFrame ya filtrado por un único suburbio.
    num_houses : int
        Cantidad de viviendas a utilizar.

    Retorna
    -------
    pd.DataFrame
        Subconjunto con `num_houses` filas, índice reiniciado (0..N-1).

    Lanza
    -----
    ValueError
        Si `num_houses` es mayor a la cantidad de viviendas disponibles,
        o si es menor a 2 (un TSP requiere al menos 2 nodos).
    """
    available = len(df_suburb)

    if num_houses < 2:
        raise ValueError(
            f"ERROR: NUM_HOUSES debe ser al menos 2 para poder construir "
            f"una ruta. Se recibió: {num_houses}."
        )

    if num_houses > available:
        raise ValueError(
            f"ERROR: Se solicitaron {num_houses} viviendas, pero el "
            f"suburbio seleccionado solo tiene {available} viviendas "
            f"válidas disponibles. Reduce NUM_HOUSES."
        )

    subset = df_suburb.iloc[:num_houses].reset_index(drop=True)
    return subset
