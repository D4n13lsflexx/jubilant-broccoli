from collections import Counter
from pathlib import Path

from analizador import detectar_nivel, leer_log
from network_scanner import escanear_red
from security_analyzer import generar_hallazgos
from sistema import recopilar_info_basica


def mostrar_menu():
    print("\n¿Qué quieres hacer?")
    print("1. Analizar logs")
    print("2. Analizar red")
    print("3. Generar reporte")
    print("4. Escanear LAN")
    print("5. Salir")


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

    print("\nHALLAZGOS\n")
    hallazgos = generar_hallazgos(info["servicios"])
    for hallazgo in hallazgos:
        print(f"[{hallazgo['riesgo']}] {hallazgo['proceso']} :{hallazgo['puerto']}")
        print(f"  Exposición: {hallazgo['exposicion']}")
        estado = "conocido" if hallazgo["conocido"] else "no identificado"
        print(f"  {hallazgo['descripcion']} ({estado})")
        print(f"  {hallazgo['motivo']}\n")


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
            print("\nEscaneando red local (puede tardar unos segundos)...")
            try:
                info_sistema = recopilar_info_basica()
                dispositivos = escanear_red(info_sistema["ip_local"])
                print(f"\nDispositivos activos encontrados: {len(dispositivos)}")
                for dispositivo in dispositivos:
                    print(f"  {dispositivo['ip']} -> {dispositivo['mac']}")
            except (OSError, ValueError) as exc:
                print(f"No se pudo escanear la red: {exc}")
        elif opcion == "5":
            break
        else:
            print("Opción inválida")


if __name__ == "__main__":
    main()
