from ipaddress import ip_address
import platform
import socket
import subprocess

import psutil


def obtener_so() -> dict:
    """Devuelve datos del sistema operativo y arquitectura."""
    return {
        "sistema": platform.system(),
        "version": platform.mac_ver()[0] or platform.version(),
        "arquitectura": platform.machine(),
    }


def obtener_hostname() -> str:
    return socket.gethostname()


def obtener_ip_local() -> str:
    """Obtiene la IP local sin enviar datos reales."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "No disponible"
    finally:
        sock.close()


def obtener_interfaces() -> dict:
    """Devuelve las interfaces de red y sus direcciones IPv4."""
    interfaces = {}
    direcciones = psutil.net_if_addrs()

    for nombre, lista_direcciones in direcciones.items():
        ips = []
        for direccion in lista_direcciones:
            if direccion.family.name == "AF_INET":
                ips.append(direccion.address)
        if ips:
            interfaces[nombre] = ips

    return interfaces


def obtener_gateway() -> str:
    """Obtiene la puerta de enlace predeterminada."""
    try:
        resultado = subprocess.run(
            ["route", "-n", "get", "default"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for linea in resultado.stdout.splitlines():
            if "gateway:" in linea:
                return linea.split("gateway:", 1)[1].strip()
        return "No encontrado"
    except (subprocess.SubprocessError, OSError) as exc:
        return f"Error: {exc}"


def obtener_dns() -> list[str]:
    """Obtiene los servidores DNS configurados sin repetirlos."""
    try:
        resultado = subprocess.run(
            ["scutil", "--dns"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        dns_servers = set()
        for linea in resultado.stdout.splitlines():
            if "nameserver" in linea:
                servidor = linea.split(":", 1)[1].strip()
                try:
                    ip_address(servidor)
                except ValueError:
                    continue
                dns_servers.add(servidor)
        return sorted(dns_servers)
    except (subprocess.SubprocessError, OSError) as exc:
        return [f"Error: {exc}"]


def obtener_servicios_locales() -> list[dict]:
    """Devuelve los servicios en escucha usando lsof."""
    servicios = []
    vistos = set()

    try:
        resultado = subprocess.run(
            ["lsof", "-i", "-P", "-n"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        for linea in resultado.stdout.splitlines()[1:]:
            if "LISTEN" not in linea:
                continue

            partes = linea.split()
            if len(partes) < 9:
                continue

            proceso = partes[0].replace(r"\x20", " ")
            pid = partes[1]
            direccion_puerto = partes[8]
            if ":" not in direccion_puerto:
                continue

            direccion, puerto = direccion_puerto.rsplit(":", 1)
            clave = (proceso, puerto)
            if clave in vistos:
                continue
            vistos.add(clave)

            servicios.append(
                {
                    "proceso": proceso,
                    "pid": pid,
                    "direccion": direccion,
                    "puerto": puerto,
                }
            )
    except (subprocess.SubprocessError, OSError) as exc:
        servicios.append({"error": str(exc)})

    return servicios


def recopilar_info_basica() -> dict:
    """Combina la información básica del equipo."""
    info = obtener_so()
    info["hostname"] = obtener_hostname()
    info["ip_local"] = obtener_ip_local()
    info["interfaces"] = obtener_interfaces()
    info["gateway"] = obtener_gateway()
    info["dns"] = obtener_dns()
    info["servicios"] = obtener_servicios_locales()
    return info