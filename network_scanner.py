import ipaddress
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

from mac_vendor_lookup import MacLookup


mac_lookup = MacLookup()


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


def obtener_mac(ip: str) -> str:
    """Consulta la MAC de una IP usando arp -n."""
    try:
        resultado = subprocess.run(
            ["arp", "-n", ip],
            capture_output=True,
            text=True,
            timeout=3,
        )
        coincidencia = re.search(
            r"([0-9a-fA-F]{1,2}(?::[0-9a-fA-F]{1,2}){5})",
            resultado.stdout,
        )
        if coincidencia:
            return coincidencia.group(1)
    except (subprocess.SubprocessError, OSError):
        pass
    return "Desconocida"


def normalizar_mac(mac: str) -> str:
    """Convierte una MAC a formato estándar con ceros y mayúsculas."""
    if mac == "Desconocida":
        return mac
    octetos = mac.split(":")
    return ":".join(octeto.zfill(2).upper() for octeto in octetos)


def identificar_fabricante(mac: str) -> str:
    """Devuelve el fabricante de una MAC según la base local."""
    if mac == "Desconocida":
        return "Desconocido"
    try:
        return mac_lookup.lookup(mac)
    except Exception:
        return "Desconocido"


def escanear_red(ip_local: str) -> list[dict]:
    """Escanea la red y obtiene MAC y fabricante de cada IP activa."""
    rango = obtener_rango_red(ip_local)

    with ThreadPoolExecutor(max_workers=50) as executor:
        resultados_ping = list(executor.map(ping_ip, rango))

    ips_vivas = [ip for ip, vivo in zip(rango, resultados_ping) if vivo]

    with ThreadPoolExecutor(max_workers=10) as executor:
        macs = list(executor.map(obtener_mac, ips_vivas))
    macs = [normalizar_mac(mac) for mac in macs]

    dispositivos = []
    for ip, mac in zip(ips_vivas, macs):
        dispositivos.append(
            {
                "ip": ip,
                "mac": mac,
                "fabricante": identificar_fabricante(mac),
            }
        )

    return dispositivos