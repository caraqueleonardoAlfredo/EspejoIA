import datetime
import unicodedata


def normalizar(texto: str) -> str:
    texto = (texto or "").lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto


def responder(pregunta: str) -> str:
    p = normalizar(pregunta)

    if not p:
        return "No escuche ninguna pregunta."

    if "hora" in p:
        ahora = datetime.datetime.now().strftime("%H:%M")
        return f"Son las {ahora}"

    if "clima" in p or "tiempo" in p:
        return "Puedes ver el clima actual en el modo informacion."

    if "dolar" in p:
        return "Puedes ver la cotizacion del dolar en el modo informacion."

    if "quien eres" in p or "como te llamas" in p:
        return "Soy Dianuby Mirror, un espejo inteligente interactivo."

    if "que puedes hacer" in p or "para que sirves" in p:
        return "Puedo mostrar informacion, acceder a domotica y responder preguntas por voz."

    if "domotica" in p:
        return "Para controlar dispositivos, cambia al modo domotica."

    if p == "hola" or "hola " in p:
        return "Hola Leo, en que puedo ayudarte."

    if "que es dianuby" in p or "que es dianubi" in p or "que es este espejo" in p:
        return "Dianuby es un proyecto de espejo inteligente con informacion, domotica e inteligencia artificial."

    if "informacion" in p or "modo informacion" in p:
        return "En el modo informacion puedes ver clima, temperatura, humedad y dolar."

    return "Todavia estoy en modo de prueba, pero pronto podre responder mucho mas."