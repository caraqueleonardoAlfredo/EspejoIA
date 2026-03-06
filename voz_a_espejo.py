import speech_recognition as sr
import requests

from logica_comandos import procesar_comando
from voz_salida import hablar

# URL del servidor local Flask
BASE_URL = "http://127.0.0.1:5000"


def set_estado(estado: str):
    """Actualiza solo el estado visible en pantalla."""
    try:
        requests.post(f"{BASE_URL}/api/set_frase", json={"estado": estado})
    except Exception:
        pass


def set_frase_y_estado(frase: str, estado: str = "FUNCIONANDO"):
    """Actualiza frase + estado en pantalla."""
    try:
        requests.post(
            f"{BASE_URL}/api/set_frase",
            json={"frase": frase, "estado": estado}
        )
    except Exception:
        pass


def get_modo_actual() -> str:
    """Lee el modo actual desde el backend."""
    try:
        status = requests.get(f"{BASE_URL}/api/status", timeout=2).json()
        return status.get("modo", "INFO")
    except Exception:
        return "INFO"


def ejecutar_accion(resultado: dict):
    """
    Ejecuta acciones de modo en el backend.
    resultado esperado:
      {"respuesta": str, "accion": "SET_MODO"|"NEXT_MODO"|None, "modo": str|None}
    """
    accion = resultado.get("accion")
    modo = resultado.get("modo")

    try:
        if accion == "NEXT_MODO":
            requests.post(f"{BASE_URL}/api/next_modo", timeout=2)

        elif accion == "SET_MODO" and modo:
            requests.post(f"{BASE_URL}/api/set_modo", json={"modo": modo}, timeout=2)

    except Exception:
        pass


def get_usb_mic_index():
    """Busca un microfono por nombre para usar el correcto siempre."""
    names = sr.Microphone.list_microphone_names()
    for i, name in enumerate(names):
        # Ajuste a un match mas seguro
        if "Logi USB Headset" in name or "USB" in name:
            return i
    return None


def main():
    r = sr.Recognizer()

    # 1) ESTADO: ESCUCHANDO
    set_estado("ESCUCHANDO...")

    mic_index = 2
    print("Mic index:", mic_index)

    # fallback: si no encontre por nombre, usa el default
    if mic_index is None:
        mic = sr.Microphone()
    else:
        mic = sr.Microphone(device_index=mic_index)

    with mic as source:
        print("Calibrando ruido ambiente... (2 segundos)")
        r.adjust_for_ambient_noise(source, duration=2)

        print("Deci algo (hasta 5 segundos)...")
        r.energy_threshold = 200  # sub� o bajamos despu�s seg�n RMS
        r.dynamic_energy_threshold = False
        r.pause_threshold = 0.8
        audio = r.listen(source, phrase_time_limit=6)

    # 2) ESTADO: TRANSCRIBIENDO
    set_estado("TRANSCRIBIENDO...")

    try:
        texto = r.recognize_google(audio, language="es-AR")
        print("Dijiste:", texto)

        modo_actual = get_modo_actual()
        print("Modo actual:", modo_actual)

        resultado = procesar_comando(texto, modo_actual)

        respuesta = (resultado.get("respuesta") or "").strip()
        if not respuesta:
            respuesta = "No entendo lo que dijiste"

        ejecutar_accion(resultado)

        # 3) HABLA
        hablar(respuesta)

        # 4) MUESTRA
        set_frase_y_estado(respuesta, "FUNCIONANDO")

        print("Respuesta enviada y hablada ?")

    except sr.UnknownValueError:
        error_msg = "No entendi lo que dijiste"
        hablar(error_msg)
        set_frase_y_estado(error_msg, "FUNCIONANDO")
        print(error_msg)

    except sr.RequestError as e:
        error_msg = "Error de conexion con el reconocimiento de voz"
        hablar(error_msg)
        set_frase_y_estado(error_msg, "FUNCIONANDO")
        print("Error STT:", e)


if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            set_estado("DETENIDO")
            break
        except Exception as e:
            print("Error inesperado:", e)
            set_frase_y_estado("Error inesperado", "FUNCIONANDO")