from datetime import datetime


def get_info_data():
    """
    Por ahora devuelve datos simulados para cerrar el modo INFO.
    Mas adelante lo conectamos a APIs reales.
    """
    return {
        "fecha_corta": datetime.now().strftime("%d/%m/%Y"),
        "clima": "Parcialmente nublado",
        "temperatura": "24 C",
        "humedad": "68%",
        "dolar": "$1285",
        "mensaje_info": "Desliza la mano para cambiar de modo"
    }