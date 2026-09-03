import ipaddress
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor


PATRON_ARP = re.compile(r"\(([\d.]+)\) at ([0-9a-fA-F:]{17})")


def obtener_rango_red(ip_local: str, prefijo: int = 24) -> list[str]:
    """Calcula las IPs utilizables de la red local."""
    red = ipaddress.ip_network(f"{ip_local}/{prefijo}", strict=False)
    return [str(ip) for ip in red.hosts()]


def ping_ip(ip: str) -> bool:
    """Envía un ping individual con timeout corto."""
    try:
        resultado = subprocess.run(
            ["ping", "-c", "1", "-W", "1000", ip],
            capture_output=True,
            timeout=2,
        )
        return resultado.returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False


def obtener_tabla_arp() -> dict:
    """Devuelve IP y MAC de las entradas completas de arp -a."""
    tabla = {}
    try:
        resultado = subprocess.run(
            ["arp", "-a"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for linea in resultado.stdout.splitlines():
            coincidencia = PATRON_ARP.search(linea)
            if coincidencia:
                ip, mac = coincidencia.groups()
                tabla[ip] = mac
    except (subprocess.SubprocessError, OSError):
        pass
    return tabla


def escanear_red(ip_local: str) -> list[dict]:
    """Escanea la red local con pings paralelos y cruza la tabla ARP."""
    rango = obtener_rango_red(ip_local)

    with ThreadPoolExecutor(max_workers=50) as executor:
        resultados = executor.map(ping_ip, rango)

    ips_vivas = [ip for ip, vivo in zip(rango, resultados) if vivo]
    tabla_arp = obtener_tabla_arp()

    return [
        {"ip": ip, "mac": tabla_arp.get(ip, "Desconocida")}
        for ip in ips_vivas
    ]