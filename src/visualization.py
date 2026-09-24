# -*- coding: utf-8 -*-
"""
visualization.py
------------------
Módulo encargado de graficar las rutas (inicial y optimizada) sobre un
plano cartesiano simple, utilizando LONGITUDE como eje X y LATITUDE
como eje Y. No se utilizan mapas externos ni APIs con clave: se trata
de una representación geométrica directa de las coordenadas.
"""

import matplotlib
matplotlib.use("Agg")  # Backend sin interfaz gráfica, apto para servidores/scripts.
import matplotlib.pyplot as plt
import pandas as pd


def plot_route(df_houses: pd.DataFrame, route: list, total_distance: float,
               title: str, output_path: str, color: str = "tab:blue"):
    """
    Genera y guarda una figura con la ruta indicada dibujada sobre las
    coordenadas de las viviendas.

    Parámetros
    ----------
    df_houses : pd.DataFrame
        DataFrame con las viviendas seleccionadas (index 0..N-1 alineado
        con los índices usados en `route`).
    route : list[int]
        Secuencia de índices que define el recorrido (cerrado, es decir,
        el primer y último elemento son iguales).
    total_distance : float
        Distancia total del recorrido, para mostrarla en el título.
    title : str
        Título principal del gráfico.
    output_path : str
        Ruta del archivo de imagen a generar (por ejemplo, .png).
    color : str
        Color de la línea de la ruta.
    """
    lons = df_houses["LONGITUDE"].values
    lats = df_houses["LATITUDE"].values

    fig, ax = plt.subplots(figsize=(9, 7))

    # 1) Dibujar todas las viviendas como puntos.
    ax.scatter(lons, lats, c="black", s=40, zorder=3, label="Viviendas")

    # 2) Etiquetar cada vivienda con su ORDEN DE VISITA en esta ruta
    #    (0 = vivienda inicial, 1 = segunda parada, ...), no con su índice
    #    fijo dentro del subconjunto. Así los números aparecen consecutivos
    #    al recorrer la ruta desde el inicio hasta el cierre. El nodo de
    #    cierre (última posición de `route`) repite físicamente la vivienda
    #    inicial, por lo que no se vuelve a etiquetar.
    for visit_order, idx in enumerate(route[:-1]):
        ax.annotate(
            str(visit_order),
            (lons[idx], lats[idx]),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
        )

    # 3) Dibujar la ruta como una secuencia de segmentos conectados.
    route_lons = [lons[i] for i in route]
    route_lats = [lats[i] for i in route]
    ax.plot(route_lons, route_lats, c=color, linewidth=1.5, zorder=2, label="Ruta")

    # 4) Resaltar el punto de inicio/cierre del recorrido.
    ax.scatter(
        [lons[route[0]]], [lats[route[0]]],
        c="red", s=120, marker="*", zorder=4, label="Vivienda inicial"
    )

    ax.set_title(f"{title}\nDistancia total: {total_distance:.4f} km")
    ax.set_xlabel("LONGITUDE")
    ax.set_ylabel("LATITUDE")
    ax.legend(loc="best")
    ax.grid(True, linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"Gráfico guardado en: {output_path}")


def plot_comparison(df_houses: pd.DataFrame, initial_route: list, initial_distance: float,
                     optimized_route: list, optimized_distance: float, output_path: str):
    """
    Genera una única figura con dos paneles lado a lado: la ruta inicial
    (Vecino Más Cercano) y la ruta optimizada (Vecino Más Cercano + 2-opt),
    para facilitar la comparación visual directa.

    Parámetros
    ----------
    df_houses : pd.DataFrame
        DataFrame con las viviendas seleccionadas.
    initial_route : list[int]
        Ruta obtenida por Vecino Más Cercano.
    initial_distance : float
        Distancia total de la ruta inicial.
    optimized_route : list[int]
        Ruta obtenida después de aplicar 2-opt.
    optimized_distance : float
        Distancia total de la ruta optimizada.
    output_path : str
        Ruta del archivo de imagen a generar.
    """
    lons = df_houses["LONGITUDE"].values
    lats = df_houses["LATITUDE"].values

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    panels = [
        (axes[0], initial_route, initial_distance,
         "Ruta inicial — Vecino Más Cercano", "tab:orange"),
        (axes[1], optimized_route, optimized_distance,
         "Ruta optimizada — Vecino Más Cercano + 2-opt", "tab:green"),
    ]

    for ax, route, distance, subtitle, color in panels:
        ax.scatter(lons, lats, c="black", s=40, zorder=3, label="Viviendas")
    
        for visit_order, idx in enumerate(route[:-1]):
            ax.annotate(
                str(visit_order),
                (lons[idx], lats[idx]),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=7,
            )
        route_lons = [lons[i] for i in route]
        route_lats = [lats[i] for i in route]
        ax.plot(route_lons, route_lats, c=color, linewidth=1.5, zorder=2, label="Ruta")
        ax.scatter(
            [lons[route[0]]], [lats[route[0]]],
            c="red", s=120, marker="*", zorder=4, label="Vivienda inicial"
        )
        ax.set_title(f"{subtitle}\nDistancia total: {distance:.4f} km")
        ax.set_xlabel("LONGITUDE")
        ax.set_ylabel("LATITUDE")
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"Gráfico comparativo guardado en: {output_path}")