from flask import Flask, render_template, jsonify, request
from state import STATE
from mirror_controller import CONTROLLER
from info_service import get_info_data
from gpio_controller import start_gpio
from ia_audio_service import process_uploaded_audio

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


@app.route("/api/next_modo", methods=["POST"])
def next_modo():
    modo = CONTROLLER.next_mode()
    return jsonify({
        "ok": True,
        "modo": modo
    })


@app.route("/api/set_modo", methods=["POST"])
def set_modo():
    data = request.get_json(force=True)
    modo = CONTROLLER.set_mode(data.get("modo", "INFO"))

    return jsonify({
        "ok": True,
        "modo": modo
    })


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


@app.route("/api/screen_off", methods=["POST"])
def screen_off():
    CONTROLLER.set_presence(False)
    return jsonify({"ok": True})


@app.route("/api/ia/process_audio", methods=["POST"])
def ia_process_audio():
    if not STATE.screen_on or STATE.mode != "IA":
        return jsonify({
            "ok": False,
            "error": "El espejo no est� en modo IA.",
            "transcript": "",
            "response": ""
        }), 400

    if "audio" not in request.files:
        return jsonify({
            "ok": False,
            "error": "No se recibi� archivo de audio.",
            "transcript": "",
            "response": ""
        }), 400

    STATE.status_text = "PROCESANDO"
    STATE.last_phrase = "Procesando..."

    result = process_uploaded_audio(request.files["audio"])

    if result["ok"]:
        STATE.status_text = "IA"
        STATE.last_phrase = result["response"]
    else:
        STATE.status_text = "IA"
        STATE.last_phrase = result["error"]

    return jsonify(result)


if __name__ == "__main__":
    start_gpio()
    app.run(host="0.0.0.0", port=5000, debug=False)