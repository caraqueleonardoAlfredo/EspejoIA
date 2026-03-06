from datetime import datetime

def procesar_comando(texto, modo_actual):
    """
    Devuelve un dict:
      {
        "respuesta": str,
        "accion": "SET_MODO" | "NEXT_MODO" | None,
        "modo": "INFO" | "DOMOTICA" | "AI" | None
      }
    """
    texto = texto.lower().strip()

    # ---- comandos de modo (simulan gesto) ----
    if "siguiente modo" in texto or "cambiar modo" in texto:
        return {"respuesta": "Cambiando de modo", "accion": "NEXT_MODO", "modo": None}

    if "modo domotica" in texto or "modo domótica" in texto:
        return {"respuesta": "Modo domótica activado", "accion": "SET_MODO", "modo": "DOMOTICA"}

    if "modo ai" in texto or "modo dianuby" in texto:
        return {"respuesta": "Modo Dianuby AI activado", "accion": "SET_MODO", "modo": "AI"}

    if "modo info" in texto or "modo información" in texto:
        return {"respuesta": "Modo información activado", "accion": "SET_MODO", "modo": "INFO"}

    # ---- comandos normales ----
    if "hora" in texto:
        hora_actual = datetime.now().strftime("%H:%M")
        return {"respuesta": f"Son las {hora_actual}", "accion": None, "modo": None}

    if "estado" in texto:
        return {"respuesta": "Sistema funcionando correctamente", "accion": None, "modo": None}

    if "hola" in texto:
        return {"respuesta": "Hola Leo 👋", "accion": None, "modo": None}

    # ---- comportamiento según modo (por ahora simple) ----
    if modo_actual == "DOMOTICA":
        # placeholder: más adelante esto llamará a domotica.py
        if "encende la luz" in texto or "encendé la luz" in texto:
            return {"respuesta": "Luz encendida", "accion": None, "modo": None}
        return {"respuesta": "Decí: encendé la luz", "accion": None, "modo": None}

    if modo_actual == "AI":
        # por ahora sin ChatGPT: devolvemos lo que dijo
        return {"respuesta": f"Estoy en modo AI. Dijiste: {texto}", "accion": None, "modo": None}

    # INFO: si no es comando, lo muestra
    return {"respuesta": texto, "accion": None, "modo": None}
