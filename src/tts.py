import os
import tempfile
from hashlib import sha256
from piper import PiperVoice
import wave
import subprocess
import asyncio

TTS_cache_dir = "tts_cache"
os.makedirs(TTS_cache_dir, exist_ok=True)

voice_model_path = "models/en_US-hfc_female-medium.onnx"
voice_config_path = "models/en_US-hfc_female-medium.onnx.json"

voice = PiperVoice.load(voice_model_path, config_path=voice_config_path)

# Tracking the process for interruptions
current_tts_process = None
interrupt_tts = False

async def speak(text: str, cacheable=True):
    global current_tts_process, interrupt_tts

    if interrupt_tts:
        return

    if voice is None:
        print("Voice model not loaded correctly")
        return

    if cacheable:
        key = sha256(text.encode()).hexdigest()
        filepath = os.path.join(TTS_cache_dir, key + ".wav")
        if not os.path.exists(filepath):
            with wave.open(filepath, "wb") as wav_file:
                voice.synthesize(text, wav_file)
        await run_ffplay(filepath)

    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
            with wave.open(fp, "wb") as wav_file:
                voice.synthesize(text, wav_file)
            await run_ffplay(fp.name)
            os.unlink(fp.name)

async def run_ffplay(path: str):
    global current_tts_process, interrupt_tts

    if interrupt_tts:
        return

    current_tts_process = await asyncio.create_subprocess_exec("ffplay", "-nodisp", "-autoexit", path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        await current_tts_process.wait()
    except asyncio.CancelledError:
        if current_tts_process and current_tts_process.returncode is None:
            current_tts_process.terminate()
            try:
                await asyncio.wait_for(current_tts_process.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                current_tts_process.kill()
                await current_tts_process.wait()
        raise
    finally:
        current_tts_process = None

def interrupt_current_tts():
    global current_tts_process, interrupt_tts
    interrupt_tts = True
    if current_tts_process and current_tts_process.returncode is None:
        current_tts_process.terminate()

def reset_tts_interrupt():
    global interrupt_tts
    interrupt_tts = False