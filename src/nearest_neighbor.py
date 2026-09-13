# -*- coding: utf-8 -*-
"""
nearest_neighbor.py
---------------------
Implementación del algoritmo heurístico Vecino Más Cercano
(Nearest Neighbor) para construir una solución inicial del TSP.

Idea general del algoritmo
---------------------------
Partiendo de una vivienda inicial, en cada paso el algoritmo se mueve
hacia la vivienda no visitada más cercana (menor costo/distancia desde
la posición actual). Este procedimiento se repite hasta visitar todas
las viviendas, y finalmente se regresa a la vivienda inicial para
cerrar el recorrido (ciclo hamiltoniano).

Es un algoritmo "goloso" (greedy): toma la mejor decisión local en cada
paso, sin considerar el efecto que esa decisión tendrá en el resto de
la ruta. Por esta razón no garantiza la solución óptima, pero es muy
rápido de calcular (complejidad O(N^2)) y ofrece un buen punto de
partida para técnicas de mejora como 2-opt.
"""

import numpy as np


def nearest_neighbor(distance_matrix: np.ndarray, start_index: int):
    """
    Construye una ruta inicial utilizando el algoritmo Vecino Más Cercano.

    Parámetros
    ----------
    distance_matrix : np.ndarray
        Matriz de distancias N x N (matriz de costos entre viviendas).
    start_index : int
        Índice (0-based) de la vivienda desde la cual se inicia el recorrido.

    Retorna
    -------
    route : list[int]
        Lista de índices representando el orden de visita. El primer y
        el último elemento son iguales a `start_index` (la ruta se cierra).
    total_distance : float
        Distancia total del recorrido, en kilómetros.

    Lanza
    -----
    ValueError
        Si `start_index` está fuera de rango.
    """
    n = distance_matrix.shape[0]

    if not (0 <= start_index < n):
        raise ValueError(
            f"ERROR: START_INDEX={start_index} está fuera de rango. "
            f"Debe estar entre 0 y {n - 1}."
        )

    visited = [False] * n
    route = [start_index]
    visited[start_index] = True
    current = start_index
    total_distance = 0.0

    # Se repite hasta visitar las N-1 viviendas restantes.
    for _ in range(n - 1):
        # Buscar, entre las viviendas no visitadas, la de menor distancia
        # respecto a la vivienda actual.
        nearest_index = None
        nearest_distance = np.inf

        for candidate in range(n):
            if not visited[candidate]:
                dist = distance_matrix[current, candidate]
                if dist < nearest_distance:
                    nearest_distance = dist
                    nearest_index = candidate

        # Moverse a la vivienda más cercana encontrada.
        route.append(nearest_index)
        visited[nearest_index] = True
        total_distance += nearest_distance
        current = nearest_index

    # Cerrar el recorrido: regresar a la vivienda inicial.
    closing_distance = distance_matrix[current, start_index]
    total_distance += closing_distance
    route.append(start_index)

    return route, total_distance


def validate_route(route: list, n: int) -> bool:
    """
    Valida que una ruta sea un ciclo hamiltoniano válido sobre `n` nodos.

    Verifica que:
      1. La ruta visite exactamente todas las viviendas (0..n-1).
      2. Ningún nodo se repita antes de regresar al origen.
      3. El primer y el último nodo sean iguales (recorrido cerrado).

    Parámetros
    ----------
    route : list[int]
        Ruta a validar (incluye el nodo de cierre al final).
    n : int
        Número total de viviendas esperado.

    Retorna
    -------
    bool
        True si la ruta es válida.

    Lanza
    -----
    ValueError
        Si alguna de las validaciones falla, con un mensaje explicando
        cuál fue el problema.
    """
    if route[0] != route[-1]:
        raise ValueError(
            "ERROR de validación: la ruta no comienza y termina en el "
            f"mismo nodo (inicio={route[0]}, fin={route[-1]})."
        )

    interior = route[:-1]  # sin contar el nodo de cierre repetido

    if len(interior) != n:
        raise ValueError(
            f"ERROR de validación: la ruta tiene {len(interior)} nodos "
            f"únicos esperados, pero se esperaban {n}."
        )

    if len(set(interior)) != n:
        raise ValueError(
            "ERROR de validación: existen nodos repetidos en la ruta "
            "antes de cerrar el recorrido."
        )

    if set(interior) != set(range(n)):
        raise ValueError(
            "ERROR de validación: la ruta no visita exactamente todos "
            "los índices esperados (0..n-1)."
        )

    return True
