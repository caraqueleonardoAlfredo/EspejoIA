from flask import Flask, render_template, jsonify, request
from datetime import datetime
from state import STATE
import time

app = Flask(__name__)

# Modos disponibles
MODOS = ["INFO", "DOMOTICA", "AI"]

# Modo actual del espejo
MODO = "INFO"

# Estado del sistema (lo vamos cambiando)
ESTADO = "FUNCIONANDO"

# Última frase reconocida (se muestra en pantalla)
ULTIMA_FRASE = ""


@app.route("/")
def home():
    """Pantalla principal del espejo"""
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    now = datetime.now().strftime("%H:%M:%S")
    return jsonify({
        "hora": now,
        "estado": ESTADO,
        "frase": ULTIMA_FRASE,
        "modo": MODO
    })



@app.route("/api/set_frase", methods=["POST"])
def set_frase():
    """
    Recibe JSON con:
      { "frase": "lo que dijiste", "estado": "..." (opcional) }
    y actualiza variables globales.
    """
    global ULTIMA_FRASE, ESTADO

    data = request.get_json(force=True)  # fuerza JSON si viene bien formado

    # Actualizamos frase si viene
    if "frase" in data:
        ULTIMA_FRASE = data["frase"]

    # Actualizamos estado si viene (opcional)
    if "estado" in data:
        ESTADO = data["estado"]

    return jsonify({"ok": True})

@app.route("/api/set_modo", methods=["POST"])
def set_modo():
    """
    Recibe JSON: { "modo": "INFO" | "DOMOTICA" | "AI" }
    """
    global MODO
    data = request.get_json(force=True)

    if "modo" in data and data["modo"] in MODOS:
        MODO = data["modo"]
        return jsonify({"ok": True, "modo": MODO})

    return jsonify({"ok": False, "error": "Modo inválido", "modos": MODOS}), 400


@app.route("/api/next_modo", methods=["POST"])
def next_modo():
    """
    Cambia el modo en ciclo: INFO -> DOMOTICA -> AI -> INFO
    """
    global MODO
    idx = MODOS.index(MODO)
    MODO = MODOS[(idx + 1) % len(MODOS)]
    return jsonify({"ok": True, "modo": MODO})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
