# from datetime import datetime
# import time

# # Estado global del sistema (luego lo usará la pantalla y la voz)
# estado = "INICIANDO"


#     #Devuelve la hora actual en formato HH:MM:SS
# def mostrar_hora():
#     now = datetime.now()
#     return now.strftime("%H:%M:%S")


# def main_loop():
#     #Loop principal del espejo.
#     #Este loop debe correr indefinidamente mientras el sistema esté encendido.
#     global estado

#     print("Espejo IA - sistema iniciado")
#     estado = "FUNCIONANDO"

#     contador = 0  # Contador de segundos

#     try:
#         while True:
#             # Obtener hora actual
#             hora = mostrar_hora()
#             print(f"[{estado}] Hora: {hora}")
#             contador += 1
#             # Cada 10 segundos mostrar mensaje de estabilidad
#             if contador == 10:
#                 print("Sistema estable")
#                 contador = 0  # Reiniciamos el contador
#             # Esperar 1 segundo antes de la próxima iteración
#             time.sleep(1)

#     except KeyboardInterrupt:
#         # Captura cuando el usuario presiona Ctrl + C
#         estado = "DETENIDO"
#         print(f"\nSistema {estado}")


# # Punto de entrada del programa
# if __name__ == "__main__":
#     main_loop()
