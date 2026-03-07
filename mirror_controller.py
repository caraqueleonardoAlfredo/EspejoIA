from state import STATE
import time


MODOS = ["INFO", "DOMOTICA", "IA"]


class MirrorController:
    def __init__(self):
        self.last_gesture_change_time = 0
        self.gesture_cooldown = 0.25
        self.last_gesture_state = None

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
            STATE.status_text = "ESPERANDO PRESENCIA"

    # -----------------------------
    # GESTO POR DOS ENTRADAS
    # s1 y s2 son bool
    # 00 -> INFO
    # 10 -> DOMOTICA
    # 01 -> IA
    # 11 -> INFO
    # -----------------------------
    def set_gesture_state(self, s1: bool, s2: bool):
        now = time.time()
        nuevo_estado = (int(s1), int(s2))

        if not STATE.screen_on:
            self.last_gesture_state = nuevo_estado
            return STATE.mode

        if self.last_gesture_state == nuevo_estado:
            return STATE.mode

        if now - self.last_gesture_change_time < self.gesture_cooldown:
            self.last_gesture_state = nuevo_estado
            return STATE.mode

        self.last_gesture_state = nuevo_estado
        self.last_gesture_change_time = now

        if nuevo_estado == (1, 0):
            STATE.set_mode("DOMOTICA")
        elif nuevo_estado == (0, 1):
            STATE.set_mode("IA")
        elif nuevo_estado == (1, 1):
            STATE.set_mode("INFO")
        elif nuevo_estado == (0, 0):
            STATE.set_mode("INFO")

        return STATE.mode

    # -----------------------------
    # CAMBIO DE MODO MANUAL
    # -----------------------------
    def next_mode(self):
        idx = MODOS.index(STATE.mode)
        next_mode = MODOS[(idx + 1) % len(MODOS)]
        STATE.set_mode(next_mode)
        return STATE.mode

    def set_mode(self, mode: str):
        mode = mode.upper()

        if mode in MODOS:
            STATE.set_mode(mode)

        return STATE.mode


CONTROLLER = MirrorController()