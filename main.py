from collections import Counter
from pathlib import Path

from analizador import detectar_nivel, leer_log
from security_analyzer import analizar_servicios, resumen_exposicion
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


def mostrar_info_red():
    info = recopilar_info_basica()

    print("\n" + "=" * 40)
    print("  SENTINEL - Información del Sistema")
    print("=" * 40)
    print(f"Sistema operativo: {info['sistema']}")
    print(f"Versión: {info['version']}")
    print(f"Arquitectura: {info['arquitectura']}")
    print(f"Hostname: {info['hostname']}")
    print(f"IP local: {info['ip_local']}")
    print(f"Gateway: {info['gateway']}")
    print(f"DNS: {', '.join(info['dns'])}")

    print("\nInterfaces de red:")
    for nombre, ips in info["interfaces"].items():
        print(f"  {nombre}: {', '.join(ips)}")

    print("\nServicios locales (escuchando):")
    if info["servicios"]:
        for servicio in info["servicios"]:
            if "error" in servicio:
                print(f"  Error: {servicio['error']}")
            else:
                print(
                    f"  {servicio['proceso']} (PID {servicio['pid']}) "
                    f"-> {servicio['direccion']}:{servicio['puerto']}"
                )
    else:
        print("  Ninguno detectado o sin permisos suficientes.")

    servicios_analizados = analizar_servicios(info["servicios"])
    resumen = resumen_exposicion(servicios_analizados)

    print("\nAnálisis de exposición:")
    for servicio in servicios_analizados:
        if "error" in servicio:
            continue
        print(
            f"  {servicio['proceso']} :{servicio['puerto']} "
            f"-> {servicio['nivel_exposicion']}"
        )
        print(f"    Descripción: {servicio['descripcion']}")
        print(f"    Conocido: {'Sí' if servicio['conocido'] else 'No'}")
        print(f"    {servicio['motivo']}")
        print(f"    Recomendación: {servicio['recomendacion']}")

    print(
        f"\nResumen: {resumen['BAJA']} baja, "
        f"{resumen['REVISAR']} revisar, "
        f"{resumen['ALTA EXPOSICIÓN']} alta exposición "
        f"(total: {resumen['total']})"
    )


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
                mostrar_info_red()
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
