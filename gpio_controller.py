import time
import threading

from gpiozero import Button

from mirror_controller import CONTROLLER


# -----------------------------
# CONFIG PINES
# -----------------------------
PIN_PRESENCIA = 17
PIN_GESTO = 27


# -----------------------------
# ENTRADAS
# -----------------------------
# pull_up=False:
# - reposo = 0
# - se�al externa a 3.3V = 1
sensor_presencia = Button(PIN_PRESENCIA, pull_up=False, bounce_time=0.05)
sensor_gesto = Button(PIN_GESTO, pull_up=False, bounce_time=0.05)


# -----------------------------
# CALLBACKS
# -----------------------------
def on_presence():
    CONTROLLER.set_presence(True)


def off_presence():
    CONTROLLER.set_presence(False)


def on_gesture():
    CONTROLLER.next_mode()


# -----------------------------
# START
# -----------------------------
def start_gpio():
    sensor_presencia.when_pressed = on_presence
    sensor_presencia.when_released = off_presence
    sensor_gesto.when_pressed = on_gesture

    # Dejamos un hilo liviano solo para mantener referencia viva
    def keep_alive():
        while True:
            time.sleep(1)

    thread = threading.Thread(target=keep_alive, daemon=True)
    thread.start()