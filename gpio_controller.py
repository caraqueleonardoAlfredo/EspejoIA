import time
import threading
from gpiozero import Button
from mirror_controller import CONTROLLER
from presence_timeout import PresenceTimeout, get_screen_off_delay_seconds

# -----------------------------
# CONFIG PINES
# -----------------------------
PIN_PRESENCIA = 17
PIN_GESTO_1 = 27
PIN_GESTO_2 = 22

# -----------------------------
# AJUSTES
# -----------------------------
# Tiempo desde la ultima deteccion antes de apagar la pantalla.
SCREEN_OFF_DELAY_SECONDS = get_screen_off_delay_seconds()

# Cuanto tiempo debe mantenerse estable un gesto
# antes de aplicarlo.
GESTURE_STABLE_SECONDS = 0.35

# -----------------------------
# ENTRADAS
# Sensores activos en bajo con pull-up interno:
# reposo = False / 0
# activo = True / 1
# -----------------------------
sensor_presencia = Button(PIN_PRESENCIA, pull_up=True, bounce_time=0.08)
sensor_gesto_1 = Button(PIN_GESTO_1, pull_up=True, bounce_time=0.05)
sensor_gesto_2 = Button(PIN_GESTO_2, pull_up=True, bounce_time=0.05)

_ultimo_estado_presencia = None
_ultimo_estado_gesto = None
_presence_timeout = PresenceTimeout(SCREEN_OFF_DELAY_SECONDS)


def leer_gesto():
    s1 = sensor_gesto_1.is_pressed
    s2 = sensor_gesto_2.is_pressed
    print(f"[GPIO] Estado gesto -> G1={int(s1)} G2={int(s2)}")
    CONTROLLER.set_gesture_state(s1, s2)


def on_presence():
    print("[GPIO] Presencia detectada")
    CONTROLLER.set_presence(True)


def off_presence():
    print("[GPIO] Presencia perdida")
    CONTROLLER.set_presence(False)


def on_gesture_change():
    print("[GPIO] Cambio en sensor de gesto")
    leer_gesto()


def start_gpio():
    global _ultimo_estado_presencia
    global _ultimo_estado_gesto

    print("[GPIO] Iniciando control GPIO...")
    print(f"[GPIO] PIN_PRESENCIA = {PIN_PRESENCIA}")
    print(f"[GPIO] PIN_GESTO_1 = {PIN_GESTO_1}")
    print(f"[GPIO] PIN_GESTO_2 = {PIN_GESTO_2}")
    print(f"[GPIO] SCREEN_OFF_DELAY_SECONDS = {SCREEN_OFF_DELAY_SECONDS:g}")

    _ultimo_estado_presencia = sensor_presencia.is_pressed
    _ultimo_estado_gesto = (sensor_gesto_1.is_pressed, sensor_gesto_2.is_pressed)

    if _ultimo_estado_presencia:
        _presence_timeout.detected(time.time())

    print(f"[GPIO] Estado inicial presencia -> {int(_ultimo_estado_presencia)}")
    CONTROLLER.set_presence(_ultimo_estado_presencia)

    print(
        f"[GPIO] Estado inicial gesto -> "
        f"G1={int(_ultimo_estado_gesto[0])} G2={int(_ultimo_estado_gesto[1])}"
    )

    # Solo aplicar gesto inicial si la pantalla esta encendida.
    if _ultimo_estado_presencia:
        CONTROLLER.set_gesture_state(_ultimo_estado_gesto[0], _ultimo_estado_gesto[1])


def keep_alive():
    global _ultimo_estado_presencia
    global _ultimo_estado_gesto

    gesto_candidato = None
    gesto_candidato_desde = 0.0

    while True:
        ahora = time.time()
        presencia = sensor_presencia.is_pressed
        gesto = (sensor_gesto_1.is_pressed, sensor_gesto_2.is_pressed)

        # -----------------------------
        # PRESENCIA CON HOLD
        # -----------------------------
        if presencia:
            # Cada lectura positiva renueva el plazo desde la ultima deteccion.
            _presence_timeout.detected(ahora)

            if _ultimo_estado_presencia is not True:
                _ultimo_estado_presencia = True
                on_presence()

        else:
            if _ultimo_estado_presencia is True and _presence_timeout.has_expired(ahora):
                _ultimo_estado_presencia = False
                off_presence()

        # -----------------------------
        # GESTO CON ESTABILIZACION
        # -----------------------------
        if gesto != _ultimo_estado_gesto:
            if gesto != gesto_candidato:
                gesto_candidato = gesto
                gesto_candidato_desde = ahora

            if ahora - gesto_candidato_desde >= GESTURE_STABLE_SECONDS:
                _ultimo_estado_gesto = gesto
                on_gesture_change()
                gesto_candidato = None

        else:
            gesto_candidato = None

        time.sleep(0.05)


thread = threading.Thread(target=keep_alive, daemon=True)
thread.start()
