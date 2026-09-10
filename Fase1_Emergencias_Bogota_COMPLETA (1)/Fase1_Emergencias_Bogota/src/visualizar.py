from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx

from grafo import EntornoEmergencias
from agente import AgenteEmergenciasUtilidad


def posiciones(entorno: EntornoEmergencias) -> Dict[str, Tuple[float, float]]:
    return {n: (float(d["lon"]), float(d["lat"])) for n, d in entorno.grafo.nodes(data=True)}


def separar_nodos_cercanos(pos: Dict[str, Tuple[float, float]], umbral_frac: float = 0.05) -> Dict[str, Tuple[float, float]]:
    """Separa visualmente los nodos que estan muy cerca entre si en lat/lon.

    Agrupa nodos cuya distancia sea menor a un umbral (proporcional al tamano
    del area total) y los reubica en un pequeno circulo alrededor del
    centroide del grupo, conservando la posicion geografica general del
    grafo mientras evita que los marcadores y las etiquetas se encimen.
    """
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    ancho = max(xs) - min(xs) or 1.0
    alto = max(ys) - min(ys) or 1.0
    diagonal = math.hypot(ancho, alto)
    umbral = diagonal * umbral_frac

    nodos = list(pos.keys())
    padre = {n: n for n in nodos}

    def encontrar(n):
        while padre[n] != n:
            padre[n] = padre[padre[n]]
            n = padre[n]
        return n

    def unir(a, b):
        ra, rb = encontrar(a), encontrar(b)
        if ra != rb:
            padre[ra] = rb

    for i in range(len(nodos)):
        for j in range(i + 1, len(nodos)):
            a, b = nodos[i], nodos[j]
            d = math.hypot(pos[a][0] - pos[b][0], pos[a][1] - pos[b][1])
            if d < umbral:
                unir(a, b)

    grupos: Dict[str, List[str]] = {}
    for n in nodos:
        grupos.setdefault(encontrar(n), []).append(n)

    nueva_pos = dict(pos)
    radio_deseado = umbral * 1.8
    for miembros in grupos.values():
        if len(miembros) < 2:
            continue
        cx = sum(pos[m][0] for m in miembros) / len(miembros)
        cy = sum(pos[m][1] for m in miembros) / len(miembros)

        # El radio no debe acercar el grupo a nodos externos vecinos: se
        # limita a una fraccion de la distancia al nodo externo mas cercano.
        externos = [pos[m] for m in nodos if m not in miembros]
        if externos:
            dist_min_externo = min(math.hypot(cx - ex, cy - ey) for ex, ey in externos)
            radio = min(radio_deseado, dist_min_externo * 0.45)
        else:
            radio = radio_deseado

        n = len(miembros)
        for idx, m in enumerate(sorted(miembros)):
            angulo = 2 * math.pi * idx / n
            nueva_pos[m] = (cx + radio * math.cos(angulo), cy + radio * math.sin(angulo))
    return nueva_pos


def dibujar_grafo(entorno: EntornoEmergencias, ruta: List[str] | None, titulo: str, salida: Path):
    g = entorno.grafo
    pos_geo = posiciones(entorno)
    pos = separar_nodos_cercanos(pos_geo)

    plt.figure(figsize=(15, 10))
    ax = plt.gca()

    nx.draw_networkx_edges(g, pos, alpha=0.35, width=1.5, ax=ax)

    tipos = nx.get_node_attributes(g, "tipo")
    estilos = {
        "emergencia": {"shape": "s", "color": "#e67e22"},
        "interseccion": {"shape": "o", "color": "#3498db"},
        "hospital": {"shape": "^", "color": "#c0392b"},
    }
    nombres_leyenda = {"emergencia": "Emergencia", "interseccion": "Interseccion", "hospital": "Hospital"}
    for tipo, estilo in estilos.items():
        nodes = [n for n, t in tipos.items() if t == tipo]
        if not nodes:
            continue
        nx.draw_networkx_nodes(
            g, pos, nodelist=nodes, node_shape=estilo["shape"], node_color=estilo["color"],
            node_size=750, alpha=0.9, edgecolors="white", linewidths=1.0, ax=ax,
            label=nombres_leyenda[tipo],
        )

    # Etiquetas de nodos desplazadas hacia abajo del marcador, con fondo
    # blanco semitransparente para que no se pierdan sobre las aristas.
    for n, (x, y) in pos.items():
        ax.annotate(
            n, xy=(x, y), xytext=(0, -14), textcoords="offset points",
            ha="center", va="top", fontsize=8, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75),
            zorder=5,
        )

    edge_labels = {(u, v): f"{d['distancia_km']}km/{d['tiempo_min']}min" for u, v, d in g.edges(data=True)}
    nx.draw_networkx_edge_labels(
        g, pos, edge_labels=edge_labels, font_size=7, ax=ax,
        bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7),
    )

    if ruta and len(ruta) > 1:
        path_edges = list(zip(ruta[:-1], ruta[1:]))
        nx.draw_networkx_edges(g, pos, edgelist=path_edges, width=4.0, alpha=0.95, edge_color="#2c3e50", ax=ax)
        nx.draw_networkx_nodes(g, pos, nodelist=ruta, node_size=950, alpha=0.4, node_color="#f1c40f", ax=ax)

    plt.title(titulo)
    plt.xlabel("Longitud")
    plt.ylabel("Latitud")
    plt.legend(scatterpoints=1, loc="upper left", framealpha=0.9)
    plt.margins(0.12)
    plt.tight_layout()
    salida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(salida, dpi=180)
    plt.close()


def generar_figuras(base_dir: str | Path):
    base = Path(base_dir)
    entorno = EntornoEmergencias(base / "data")
    agente = AgenteEmergenciasUtilidad(entorno)

    dibujar_grafo(entorno, None, "Red inicial de emergencias - Fase 1", base / "figures" / "grafo_red_emergencias.png")

    r1 = agente.seleccionar_mejor_ruta("E_KEN")
    dibujar_grafo(entorno, r1.ruta, "Prueba 1 - Ruta normal seleccionada por utilidad", base / "figures" / "ruta_normal.png")

    entorno.bloquear_via("E_KEN", "H_KEN")
    entorno.bloquear_via("E_KEN", "H_BAS")
    r3 = agente.seleccionar_mejor_ruta("E_KEN")
    dibujar_grafo(entorno, r3.ruta, "Prueba 3 - Recalculo con via bloqueada", base / "figures" / "ruta_bloqueo.png")


if __name__ == "__main__":
    generar_figuras(Path(__file__).resolve().parents[1])
