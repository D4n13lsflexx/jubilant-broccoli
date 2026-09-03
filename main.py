from collections import Counter
from pathlib import Path

from analizador import detectar_nivel, leer_log
from sistema import recopilar_info_basica


def mostrar_menu():
    print("\n¿Qué quieres hacer?")
    print("1. Analizar logs")
    print("2. Analizar red")
    print("3. Generar reporte")
    print("4. Salir")


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


def mostrar_info_sistema():
    print("\n" + "=" * 40)
    print("  SENTINEL - Información del sistema")
    print("=" * 40)

    for nombre, valor in recopilar_info_basica().items():
        print(f"{nombre.capitalize()}: {valor}")


def main():
    print("=" * 40)
    print("  SENTINEL - Analizador de Logs")
    print("=" * 40)

    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "1":
            try:
                ruta = Path(input("Ruta del archivo de log: ").strip())
                lineas = leer_log(ruta)
                if lineas is not None:
                    mostrar_analisis(ruta, lineas)
            except (OSError, ValueError) as exc:
                print(f"No se pudo analizar el archivo: {exc}")
        elif opcion == "2":
            try:
                mostrar_info_sistema()
            except OSError as exc:
                print(f"No se pudo obtener la información del sistema: {exc}")
        elif opcion == "3":
            print("Generando reporte...")
        elif opcion == "4":
            break
        else:
            print("Opción inválida")


if __name__ == "__main__":
    main()
