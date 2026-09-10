from __future__ import annotations

from pathlib import Path

from agente import AgenteEmergenciasUtilidad
from grafo import EntornoEmergencias


def ejecutar_pruebas(data_dir: str | Path, output_file: str | Path | None = None) -> str:
    entorno = EntornoEmergencias(data_dir)
    agente = AgenteEmergenciasUtilidad(entorno)
    lineas = []

    lineas.append("========== RESUMEN DEL ENTORNO ==========")
    lineas.append(str(entorno.resumen()))
    lineas.append("")

    lineas.append("========== PRUEBA 1: Ruta normal ==========")
    r1 = agente.seleccionar_mejor_ruta("E_KEN")
    lineas.append(agente.explicar_decision(r1))

    lineas.append("========== PRUEBA 2: Comparacion por criterio ==========")
    # Criterio simple: hospital con menor distancia de ruta sin bonificar adecuacion.
    resultados = [agente.evaluar_ruta("E_KEN", h) for h in entorno.hospitales_disponibles()]
    resultados = [r for r in resultados if r is not None]
    por_distancia = min(resultados, key=lambda r: r.distancia_total)
    por_utilidad = min(resultados, key=lambda r: r.utilidad)
    lineas.append(f"Centro mas cercano por distancia: {por_distancia.hospital} ({por_distancia.distancia_total} km)")
    lineas.append(f"Centro elegido por utilidad: {por_utilidad.hospital} (utilidad {por_utilidad.utilidad})")
    lineas.append("Interpretacion: el agente puede considerar tiempo, semaforos, demanda local y adecuacion del servicio, no solo distancia.")
    lineas.append("")

    lineas.append("========== PRUEBA 3: Bloqueo dinamico ==========")
    entorno.bloquear_via("E_KEN", "H_KEN")
    entorno.bloquear_via("E_KEN", "H_BAS")
    r3 = agente.seleccionar_mejor_ruta("E_KEN")
    lineas.append("Se bloquearon los accesos E_KEN - H_KEN y E_KEN - H_BAS para simular afectacion en la zona cercana.")
    lineas.append(agente.explicar_decision(r3))
    lineas.append("Interpretacion: el agente percibe que la conexion ya no esta disponible y recalcula una ruta valida.")

    salida = "\n".join(lineas)
    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(output_file).write_text(salida, encoding="utf-8")
    return salida


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[1]
    print(ejecutar_pruebas(repo / "data", repo / "output" / "salida_pruebas.txt"))
