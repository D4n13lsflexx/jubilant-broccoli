PROCESOS_CONOCIDOS = {
    "ControlCe": "AirPlay Receiver / Control Center (macOS)",
    "rapportd": "Continuity / Handoff (macOS)",
}

MATRIZ_RIESGO = {
    ("BAJA", True): "BAJO",
    ("BAJA", False): "REVISAR",
    ("REVISAR", True): "REVISAR",
    ("REVISAR", False): "ALTA PRIORIDAD",
    ("ALTA EXPOSICIÓN", True): "REVISAR",
    ("ALTA EXPOSICIÓN", False): "ALTA PRIORIDAD",
}


def identificar_proceso(nombre_proceso: str) -> tuple[str, bool]:
    """Devuelve (descripción, conocido) para un nombre de proceso."""
    if nombre_proceso in PROCESOS_CONOCIDOS:
        return PROCESOS_CONOCIDOS[nombre_proceso], True
    return "Proceso no identificado", False


def calcular_riesgo(nivel_exposicion: str, conocido: bool) -> str:
    """Combina exposición e identificación como prioridad de revisión."""
    return MATRIZ_RIESGO.get((nivel_exposicion, conocido), "REVISAR")


def generar_recomendacion(nivel_exposicion: str, conocido: bool) -> str:
    """Genera una recomendación según exposición e identificación."""
    if nivel_exposicion == "BAJA":
        if conocido:
            return "Sin acción inmediata. El servicio está limitado a esta máquina."
        return "Revisar el proceso si no reconoces qué aplicación lo inició."

    if nivel_exposicion == "ALTA EXPOSICIÓN":
        if conocido:
            return (
                "Verificar que este servicio necesite estar disponible "
                "en todas las interfaces."
            )
        return (
            "Revisar con prioridad: el proceso no está identificado "
            "y escucha en todas las interfaces."
        )

    if conocido:
        return (
            "Verificar si este servicio debe estar disponible "
            "en la dirección indicada."
        )

    return (
        "Revisar el proceso y confirmar por qué está escuchando "
        "en esta dirección."
    )


def clasificar_exposicion(direccion: str) -> tuple[str, str]:
    """Clasifica el nivel de exposición según la dirección de escucha."""
    if direccion in ("127.0.0.1", "::1"):
        return "BAJA", "El servicio solo acepta conexiones desde esta misma máquina."

    if direccion in ("*", "0.0.0.0", "::"):
        return (
            "ALTA EXPOSICIÓN",
            "El servicio escucha en todas las interfaces, accesible potencialmente "
            "fuera de esta máquina.",
        )

    return (
        "REVISAR",
        f"El servicio está vinculado a la dirección {direccion}, "
        "alcanzable desde otros dispositivos en tu red local.",
    )


def analizar_servicios(servicios: list[dict]) -> list[dict]:
    """Enriquece cada servicio con exposición e identificación."""
    analizados = []

    for servicio in servicios:
        if "error" in servicio:
            analizados.append(servicio)
            continue

        nivel, motivo = clasificar_exposicion(servicio["direccion"])
        descripcion, conocido = identificar_proceso(servicio["proceso"])
        enriquecido = servicio.copy()
        enriquecido["nivel_exposicion"] = nivel
        enriquecido["motivo"] = motivo
        enriquecido["conocido"] = conocido
        enriquecido["descripcion"] = descripcion
        enriquecido["recomendacion"] = generar_recomendacion(nivel, conocido)
        analizados.append(enriquecido)

    return analizados


def generar_hallazgos(servicios: list[dict]) -> list[dict]:
    """Convierte servicios en hallazgos estructurados."""
    hallazgos = []

    for servicio in servicios:
        if "error" in servicio:
            continue

        nivel_exposicion, motivo = clasificar_exposicion(servicio["direccion"])
        descripcion, conocido = identificar_proceso(servicio["proceso"])
        riesgo = calcular_riesgo(nivel_exposicion, conocido)

        hallazgos.append(
            {
                "tipo": "servicio_local",
                "proceso": servicio["proceso"],
                "pid": servicio["pid"],
                "puerto": servicio["puerto"],
                "exposicion": nivel_exposicion,
                "descripcion": descripcion,
                "conocido": conocido,
                "motivo": motivo,
                "riesgo": riesgo,
            }
        )

    return hallazgos


def resumen_exposicion(servicios_analizados: list[dict]) -> dict:
    """Genera un conteo agregado por nivel de exposición."""
    resumen = {"BAJA": 0, "REVISAR": 0, "ALTA EXPOSICIÓN": 0}

    for servicio in servicios_analizados:
        nivel = servicio.get("nivel_exposicion")
        if nivel in resumen:
            resumen[nivel] += 1

    resumen["total"] = sum(valor for clave, valor in resumen.items() if clave != "total")
    return resumen