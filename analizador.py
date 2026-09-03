import sys
from collections import Counter
from pathlib import Path


def leer_log(ruta_archivo):
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{ruta_archivo}'")
        return None
    except OSError as exc:
        print(f"Error al leer el archivo: {exc}")
        return None

    return [linea.rstrip("\n") for linea in lineas]


def detectar_nivel(linea):
    texto = linea.lower()
    for nivel in ("critical", "error", "warning", "info", "debug"):
        if nivel in texto:
            return nivel.upper()
    return "UNKNOWN"


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 analizador.py <ruta_del_log>")
        print("Ejemplo: python3 analizador.py logs/ejemplo.log")
        return 1

    ruta = Path(sys.argv[1])
    lineas = leer_log(ruta)
    if lineas is None:
        return 1

    total = len(lineas)
    niveles = Counter(detectar_nivel(linea) for linea in lineas)

    print("=" * 40)
    print("  SENTINEL - Análisis de Logs")
    print("=" * 40)
    print(f"Archivo: {ruta}")
    print(f"Líneas leídas: {total}")
    print("\nConteo por nivel:")

    for nivel in ["ERROR", "WARNING", "INFO", "DEBUG", "CRITICAL", "UNKNOWN"]:
        if niveles[nivel]:
            print(f"- {nivel}: {niveles[nivel]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
