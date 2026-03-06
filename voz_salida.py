import asyncio
import os
import subprocess
import tempfile

import edge_tts

# Voz neural en espa�ol (Argentina)
VOZ = "es-AR-ElenaNeural"


async def _generar_mp3(texto: str, ruta_mp3: str) -> None:
    """Genera un MP3 con Edge TTS y lo guarda en ruta_mp3."""
    communicate = edge_tts.Communicate(texto, VOZ)
    await communicate.save(ruta_mp3)


def _reproducir_mp3_ffplay(ruta_mp3: str) -> None:
    """
    Reproduce un mp3 de forma robusta en Raspberry.
    Requiere: sudo apt install ffmpeg
    """
    subprocess.run(
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", ruta_mp3],
        check=False
    )


def hablar(texto: str) -> None:
    """
    1) Genera audio con Edge TTS (async)
    2) Reproduce el mp3 con ffplay
    3) Borra el archivo temporal
    """
    texto = (texto or "").strip()
    if not texto:
        return

    # Creamos archivo temporal �nico (evita conflictos si habl�s seguido)
    fd, ruta_mp3 = tempfile.mkstemp(prefix="tts_", suffix=".mp3")
    os.close(fd)

    try:
        asyncio.run(_generar_mp3(texto, ruta_mp3))
        _reproducir_mp3_ffplay(ruta_mp3)
    finally:
        try:
            os.remove(ruta_mp3)
        except Exception:
            pass