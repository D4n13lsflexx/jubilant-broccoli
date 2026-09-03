import platform
import socket


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


def recopilar_info_basica() -> dict:
    """Combina la información básica del equipo."""
    info = obtener_so()
    info["hostname"] = obtener_hostname()
    info["ip_local"] = obtener_ip_local()
    return info