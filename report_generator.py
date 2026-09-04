from collections import Counter
from datetime import datetime

from analizador import detectar_nivel


def generar_reporte(
    ruta_log, lineas, info_sistema, hallazgos, dispositivos
) -> str:
    """Genera un reporte de auditoría en formato TXT."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"reporte_{timestamp}.txt"

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write("=" * 50 + "\n")
        archivo.write("  SENTINEL - Reporte de Auditoría\n")
        archivo.write("=" * 50 + "\n")
        archivo.write(
            f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        archivo.write("--- Análisis de Logs ---\n")
        if lineas:
            niveles = Counter(detectar_nivel(linea) for linea in lineas)
            archivo.write(f"Archivo: {ruta_log}\n")
            archivo.write(f"Líneas leídas: {len(lineas)}\n")
            for nivel in ["ERROR", "WARNING", "INFO", "DEBUG", "CRITICAL", "UNKNOWN"]:
                if niveles[nivel]:
                    archivo.write(f"  {nivel}: {niveles[nivel]}\n")
        else:
            archivo.write("No se ha analizado ningún log todavía.\n")

        archivo.write("\n--- Información del Sistema ---\n")
        archivo.write(f"Sistema operativo: {info_sistema['sistema']}\n")
        archivo.write(f"Versión: {info_sistema['version']}\n")
        archivo.write(f"Arquitectura: {info_sistema['arquitectura']}\n")
        archivo.write(f"Hostname: {info_sistema['hostname']}\n")
        archivo.write(f"IP local: {info_sistema['ip_local']}\n")
        archivo.write(f"Gateway: {info_sistema['gateway']}\n")
        archivo.write(f"DNS: {', '.join(info_sistema['dns'])}\n")
        archivo.write("\nInterfaces de red:\n")
        for nombre, ips in info_sistema["interfaces"].items():
            archivo.write(f"  {nombre}: {', '.join(ips)}\n")

        archivo.write("\n--- Hallazgos de Seguridad ---\n")
        if hallazgos:
            conteo_riesgo = Counter(hallazgo["riesgo"] for hallazgo in hallazgos)
            archivo.write(
                f"Total: {len(hallazgos)} servicio(s) - "
                + ", ".join(
                    f"{cantidad} {riesgo}"
                    for riesgo, cantidad in conteo_riesgo.items()
                )
                + "\n\n"
            )
            for hallazgo in hallazgos:
                archivo.write(
                    f"[{hallazgo['riesgo']}] "
                    f"{hallazgo['proceso']} :{hallazgo['puerto']}\n"
                )
                archivo.write(f"  Exposición: {hallazgo['exposicion']}\n")
                estado = "conocido" if hallazgo["conocido"] else "no identificado"
                archivo.write(f"  {hallazgo['descripcion']} ({estado})\n")
                archivo.write(f"  {hallazgo['motivo']}\n\n")
        else:
            archivo.write("No se detectaron servicios locales.\n")

        archivo.write("\n--- Dispositivos en la Red Local ---\n")
        if dispositivos:
            archivo.write(f"Total detectados: {len(dispositivos)}\n\n")
            for dispositivo in dispositivos:
                archivo.write(
                    f"  {dispositivo['ip']} -> {dispositivo['mac']} "
                    f"({dispositivo['fabricante']})\n"
                )
        else:
            archivo.write("No se ha ejecutado el escaneo de LAN todavía.\n")

    return nombre_archivo