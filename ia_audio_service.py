import os
import tempfile
import subprocess
import speech_recognition as sr

from ia_simulada import responder
from voz_salida import hablar


def process_uploaded_audio(file_storage):
    if not file_storage:
        return {
            "ok": False,
            "error": "No se recibi� audio.",
            "transcript": "",
            "response": ""
        }

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input_audio.webm")
            wav_path = os.path.join(tmpdir, "audio.wav")

            file_storage.save(input_path)

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i", input_path,
                    "-ac", "1",
                    "-ar", "16000",
                    wav_path
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )

            recognizer = sr.Recognizer()

            with sr.AudioFile(wav_path) as source:
                audio = recognizer.record(source)

            try:
                transcript = recognizer.recognize_google(audio, language="es-AR").strip()
            except sr.UnknownValueError:
                return {
                    "ok": False,
                    "error": "No pude entender el audio.",
                    "transcript": "",
                    "response": ""
                }

            response = responder(transcript)

            hablar(response)

            return {
                "ok": True,
                "error": "",
                "transcript": transcript,
                "response": response
            }

    except FileNotFoundError:
        return {
            "ok": False,
            "error": "No se encontr� ffmpeg instalado en el sistema.",
            "transcript": "",
            "response": ""
        }

    except sr.RequestError as e:
        return {
            "ok": False,
            "error": f"Error del servicio de reconocimiento: {e}",
            "transcript": "",
            "response": ""
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Error procesando audio: {e}",
            "transcript": "",
            "response": ""
        }