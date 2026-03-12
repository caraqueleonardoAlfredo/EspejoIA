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
# pull_up=False:
# reposo = 0
# se�al a 3.3V = 1
# -----------------------------
sensor_presencia = Button(PIN_PRESENCIA, pull_up=True, bounce_time=0.08)
sensor_gesto_1 = Button(PIN_GESTO_1, pull_up=True, bounce_time=0.05)
sensor_gesto_2 = Button(PIN_GESTO_2, pull_up=True, bounce_time=0.05)


def leer_gesto():
    s1 = sensor_gesto_1.is_pressed
    s2 = sensor_gesto_2.is_pressed
    print(f"[GPIO] Estado gesto -> G1={int(s1)} G2={int(s2)}")
    CONTROLLER.set_gesture_state(s1, s2)


# -----------------------------
# CALLBACKS PRESENCIA
# -----------------------------
def on_presence():
    print("[GPIO] Presencia detectada")
    CONTROLLER.set_presence(True)


def off_presence():
    print("[GPIO] Presencia perdida")
    CONTROLLER.set_presence(False)


# -----------------------------
# CALLBACKS GESTO
# cualquier cambio en cualquiera
# de las dos l�neas vuelve a leer
# el estado combinado
# -----------------------------
def on_gesture_change():
    print("[GPIO] Cambio en sensor de gesto")
    leer_gesto()


# -----------------------------
# START
# -----------------------------
def start_gpio():
    print("[GPIO] Iniciando control GPIO...")
    print(f"[GPIO] PIN_PRESENCIA = {PIN_PRESENCIA}")
    print(f"[GPIO] PIN_GESTO_1 = {PIN_GESTO_1}")
    print(f"[GPIO] PIN_GESTO_2 = {PIN_GESTO_2}")

    # presencia
    sensor_presencia.when_pressed = on_presence
    sensor_presencia.when_released = off_presence

    # gesto 1
    sensor_gesto_1.when_pressed = on_gesture_change
    sensor_gesto_1.when_released = on_gesture_change

    # gesto 2
    sensor_gesto_2.when_pressed = on_gesture_change
    sensor_gesto_2.when_released = on_gesture_change

    # leer estados iniciales
    print(f"[GPIO] Estado inicial presencia -> {int(sensor_presencia.is_pressed)}")
    leer_gesto()


def keep_alive():
    while True:
        time.sleep(1)


thread = threading.Thread(target=keep_alive, daemon=True)
thread.start()