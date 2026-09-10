from pathlib import Path

from pruebas import ejecutar_pruebas


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1]
    salida = ejecutar_pruebas(base / "data", base / "output" / "salida_pruebas.txt")
    print(salida)
