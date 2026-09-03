from collections import Counter
from pathlib import Path

from analizador import detectar_nivel, leer_log


def mostrar_menu():
    print("\n¿Qué quieres hacer?")
    print("1. Analizar un archivo de log")
    print("2. Salir")


def mostrar_analisis(ruta, lineas):
    niveles = Counter(detectar_nivel(linea) for linea in lineas)

    print("\n" + "=" * 40)
    print("  SENTINEL - Análisis de Logs")
    print("=" * 40)
    print(f"Archivo: {ruta}")
    print(f"Líneas leídas: {len(lineas)}")
    print("\nConteo por nivel:")

    for nivel in ["ERROR", "WARNING", "INFO", "DEBUG", "CRITICAL", "UNKNOWN"]:
        if niveles[nivel]:
            print(f"- {nivel}: {niveles[nivel]}")


def main():
    print("=" * 40)
    print("  SENTINEL - Analizador de Logs")
    print("=" * 40)

    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "1":
            ruta = Path(input("Ruta del archivo de log: ").strip())
            lineas = leer_log(ruta)
            if lineas is not None:
                mostrar_analisis(ruta, lineas)
        elif opcion == "2":
            print("\nHasta luego.")
            break
        else:
            print("\nOpción no válida. Elige 1 o 2.")


if __name__ == "__main__":
    main()
