from state import STATE
import time


MODOS = ["INFO", "DOMOTICA", "IA"]


class MirrorController:

    def __init__(self):
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0  # segundos


    # -----------------------------
    # PRESENCIA
    # -----------------------------
    def set_presence(self, detected: bool):

        STATE.presence_detected = detected

        if detected:
            STATE.screen_on = True
            STATE.set_mode("INFO")
            STATE.status_text = "FUNCIONANDO"
            STATE.last_phrase = "Desliza la mano para cambiar de modo"

        else:
            STATE.screen_on = False


    # -----------------------------
    # CAMBIO DE MODO
    # -----------------------------
    def next_mode(self):

        now = time.time()

        if now - self.last_gesture_time < self.gesture_cooldown:
            return STATE.mode

        self.last_gesture_time = now

        idx = MODOS.index(STATE.mode)
        next_mode = MODOS[(idx + 1) % len(MODOS)]

        STATE.set_mode(next_mode)

        return STATE.mode


    # -----------------------------
    # MODO DIRECTO
    # -----------------------------
    def set_mode(self, mode: str):

        mode = mode.upper()

        if mode in MODOS:
            STATE.set_mode(mode)

        return STATE.mode


# instancia global
CONTROLLER = MirrorController()