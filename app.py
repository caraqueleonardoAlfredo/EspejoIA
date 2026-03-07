from flask import Flask, render_template, jsonify, request
from state import STATE, VALID_MODES
from info_service import get_info_data

app = Flask(__name__)

HOME_ASSISTANT_URL = "http://127.0.0.1:8123"


@app.route("/")
def home():
    return render_template("index.html")


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


@app.route("/api/info")
def api_info():
    return jsonify(get_info_data())


@app.route("/api/set_frase", methods=["POST"])
def set_frase():
    data = request.get_json(force=True)

    if "frase" in data:
        STATE.last_phrase = str(data["frase"])

    if "estado" in data:
        STATE.status_text = str(data["estado"])

    return jsonify({"ok": True})


@app.route("/api/set_modo", methods=["POST"])
def set_modo():
    data = request.get_json(force=True)
    nuevo_modo = str(data.get("modo", "")).upper()

    if nuevo_modo not in VALID_MODES:
        return jsonify({"ok": False, "error": "Modo invalido"}), 400

    STATE.set_mode(nuevo_modo)

    return jsonify({
        "ok": True,
        "modo": STATE.mode,
        "mostrar_ha": STATE.mode == "DOMOTICA"
    })


@app.route("/api/next_modo", methods=["POST"])
def next_modo():
    modos = ["INFO", "DOMOTICA", "IA"]
    idx = modos.index(STATE.mode)
    siguiente = modos[(idx + 1) % len(modos)]
    STATE.set_mode(siguiente)

    return jsonify({
        "ok": True,
        "modo": STATE.mode,
        "mostrar_ha": STATE.mode == "DOMOTICA"
    })


@app.route("/api/set_presence", methods=["POST"])
def set_presence():
    data = request.get_json(force=True)
    presence = bool(data.get("presence_detected", False))

    STATE.presence_detected = presence
    STATE.screen_on = presence

    if presence:
        STATE.set_mode("INFO")
        STATE.status_text = "FUNCIONANDO"
        if not STATE.last_phrase:
            STATE.last_phrase = "Desliza la mano para cambiar de modo"

    return jsonify({
        "ok": True,
        "presence_detected": STATE.presence_detected,
        "screen_on": STATE.screen_on,
        "modo": STATE.mode
    })


@app.route("/api/screen_off", methods=["POST"])
def screen_off():
    STATE.screen_on = False
    STATE.presence_detected = False

    return jsonify({
        "ok": True,
        "screen_on": STATE.screen_on
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)