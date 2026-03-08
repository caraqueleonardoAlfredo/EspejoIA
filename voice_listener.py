import speech_recognition as sr
from audio_utils import beep
import time


PREFERRED_MIC_KEYWORDS = [
    "logi",
    "logitech",
    "usb",
    "headset",
    "mic"
]

recognizer = sr.Recognizer()
recognizer.energy_threshold = 200
recognizer.dynamic_energy_threshold = False
recognizer.pause_threshold = 0.7

_calibrado = False
_mic_index = None
_mic_name = None


def resolver_microfono():
    global _mic_index, _mic_name

    nombres = sr.Microphone.list_microphone_names()

    print("\n--- MICROFONOS DETECTADOS ---")
    for i, nombre in enumerate(nombres):
        print(f"[{i}] {nombre}")
    print("-----------------------------\n")

    if not nombres:
        raise RuntimeError("No se detect� ning�n micr�fono.")

    for i, nombre in enumerate(nombres):
        nombre_lower = nombre.lower()
        if any(k in nombre_lower for k in PREFERRED_MIC_KEYWORDS):
            _mic_index = i
            _mic_name = nombre
            print(f"Micr�fono seleccionado: [{_mic_index}] {_mic_name}")
            return

    _mic_index = 0
    _mic_name = nombres[0]
    print(f"Micr�fono fallback: [{_mic_index}] {_mic_name}")


def calibrar_microfono():
    global _calibrado

    if _calibrado:
        return

    if _mic_index is None:
        resolver_microfono()

    print(f"Calibrando ruido ambiente... (1 segundo) [{_mic_index}] {_mic_name}")

    with sr.Microphone(device_index=_mic_index) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    _calibrado = True
    print("Micr�fono calibrado.")


def escuchar() -> str:
    global _calibrado, _mic_index, _mic_name

    try:
        if _mic_index is None:
            resolver_microfono()

        if not _calibrado:
            calibrar_microfono()

        print(f"Beep -> habl� ahora [{_mic_index}] {_mic_name}")

        beep()

        # MUY IMPORTANTE
        # damos tiempo a que el dispositivo de audio se libere
        time.sleep(0.45)

        with sr.Microphone(device_index=_mic_index) as source:

            # escuchamos inmediatamente
            audio = recognizer.listen(
                source,
                timeout=4,
                phrase_time_limit=4
            )

        texto = recognizer.recognize_google(audio, language="es-AR")
        texto = (texto or "").strip()

        print("Dijiste:", texto)
        return texto

    except sr.WaitTimeoutError:
        print("No detect� voz a tiempo.")
        return ""

    except sr.UnknownValueError:
        print("No se entendi� el audio.")
        return ""

    except sr.RequestError as e:
        print("Error del servicio de reconocimiento:", e)
        return ""

    except OSError as e:
        print("Error de dispositivo de audio:", e)
        _calibrado = False
        _mic_index = None
        _mic_name = None
        return ""

    except Exception as e:
        print("Error escuchando:", e)
        return ""