import speech_recognition as sr

def get_usb_mic_index():
    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        if "Logi USB Headset" in name or "USB" in name:
            return i
    return None

r = sr.Recognizer()
mic_index = get_usb_mic_index()
print("Mic index:", mic_index)
print("Mic name:", sr.Microphone.list_microphone_names()[mic_index] if mic_index is not None else "None")

with sr.Microphone(device_index=mic_index) as source:
    r.adjust_for_ambient_noise(source, duration=1)
    print("Dec� algo...")
    audio = r.listen(source, timeout=5, phrase_time_limit=5)

print("Procesando...")
print(r.recognize_google(audio, language="es-AR"))


