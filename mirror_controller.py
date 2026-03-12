from state import STATE
import time

MODOS = ["INFO", "DOMOTICA", "IA"]


class MirrorController:
    def __init__(self):
        self.last_gesture_change_time = 0
        self.gesture_cooldown = 0.25
        self.last_gesture_state = None

    def _apply_mode_ui(self, mode: str):
        mode = mode.upper()
        STATE.set_mode(mode)

        if mode == "INFO":
            STATE.status_text = "FUNCIONANDO"
            STATE.last_phrase = "Desliza la mano para cambiar de modo"

        elif mode == "DOMOTICA":
            STATE.status_text = "DOMOTICA"
            STATE.last_phrase = "Panel dom�tico activo"

        elif mode == "IA":
            STATE.status_text = "IA"
            STATE.last_phrase = "Manten� presionado el bot�n para hablar"

    def set_presence(self, detected: bool):
        STATE.presence_detected = detected

        if detected:
            STATE.screen_on = True
            self._apply_mode_ui("INFO")
        else:
            STATE.screen_on = False
            STATE.status_text = "ESPERANDO PRESENCIA"
            STATE.last_phrase = "Desliza la mano para cambiar de modo"

        print(
            f"[MIRROR] Presencia={STATE.presence_detected} | "
            f"Pantalla={STATE.screen_on} | "
            f"Modo={STATE.mode}"
        )

    def set_gesture_state(self, s1: bool, s2: bool):
        """
        Nueva l�gica del sensor de gesto:
        0 0 -> INFO
        0 1 -> DOMOTICA
        1 1 -> IA
        1 0 -> ignorado (estado intermedio)
        """
        now = time.time()
        nuevo_estado = (int(s1), int(s2))

        print(f"[MIRROR] Gesto recibido -> G1={nuevo_estado[0]} G2={nuevo_estado[1]}")

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

        if nuevo_estado == (0, 0):
            self._apply_mode_ui("INFO")

        elif nuevo_estado == (0, 1):
            self._apply_mode_ui("DOMOTICA")

        elif nuevo_estado == (1, 1):
            self._apply_mode_ui("IA")

        elif nuevo_estado == (1, 0):
            print("[MIRROR] Estado intermedio 1,0 -> se mantiene el modo actual")
            return STATE.mode

        print(f"[MIRROR] Modo actual -> {STATE.mode}")
        return STATE.mode

    def next_mode(self):
        idx = MODOS.index(STATE.mode)
        next_mode = MODOS[(idx + 1) % len(MODOS)]
        self._apply_mode_ui(next_mode)
        return STATE.mode

    def set_mode(self, mode: str):
        mode = (mode or "INFO").upper()
        if mode in MODOS:
            self._apply_mode_ui(mode)
        return STATE.mode


CONTROLLER = MirrorController()