# import speech_recognition as sr

# # Creamos el reconocedor
# r = sr.Recognizer()

# # Elegimos el micrófono por defecto (integrado)
# with sr.Microphone() as source:
#     print("Calibrando ruido ambiente... (2 segundos)")
#     r.adjust_for_ambient_noise(source, duration=2)

#     print("Decí algo (tenés 5 segundos)...")
#     audio = r.listen(source, timeout=5, phrase_time_limit=5)

# print("Audio capturado. Ahora intento transcribir...")
