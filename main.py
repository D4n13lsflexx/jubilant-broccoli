from collections import Counter
from datetime import datetime
from pathlib import Path

from analizador import detectar_nivel, leer_log
from network_scanner import escanear_red
from report_generator import generar_reporte
from security_analyzer import generar_hallazgos
from sistema import recopilar_info_basica
from historial import (
    cargar_auditoria,
    comparar_auditorias,
    guardar_auditoria,
    obtener_ultima_auditoria,
)


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


def construir_datos_auditoria(info_sistema, hallazgos, dispositivos):
    conteo_exposicion = Counter(hallazgo["exposicion"] for hallazgo in hallazgos)
    conteo_riesgo = Counter(hallazgo["riesgo"] for hallazgo in hallazgos)

    return {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sistema": info_sistema,
        "hallazgos": hallazgos,
        "dispositivos_lan": dispositivos,
        "resumen": {
            "total_servicios": len(hallazgos),
            "exposicion": dict(conteo_exposicion),
            "riesgo": dict(conteo_riesgo),
            "total_dispositivos": len(dispositivos),
        },
    }


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

    ultima_ruta = None
    ultimas_lineas = None
    ultimos_dispositivos = []

    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "1":
            try:
                ruta = Path(input("Ruta del archivo de log: ").strip())
                lineas = leer_log(ruta)
                if lineas is not None:
                    mostrar_analisis(ruta, lineas)
                    ultima_ruta, ultimas_lineas = ruta, lineas
            except (OSError, ValueError) as exc:
                print(f"No se pudo analizar el archivo: {exc}")
        elif opcion == "2":
            try:
                mostrar_info_red()
            except OSError as exc:
                print(f"No se pudo obtener la información del sistema: {exc}")
        elif opcion == "3":
            try:
                info_sistema = recopilar_info_basica()
                hallazgos = generar_hallazgos(info_sistema["servicios"])
                nombre = generar_reporte(
                    ultima_ruta,
                    ultimas_lineas,
                    info_sistema,
                    hallazgos,
                    ultimos_dispositivos,
                )
                print(f"\nReporte guardado en: {nombre}")

                datos_actuales = construir_datos_auditoria(
                    info_sistema, hallazgos, ultimos_dispositivos
                )
                ruta_anterior = obtener_ultima_auditoria()
                if ruta_anterior:
                    auditoria_anterior = cargar_auditoria(ruta_anterior)
                    diferencias = comparar_auditorias(
                        datos_actuales, auditoria_anterior
                    )

                    print("\n--- CAMBIOS DESDE LA ÚLTIMA AUDITORÍA ---")
                    if diferencias["dispositivos"]["nuevos"]:
                        print("\nDispositivos nuevos:")
                        for ip in diferencias["dispositivos"]["nuevos"]:
                            print(f"  + {ip}")
                    if diferencias["dispositivos"]["eliminados"]:
                        print("\nDispositivos desaparecidos:")
                        for ip in diferencias["dispositivos"]["eliminados"]:
                            print(f"  - {ip}")
                    if diferencias["servicios"]["nuevos"]:
                        print("\nServicios nuevos:")
                        for servicio in diferencias["servicios"]["nuevos"]:
                            print(f"  + {servicio}")
                    if diferencias["servicios"]["eliminados"]:
                        print("\nServicios desaparecidos:")
                        for servicio in diferencias["servicios"]["eliminados"]:
                            print(f"  - {servicio}")
                    if diferencias["cambios"]:
                        print("\nCambios de riesgo:")
                        for cambio in diferencias["cambios"]:
                            print(
                                f"  {cambio['servicio']}: "
                                f"{cambio['anterior']} -> {cambio['actual']}"
                            )

                    sin_cambios = not any(
                        [
                            diferencias["dispositivos"]["nuevos"],
                            diferencias["dispositivos"]["eliminados"],
                            diferencias["servicios"]["nuevos"],
                            diferencias["servicios"]["eliminados"],
                            diferencias["cambios"],
                        ]
                    )
                    if sin_cambios:
                        print("\nSin cambios respecto a la auditoría anterior.")
                else:
                    print(
                        "\nEsta es la primera auditoría guardada - "
                        "no hay nada con qué comparar todavía."
                    )

                guardar_auditoria(datos_actuales)
            except (OSError, ValueError, KeyError) as exc:
                print(f"No se pudo generar el reporte: {exc}")
        elif opcion == "4":
            print("\nEscaneando red local (puede tardar unos segundos)...")
            try:
                info_sistema = recopilar_info_basica()
                ultimos_dispositivos = escanear_red(info_sistema["ip_local"])
                print(f"\nDispositivos activos encontrados: {len(ultimos_dispositivos)}")
                for dispositivo in ultimos_dispositivos:
                    print(
                        f"  {dispositivo['ip']} -> {dispositivo['mac']} "
                        f"({dispositivo['fabricante']})"
                    )
            except (OSError, ValueError) as exc:
                print(f"No se pudo escanear la red: {exc}")
        elif opcion == "5":
            break
        else:
            print("Opción inválida")


if __name__ == "__main__":
    main()
