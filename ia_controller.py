import threading
import time

from state import STATE
from voz_salida import hablar
from ia_simulada import responder
from voice_listener import escuchar, calibrar_microfono


class IAController:
    def __init__(self):
        self.last_mode = None
        self.thread_running = False
        self.session_id = 0

    def _session_activa(self, session_id_local: int) -> bool:
        return (
            self.thread_running
            and session_id_local == self.session_id
            and STATE.screen_on
            and STATE.mode == "IA"
        )

    def stop(self):
        self.session_id += 1
        self.thread_running = False

    def conversacion_loop(self, session_id_local: int):
        self.thread_running = True

        try:
            STATE.status_text = "PREPARANDO"
            STATE.last_phrase = "Preparando micr�fono..."
            calibrar_microfono()

            if not self._session_activa(session_id_local):
                return

            STATE.status_text = "IA"
            STATE.last_phrase = "Hola, �en qu� puedo ayudarte?"
            hablar("Hola, �en qu� puedo ayudarte?")

            if not self._session_activa(session_id_local):
                return

            time.sleep(0.4)

            while self._session_activa(session_id_local):
                STATE.status_text = "ESCUCHANDO"
                STATE.last_phrase = "Habl� ahora"
                time.sleep(0.4)

                if not self._session_activa(session_id_local):
                    break

                pregunta = escuchar()

                if not self._session_activa(session_id_local):
                    break

                if not pregunta:
                    STATE.status_text = "IA"
                    STATE.last_phrase = "No te entend�. Prob� de nuevo."
                    time.sleep(0.6)
                    continue

                STATE.status_text = "PROCESANDO"
                STATE.last_phrase = "Procesando..."
                time.sleep(0.2)

                if not self._session_activa(session_id_local):
                    break

                respuesta = responder(pregunta)

                STATE.status_text = "RESPONDIENDO"
                STATE.last_phrase = respuesta
                hablar(respuesta)

                if not self._session_activa(session_id_local):
                    break

                time.sleep(0.5)

            if STATE.mode == "IA" and STATE.screen_on:
                STATE.status_text = "IA"
                STATE.last_phrase = "Modo IA listo"

        except Exception as e:
            print("Error en IA:", e)
            STATE.status_text = "ERROR IA"
            STATE.last_phrase = "Ocurri� un error en el modo IA"

        finally:
            if session_id_local == self.session_id:
                self.thread_running = False

    def loop(self):
        while True:
            modo_actual = STATE.mode

            if modo_actual != "IA" or not STATE.screen_on:
                if self.last_mode == "IA":
                    self.stop()

            if STATE.screen_on and modo_actual == "IA":
                if self.last_mode != "IA":
                    self.stop()
                    self.thread_running = True
                    self.session_id += 1
                    session_id_local = self.session_id

                    hilo = threading.Thread(
                        target=self.conversacion_loop,
                        args=(session_id_local,),
                        daemon=True
                    )
                    hilo.start()

            self.last_mode = modo_actual
            time.sleep(0.15)


IA_CONTROLLER = IAController()


def start_ia():
    thread = threading.Thread(target=IA_CONTROLLER.loop, daemon=True)
    thread.start()