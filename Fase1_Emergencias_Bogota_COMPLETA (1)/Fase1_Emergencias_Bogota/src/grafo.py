from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd
import networkx as nx


class EntornoEmergencias:
    """Entorno de movilidad para atencion de emergencias.

    Construye un grafo no dirigido G=(V,E). Los nodos representan puntos de
    emergencia, intersecciones y hospitales. Las aristas representan tramos
    viales con atributos de distancia, tiempo, semaforos y disponibilidad.
    """

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self.nodos_df = pd.read_csv(self.data_dir / "nodos.csv")
        self.aristas_df = pd.read_csv(self.data_dir / "aristas.csv")
        self.servicios_df = pd.read_csv(self.data_dir / "servicios_urgencias_muestra.csv")
        self.demanda_df = pd.read_csv(self.data_dir / "llamadas123_resumen_localidad_muestra.csv")
        self.grafo = nx.Graph()
        self._construir_grafo()

    def _construir_grafo(self) -> None:
        demanda = {
            row["localidad"]: float(row["indice_demanda_0_1"])
            for _, row in self.demanda_df.iterrows()
        }
        servicios = self.servicios_df.set_index("id_hospital").to_dict("index")

        for _, row in self.nodos_df.iterrows():
            node_id = row["id"]
            attrs = row.to_dict()
            attrs["demanda_localidad"] = demanda.get(row["localidad"], 0.30)
            if node_id in servicios:
                attrs.update(servicios[node_id])
            self.grafo.add_node(node_id, **attrs)

        for _, row in self.aristas_df.iterrows():
            disponible = str(row["disponible"]).strip().lower() in {"si", "sí", "true", "1"}
            self.grafo.add_edge(
                row["origen"],
                row["destino"],
                distancia_km=float(row["distancia_km"]),
                tiempo_min=float(row["tiempo_min"]),
                semaforos=int(row["semaforos"]),
                disponible=disponible,
                tipo_via=row["tipo_via"],
                observacion=row["observacion"],
            )

    def hospitales_disponibles(self) -> List[str]:
        return [n for n, data in self.grafo.nodes(data=True) if data.get("tipo") == "hospital"]

    def vecinos_disponibles(self, nodo: str) -> List[str]:
        return [
            vecino
            for vecino in self.grafo.neighbors(nodo)
            if self.grafo[nodo][vecino].get("disponible", True)
        ]

    def bloquear_via(self, origen: str, destino: str) -> None:
        if self.grafo.has_edge(origen, destino):
            self.grafo[origen][destino]["disponible"] = False

    def habilitar_via(self, origen: str, destino: str) -> None:
        if self.grafo.has_edge(origen, destino):
            self.grafo[origen][destino]["disponible"] = True

    def subgrafo_disponible(self) -> nx.Graph:
        g = nx.Graph()
        for n, attrs in self.grafo.nodes(data=True):
            g.add_node(n, **attrs)
        for u, v, attrs in self.grafo.edges(data=True):
            if attrs.get("disponible", True):
                g.add_edge(u, v, **attrs)
        return g

    def resumen(self) -> Dict[str, int]:
        return {
            "nodos": self.grafo.number_of_nodes(),
            "aristas": self.grafo.number_of_edges(),
            "hospitales": len(self.hospitales_disponibles()),
        }
