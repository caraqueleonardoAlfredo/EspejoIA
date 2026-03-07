from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# CONFIGURACI�N
# -----------------------------
MODOS = ["INFO", "DOMOTICA", "AI"]
HOME_ASSISTANT_URL = "http://127.0.0.1:8123"

# -----------------------------
# ESTADO GLOBAL
# -----------------------------
modo_actual = "INFO"
estado_actual = "FUNCIONANDO"
frase_actual = "Decime algo..."

# -----------------------------
# RUTAS
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    hora_actual = datetime.now().strftime("%H:%M:%S")

    return jsonify({
        "hora": hora_actual,
        "estado": estado_actual,
        "frase": frase_actual,
        "modo": modo_actual,
        "ha_url": HOME_ASSISTANT_URL,
        "mostrar_ha": modo_actual == "DOMOTICA"
    })


@app.route("/api/set_frase", methods=["POST"])
def set_frase():
    global frase_actual, estado_actual

    data = request.get_json(force=True)

    if "frase" in data:
        frase_actual = data["frase"]

    if "estado" in data:
        estado_actual = data["estado"]

    return jsonify({"ok": True})


@app.route("/api/set_modo", methods=["POST"])
def set_modo():
    global modo_actual

    data = request.get_json(force=True)
    nuevo_modo = data.get("modo")

    if nuevo_modo in MODOS:
        modo_actual = nuevo_modo
        return jsonify({
            "ok": True,
            "modo": modo_actual,
            "mostrar_ha": modo_actual == "DOMOTICA"
        })

    return jsonify({
        "ok": False,
        "error": "Modo inv�lido"
    }), 400


@app.route("/api/next_modo", methods=["POST"])
def next_modo():
    global modo_actual

    idx = MODOS.index(modo_actual)
    modo_actual = MODOS[(idx + 1) % len(MODOS)]

    return jsonify({
        "ok": True,
        "modo": modo_actual,
        "mostrar_ha": modo_actual == "DOMOTICA"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)