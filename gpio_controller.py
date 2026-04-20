import time
import threading
from gpiozero import Button
from mirror_controller import CONTROLLER

# -----------------------------
# CONFIG PINES
# -----------------------------
PIN_PRESENCIA = 17
PIN_GESTO_1 = 27
PIN_GESTO_2 = 22

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


def leer_gesto():
    s1 = sensor_gesto_1.is_pressed
    s2 = sensor_gesto_2.is_pressed

    print(f"[GPIO] Estado gesto -> G1={int(s1)} G2={int(s2)}")
    CONTROLLER.set_gesture_state(s1, s2)


# -----------------------------
# PRESENCIA
# -----------------------------
def on_presence():
    print("[GPIO] Presencia detectada")
    CONTROLLER.set_presence(True)


def off_presence():
    print("[GPIO] Presencia perdida")
    CONTROLLER.set_presence(False)


# -----------------------------
# GESTO
# -----------------------------
def on_gesture_change():
    print("[GPIO] Cambio en sensor de gesto")
    time.sleep(0.08)
    leer_gesto()


# -----------------------------
# START
# -----------------------------
def start_gpio():
    global _ultimo_estado_presencia
    global _ultimo_estado_gesto

    print("[GPIO] Iniciando control GPIO...")
    print(f"[GPIO] PIN_PRESENCIA = {PIN_PRESENCIA}")
    print(f"[GPIO] PIN_GESTO_1 = {PIN_GESTO_1}")
    print(f"[GPIO] PIN_GESTO_2 = {PIN_GESTO_2}")

    _ultimo_estado_presencia = sensor_presencia.is_pressed
    _ultimo_estado_gesto = (sensor_gesto_1.is_pressed, sensor_gesto_2.is_pressed)

    print(f"[GPIO] Estado inicial presencia -> {int(_ultimo_estado_presencia)}")
    CONTROLLER.set_presence(_ultimo_estado_presencia)

    print(
        f"[GPIO] Estado inicial gesto -> "
        f"G1={int(_ultimo_estado_gesto[0])} G2={int(_ultimo_estado_gesto[1])}"
    )
    CONTROLLER.set_gesture_state(_ultimo_estado_gesto[0], _ultimo_estado_gesto[1])


def keep_alive():
    global _ultimo_estado_presencia
    global _ultimo_estado_gesto

    gesto_candidato = None
    gesto_candidato_desde = 0
    tiempo_estable_gesto = 0.6

    while True:
        presencia = sensor_presencia.is_pressed
        gesto = (sensor_gesto_1.is_pressed, sensor_gesto_2.is_pressed)
        ahora = time.time()

        if presencia != _ultimo_estado_presencia:
            _ultimo_estado_presencia = presencia

            if presencia:
                on_presence()
            else:
                off_presence()

        if gesto != _ultimo_estado_gesto:
            if gesto != gesto_candidato:
                gesto_candidato = gesto
                gesto_candidato_desde = ahora

            if ahora - gesto_candidato_desde >= tiempo_estable_gesto:
                _ultimo_estado_gesto = gesto
                on_gesture_change()
                gesto_candidato = None

        else:
            gesto_candidato = None

        time.sleep(0.05)



thread = threading.Thread(target=keep_alive, daemon=True)
thread.start()
