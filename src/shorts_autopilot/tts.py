from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path


async def _edge_save(text: str, voice: str, destination: Path) -> None:
    import edge_tts

    communicator = edge_tts.Communicate(text=text, voice=voice, rate="+8%")
    await communicator.save(str(destination))


def synthesize(text: str, voice: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        asyncio.run(_edge_save(text, voice, destination))
        return destination
    except Exception:
        if sys.platform != "win32":
            raise

    wav = destination.with_suffix(".wav")
    escaped_text = text.replace("'", "''")
    escaped_path = str(wav).replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.Rate=2; "
        f"$s.SetOutputToWaveFile('{escaped_path}'); $s.Speak('{escaped_text}'); "
        "$s.Dispose()"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=True,
    )
    return wav
