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
    """Enriquece cada servicio con su nivel de exposición y motivo."""
    analizados = []

    for servicio in servicios:
        if "error" in servicio:
            analizados.append(servicio)
            continue

        nivel, motivo = clasificar_exposicion(servicio["direccion"])
        enriquecido = servicio.copy()
        enriquecido["nivel_exposicion"] = nivel
        enriquecido["motivo"] = motivo
        analizados.append(enriquecido)

    return analizados


def resumen_exposicion(servicios_analizados: list[dict]) -> dict:
    """Genera un conteo agregado por nivel de exposición."""
    resumen = {"BAJA": 0, "REVISAR": 0, "ALTA EXPOSICIÓN": 0}

    for servicio in servicios_analizados:
        nivel = servicio.get("nivel_exposicion")
        if nivel in resumen:
            resumen[nivel] += 1

    resumen["total"] = sum(valor for clave, valor in resumen.items() if clave != "total")
    return resumen