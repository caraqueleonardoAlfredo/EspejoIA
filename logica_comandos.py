from datetime import datetime


def procesar_comando(texto, modo_actual):
    """
    Devuelve un dict:
    {
        "respuesta": str,
        "accion": "SET_MODO" | "NEXT_MODO" | None,
        "modo": "INFO" | "DOMOTICA" | "IA" | None
    }
    """
    texto = (texto or "").lower().strip()

    # ---- comandos de cambio de modo ----
    if "siguiente modo" in texto or "cambiar modo" in texto:
        return {"respuesta": "Cambiando de modo", "accion": "NEXT_MODO", "modo": None}

    if "modo domotica" in texto or "modo dom�tica" in texto:
        return {"respuesta": "Modo dom�tica activado", "accion": "SET_MODO", "modo": "DOMOTICA"}

    if "modo ia" in texto or "modo inteligencia artificial" in texto:
        return {"respuesta": "Modo IA activado", "accion": "SET_MODO", "modo": "IA"}

    if "modo info" in texto or "modo informaci�n" in texto:
        return {"respuesta": "Modo informaci�n activado", "accion": "SET_MODO", "modo": "INFO"}

    # ---- comandos normales ----
    if "hora" in texto:
        hora_actual = datetime.now().strftime("%H:%M")
        return {"respuesta": f"Son las {hora_actual}", "accion": None, "modo": None}

    if "estado" in texto:
        return {"respuesta": "Sistema funcionando correctamente", "accion": None, "modo": None}

    if "hola" in texto:
        return {"respuesta": "Hola Leo", "accion": None, "modo": None}

    # ---- comportamiento seg�n modo ----
    if modo_actual == "DOMOTICA":
        if "encende la luz" in texto or "encend� la luz" in texto:
            return {"respuesta": "Luz encendida", "accion": None, "modo": None}
        return {"respuesta": "Modo dom�tica activo", "accion": None, "modo": None}

    if modo_actual == "IA":
        return {"respuesta": f"Modo IA activo. Dijiste: {texto}", "accion": None, "modo": None}

    # INFO: si no es comando, lo muestra
    return {"respuesta": texto, "accion": None, "modo": None}