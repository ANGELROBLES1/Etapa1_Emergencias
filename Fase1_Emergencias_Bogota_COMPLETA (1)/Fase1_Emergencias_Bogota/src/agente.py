from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import networkx as nx

from grafo import EntornoEmergencias


@dataclass
class ResultadoRuta:
    hospital: str
    ruta: List[str]
    costo_total: float
    distancia_total: float
    tiempo_total: float
    semaforos_total: int
    utilidad: float


class AgenteEmergenciasUtilidad:
    """Agente basado en utilidad para seleccionar centro de urgencias y ruta.

    El agente percibe el grafo disponible, evalua rutas posibles hacia centros
    de urgencias y elige la alternativa con menor costo ajustado. En Fase 1 se
    usa Dijkstra ponderado como mecanismo inicial de decision; en Fase 2 se
    reemplazara/comparara con BFS, DFS, UCS, Greedy y A*.
    """

    def __init__(self, entorno: EntornoEmergencias, pesos: Dict[str, float] | None = None):
        self.entorno = entorno
        self.pesos = pesos or {
            "distancia": 0.35,
            "tiempo": 0.30,
            "semaforos": 0.15,
            "demanda": 0.10,
            "adecuacion": 0.25,
        }

    def costo_arista(self, u: str, v: str, attrs: Dict) -> float:
        localidad_destino = self.entorno.grafo.nodes[v].get("localidad", "")
        demanda = float(self.entorno.grafo.nodes[v].get("demanda_localidad", 0.30))
        return (
            self.pesos["distancia"] * float(attrs["distancia_km"])
            + self.pesos["tiempo"] * (float(attrs["tiempo_min"]) / 10)
            + self.pesos["semaforos"] * (int(attrs["semaforos"]) / 5)
            + self.pesos["demanda"] * demanda
        )

    def evaluar_ruta(self, origen: str, hospital: str) -> ResultadoRuta | None:
        g = self.entorno.subgrafo_disponible()
        try:
            ruta = nx.shortest_path(g, origen, hospital, weight=self.costo_arista)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

        distancia = 0.0
        tiempo = 0.0
        semaforos = 0
        costo = 0.0
        for u, v in zip(ruta[:-1], ruta[1:]):
            attrs = g[u][v]
            distancia += float(attrs["distancia_km"])
            tiempo += float(attrs["tiempo_min"])
            semaforos += int(attrs["semaforos"])
            costo += self.costo_arista(u, v, attrs)

        datos_hospital = g.nodes[hospital]
        adecuacion = float(datos_hospital.get("nivel_adecuacion", 3))
        # Mientras mayor sea la adecuacion del centro, menor queda el costo ajustado.
        utilidad = costo - self.pesos["adecuacion"] * adecuacion

        return ResultadoRuta(
            hospital=hospital,
            ruta=ruta,
            costo_total=round(costo, 4),
            distancia_total=round(distancia, 2),
            tiempo_total=round(tiempo, 2),
            semaforos_total=semaforos,
            utilidad=round(utilidad, 4),
        )

    def seleccionar_mejor_ruta(self, origen: str) -> ResultadoRuta:
        candidatos = []
        for hospital in self.entorno.hospitales_disponibles():
            resultado = self.evaluar_ruta(origen, hospital)
            if resultado is not None:
                candidatos.append(resultado)
        if not candidatos:
            raise ValueError("No existe ruta disponible hacia ningun hospital.")
        return min(candidatos, key=lambda r: r.utilidad)

    def explicar_decision(self, resultado: ResultadoRuta) -> str:
        nombres = [self.entorno.grafo.nodes[n]["nombre"] for n in resultado.ruta]
        return (
            f"Hospital seleccionado: {self.entorno.grafo.nodes[resultado.hospital]['nombre']}\n"
            f"Ruta: {' -> '.join(resultado.ruta)}\n"
            f"Ruta detallada: {' -> '.join(nombres)}\n"
            f"Distancia total: {resultado.distancia_total} km\n"
            f"Tiempo estimado: {resultado.tiempo_total} min\n"
            f"Semaforos estimados: {resultado.semaforos_total}\n"
            f"Costo combinado: {resultado.costo_total}\n"
            f"Utilidad ajustada: {resultado.utilidad}\n"
        )
