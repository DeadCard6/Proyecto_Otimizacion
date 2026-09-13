# -*- coding: utf-8 -*-
"""
two_opt.py
-----------
Implementación del algoritmo de búsqueda local 2-opt (Croes, 1958),
utilizado para mejorar la ruta inicial generada por Vecino Más Cercano.

Idea general del algoritmo
---------------------------
2-opt examina pares de aristas de la ruta actual. Si al "cortar" esas
dos aristas e invertir el segmento de ruta que queda entre ellas se
obtiene una distancia total menor, el intercambio se conserva; en caso
contrario se descarta. Este proceso se repite (recorriendo todos los
pares posibles) hasta que ya no se encuentra ninguna mejora, momento en
el cual se dice que la ruta es "2-óptima" (óptimo local respecto a este
tipo de movimiento).

Este intercambio elimina los cruces innecesarios entre segmentos de la
ruta, que son una de las principales fuentes de ineficiencia en las
soluciones construidas por algoritmos golosos como Vecino Más Cercano.
"""

import numpy as np


def _route_distance(route: list, distance_matrix: np.ndarray) -> float:
    """
    Calcula la distancia total de una ruta completa (incluye el cierre
    del ciclo, es decir, el regreso al nodo inicial).
    """
    total = 0.0
    for i in range(len(route) - 1):
        total += distance_matrix[route[i], route[i + 1]]
    return total


def two_opt(route: list, distance_matrix: np.ndarray, verbose: bool = True, max_iterations: int = 1000):
    """
    Aplica el algoritmo 2-opt sobre una ruta inicial para intentar
    reducir su distancia total.

    Parámetros
    ----------
    route : list[int]
        Ruta inicial (por ejemplo, la generada por `nearest_neighbor`).
        Debe comenzar y terminar en el mismo nodo.
    distance_matrix : np.ndarray
        Matriz de distancias N x N.
    verbose : bool
        Si es True, imprime en consola el progreso de cada iteración de
        mejora encontrada.
    max_iterations : int
        Límite de seguridad de iteraciones completas (pasadas sobre toda
        la ruta) para evitar bucles infinitos en casos degenerados.

    Retorna
    -------
    best_route : list[int]
        Ruta optimizada (mismo formato que `route`, cerrada en el mismo
        nodo inicial).
    best_distance : float
        Distancia total de la ruta optimizada, en kilómetros.
    """
    best_route = route[:]
    best_distance = _route_distance(best_route, distance_matrix)

    if verbose:
        print("Aplicando 2-opt...\n")

    n = len(best_route)
    iteration = 0
    improved = True

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1

        # Se recorren todos los pares posibles de aristas (i, i+1) y (j, j+1).
        # Los índices 0 y n-1 corresponden al nodo de cierre, por lo que se
        # excluyen de la posición "i" para no romper el cierre del ciclo.
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                # Arista 1: (route[i-1], route[i])
                # Arista 2: (route[j], route[j+1])
                current_cost = (
                    distance_matrix[best_route[i - 1], best_route[i]]
                    + distance_matrix[best_route[j], best_route[j + 1]]
                )

                # Nuevo costo si se invierte el segmento [i, j].
                new_cost = (
                    distance_matrix[best_route[i - 1], best_route[j]]
                    + distance_matrix[best_route[i], best_route[j + 1]]
                )

                if new_cost < current_cost:
                    # Se invierte el segmento entre i y j (2-opt swap).
                    best_route[i:j + 1] = best_route[i:j + 1][::-1]
                    improved = True

        new_distance = _route_distance(best_route, distance_matrix)

        if verbose:
            print(f"Iteración {iteration}:")
            print(f"Distancia: {new_distance:.4f} km\n")

        best_distance = new_distance

    if verbose:
        print("Optimización finalizada.\n")

    return best_route, best_distance
