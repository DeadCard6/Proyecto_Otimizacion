# -*- coding: utf-8 -*-
"""
distances.py
-------------
Módulo encargado del cálculo de distancias geográficas entre viviendas
y de la construcción de la matriz de distancias N x N utilizada como
matriz de costos por los algoritmos Vecino Más Cercano y 2-opt.

Fundamento matemático
----------------------
Dado que la Tierra es (aproximadamente) un esferoide, la distancia entre
dos puntos definidos por (latitud, longitud) no puede calcularse con la
distancia euclidiana plana sin introducir errores significativos, sobre
todo a mayor escala. Por ello se utiliza la fórmula de distancia
geodésica implementada en la librería `geopy` (basada en el algoritmo
de Karney sobre el elipsoide WGS-84), que entrega la distancia real
sobre la superficie terrestre en kilómetros.
"""

import numpy as np
import pandas as pd
from geopy.distance import geodesic


def calculate_distance(coord1: tuple, coord2: tuple) -> float:
    """
    Calcula la distancia geodésica (en kilómetros) entre dos coordenadas.

    Parámetros
    ----------
    coord1 : tuple(float, float)
        Tupla (latitud, longitud) del primer punto.
    coord2 : tuple(float, float)
        Tupla (latitud, longitud) del segundo punto.

    Retorna
    -------
    float
        Distancia en kilómetros entre los dos puntos.
    """
    return geodesic(coord1, coord2).km


def build_distance_matrix(df_houses: pd.DataFrame) -> np.ndarray:
    """
    Construye la matriz de distancias N x N entre todas las viviendas
    del subconjunto seleccionado.

    La matriz es simétrica (distancia(i, j) == distancia(j, i)) y su
    diagonal principal es cero (distancia de un punto a sí mismo).

    Parámetros
    ----------
    df_houses : pd.DataFrame
        DataFrame con las viviendas seleccionadas. Debe contener las
        columnas LATITUDE y LONGITUDE, e index consecutivo 0..N-1.

    Retorna
    -------
    np.ndarray
        Matriz de distancias de tamaño (N, N), en kilómetros.
    """
    n = len(df_houses)
    coords = list(zip(df_houses["LATITUDE"].values, df_houses["LONGITUDE"].values))

    distance_matrix = np.zeros((n, n), dtype=float)

    # Solo se calcula el triángulo superior y se refleja, ya que la
    # distancia geodésica es simétrica: esto reduce a la mitad el
    # número de llamadas a geopy (de N^2 a N*(N-1)/2).
    for i in range(n):
        for j in range(i + 1, n):
            dist = calculate_distance(coords[i], coords[j])
            distance_matrix[i, j] = dist
            distance_matrix[j, i] = dist

    return distance_matrix


def print_distance_matrix(distance_matrix: np.ndarray, labels=None, max_size: int = 15):
    """
    Imprime en consola la matriz de distancias de forma legible, solo si
    el número de viviendas es razonablemente pequeño (para no saturar la
    consola con matrices enormes).

    Parámetros
    ----------
    distance_matrix : np.ndarray
        Matriz de distancias N x N.
    labels : list[str], opcional
        Etiquetas (por ejemplo H1, H2, ...) para las filas/columnas.
        Si no se proporciona, se generan automáticamente.
    max_size : int
        Tamaño máximo de matriz a imprimir completa en consola.
    """
    n = distance_matrix.shape[0]

    if labels is None:
        labels = [f"H{i}" for i in range(n)]

    if n > max_size:
        print(f"(La matriz de distancias tiene {n}x{n} elementos; se omite "
              f"su impresión completa por ser demasiado grande. "
              f"Se muestra únicamente para conjuntos de hasta {max_size} viviendas.)\n")
        return

    print("Matriz de distancias (km):")
    header = "      " + "".join(f"{lbl:>9}" for lbl in labels)
    print(header)
    for i in range(n):
        row = f"{labels[i]:<6}" + "".join(f"{distance_matrix[i, j]:9.2f}" for j in range(n))
        print(row)
    print()
