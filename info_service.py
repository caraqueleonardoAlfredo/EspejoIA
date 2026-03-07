import requests
import time
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------

CACHE_SECONDS = 300  # 5 minutos

LAT = -26.8241   # Tucuman
LON = -65.2226

# -----------------------------
# CACHE
# -----------------------------

_last_update = 0
_cached_data = {
    "clima": "--",
    "temperatura": "--",
    "humedad": "--",
    "dolar": "--"
}


# -----------------------------
# CLIMA
# -----------------------------

def obtener_clima():

    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}"
        "&current=temperature_2m,relative_humidity_2m,weather_code"
    )

    r = requests.get(url, timeout=5)
    data = r.json()

    current = data["current"]

    temperatura = f'{round(current["temperature_2m"])} °C'
    humedad = f'{current["relative_humidity_2m"]}%'

    clima = traducir_weather_code(current["weather_code"])

    return clima, temperatura, humedad


# -----------------------------
# DOLAR
# -----------------------------

def obtener_dolar():

    url = "https://dolarapi.com/v1/dolares/blue"

    r = requests.get(url, timeout=5)
    data = r.json()

    valor = data["venta"]

    return f"${valor}"


# -----------------------------
# TRADUCCION CLIMA
# -----------------------------

def traducir_weather_code(code):

    tabla = {
        0: "Despejado",
        1: "Mayormente despejado",
        2: "Parcialmente nublado",
        3: "Nublado",
        45: "Niebla",
        48: "Niebla",
        51: "Llovizna",
        53: "Llovizna",
        55: "Llovizna fuerte",
        61: "Lluvia",
        63: "Lluvia",
        65: "Lluvia fuerte",
        71: "Nieve",
        80: "Chubascos",
        95: "Tormenta"
    }

    return tabla.get(code, "Clima desconocido")


# -----------------------------
# FUNCION PRINCIPAL
# -----------------------------

def get_info_data():

    global _last_update
    global _cached_data

    ahora = time.time()

    # usar cache
    if ahora - _last_update < CACHE_SECONDS:
        return {
            "fecha_corta": datetime.now().strftime("%d/%m/%Y"),
            "clima": _cached_data["clima"],
            "temperatura": _cached_data["temperatura"],
            "humedad": _cached_data["humedad"],
            "dolar": _cached_data["dolar"],
            "mensaje_info": "Desliza la mano para cambiar de modo"
        }

    try:

        clima, temperatura, humedad = obtener_clima()
        dolar = obtener_dolar()

        _cached_data = {
            "clima": clima,
            "temperatura": temperatura,
            "humedad": humedad,
            "dolar": dolar
        }

        _last_update = ahora

    except Exception as e:

        print("Error actualizando INFO:", e)

    return {
        "fecha_corta": datetime.now().strftime("%d/%m/%Y"),
        "clima": _cached_data["clima"],
        "temperatura": _cached_data["temperatura"],
        "humedad": _cached_data["humedad"],
        "dolar": _cached_data["dolar"],
        "mensaje_info": "Desliza la mano para cambiar de modo"
    }