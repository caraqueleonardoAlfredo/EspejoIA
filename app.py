from flask import Flask, render_template, jsonify, request
from state import STATE
from mirror_controller import CONTROLLER
from info_service import get_info_data

app = Flask(__name__)

HOME_ASSISTANT_URL = "http://127.0.0.1:8123"


@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# STATUS
# -----------------------------
@app.route("/api/status")
def api_status():

    return jsonify({
        "estado": STATE.status_text,
        "frase": STATE.last_phrase,
        "modo": STATE.mode,
        "ha_url": HOME_ASSISTANT_URL,
        "mostrar_ha": STATE.mode == "DOMOTICA",
        "screen_on": STATE.screen_on,
        "presence_detected": STATE.presence_detected
    })


# -----------------------------
# INFO
# -----------------------------
@app.route("/api/info")
def api_info():
    return jsonify(get_info_data())


# -----------------------------
# CAMBIO DE MODO
# -----------------------------
@app.route("/api/next_modo", methods=["POST"])
def next_modo():

    modo = CONTROLLER.next_mode()

    return jsonify({
        "ok": True,
        "modo": modo
    })


# -----------------------------
# SET MODO
# -----------------------------
@app.route("/api/set_modo", methods=["POST"])
def set_modo():

    data = request.get_json(force=True)

    modo = CONTROLLER.set_mode(data.get("modo", "INFO"))

    return jsonify({
        "ok": True,
        "modo": modo
    })


# -----------------------------
# PRESENCIA
# -----------------------------
@app.route("/api/set_presence", methods=["POST"])
def set_presence():

    data = request.get_json(force=True)

    detected = bool(data.get("presence_detected", False))

    CONTROLLER.set_presence(detected)

    return jsonify({
        "ok": True,
        "presence_detected": STATE.presence_detected,
        "screen_on": STATE.screen_on,
        "modo": STATE.mode
    })


# -----------------------------
# APAGAR PANTALLA
# -----------------------------
@app.route("/api/screen_off", methods=["POST"])
def screen_off():

    CONTROLLER.set_presence(False)

    return jsonify({
        "ok": True
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)