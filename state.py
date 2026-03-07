from dataclasses import dataclass, field
import time

VALID_MODES = {"INFO", "DOMOTICA", "IA"}


@dataclass
class MirrorState:
    mode: str = "INFO"
    status_text: str = "ESPERANDO PRESENCIA"
    last_phrase: str = "Desliza la mano para cambiar de modo"
    presence_detected: bool = False
    screen_on: bool = False
    last_change_ts: float = field(default_factory=time.time)

    def set_mode(self, new_mode: str):
        new_mode = (new_mode or "").upper()

        if new_mode not in VALID_MODES:
            raise ValueError(f"Modo invalido: {new_mode}. Validos: {sorted(VALID_MODES)}")

        self.mode = new_mode
        self.last_change_ts = time.time()


STATE = MirrorState()