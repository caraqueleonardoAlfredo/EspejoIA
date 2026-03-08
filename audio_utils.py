import subprocess


def beep():
    try:
        subprocess.run(
            [
                "play",
                "-n",
                "synth",
                "0.12",
                "sin",
                "880",
                "fade",
                "0.01",
                "0.12",
                "0.01"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print("Error generando beep:", e)