import json
from datetime import datetime
from pathlib import Path
from typing import Optional


DIRECTORIO_HISTORIAL = Path("historial")


def guardar_auditoria(datos: dict) -> str:
    """Guarda una auditoría completa y devuelve el nombre del archivo."""
    DIRECTORIO_HISTORIAL.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    ruta = DIRECTORIO_HISTORIAL / f"auditoria_{timestamp}.json"
    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
    return str(ruta)


def obtener_ultima_auditoria() -> Optional[str]:
    """Devuelve la ruta de la auditoría más reciente, si existe."""
    if not DIRECTORIO_HISTORIAL.exists():
        return None
    auditorias = sorted(DIRECTORIO_HISTORIAL.glob("auditoria_*.json"))
    return str(auditorias[-1]) if auditorias else None


def cargar_auditoria(ruta: str) -> dict:
    """Carga una auditoría guardada en JSON."""
    with Path(ruta).open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def comparar_auditorias(actual: dict, anterior: dict) -> dict:
    """Compara dispositivos, servicios y riesgos entre dos auditorías."""
    dispositivos_actuales = {
        dispositivo["ip"] for dispositivo in actual.get("dispositivos_lan", [])
    }
    dispositivos_anteriores = {
        dispositivo["ip"] for dispositivo in anterior.get("dispositivos_lan", [])
    }

    servicios_actuales = {
        f"{hallazgo['proceso']}:{hallazgo['puerto']}"
        for hallazgo in actual.get("hallazgos", [])
    }
    servicios_anteriores = {
        f"{hallazgo['proceso']}:{hallazgo['puerto']}"
        for hallazgo in anterior.get("hallazgos", [])
    }

    riesgos_anteriores = {
        f"{hallazgo['proceso']}:{hallazgo['puerto']}": hallazgo["riesgo"]
        for hallazgo in anterior.get("hallazgos", [])
    }
    cambios = []
    for hallazgo in actual.get("hallazgos", []):
        servicio = f"{hallazgo['proceso']}:{hallazgo['puerto']}"
        riesgo_anterior = riesgos_anteriores.get(servicio)
        if riesgo_anterior and riesgo_anterior != hallazgo["riesgo"]:
            cambios.append(
                {
                    "servicio": servicio,
                    "anterior": riesgo_anterior,
                    "actual": hallazgo["riesgo"],
                }
            )

    return {
        "dispositivos": {
            "nuevos": sorted(dispositivos_actuales - dispositivos_anteriores),
            "eliminados": sorted(dispositivos_anteriores - dispositivos_actuales),
        },
        "servicios": {
            "nuevos": sorted(servicios_actuales - servicios_anteriores),
            "eliminados": sorted(servicios_anteriores - servicios_actuales),
        },
        "cambios": cambios,
    }