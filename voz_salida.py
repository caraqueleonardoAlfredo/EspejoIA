import asyncio
import os
import subprocess
import tempfile
from pathlib import Path

import edge_tts

VOICE = "es-AR-ElenaNeural"


async def _generar_tts_async(texto: str, output_file: str) -> None:
    communicate = edge_tts.Communicate(texto, VOICE)
    await communicate.save(output_file)


def hablar_texto(texto: str) -> bool:
    """
    Genera un MP3 con edge-tts y lo reproduce con ffplay.
    Devuelve True si todo sali� bien, False si hubo error.
    """
    texto = (texto or "").strip()
    if not texto:
        print("[voz_salida] Texto vac�o, no se reproduce nada.")
        return False

    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = tmp.name

        asyncio.run(_generar_tts_async(texto, tmp_path))

        cmd = [
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-loglevel",
            "quiet",
            tmp_path,
        ]

        subprocess.run(cmd, check=True)
        return True

    except Exception as e:
        print(f"[voz_salida] Error reproduciendo audio: {e}")
        return False

    finally:
        if tmp_path and Path(tmp_path).exists():
            try:
                os.remove(tmp_path)
            except Exception:
                pass