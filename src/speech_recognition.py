import pyaudio
from vosk import Model, KaldiRecognizer
import asyncio
import threading
import json
import queue

wake_word = "ganymede"

model = Model("models/vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

audio_queue = queue.Queue()
running = True

wake_word_callbacks = []
wake_word_detected = asyncio.Event()

def register_wake_word_callback(callback):
    wake_word_callbacks.append(callback)

def audio_worker():
    global running
    while running:
        try:
            data = stream.read(4096, exception_on_overflow=False)
            audio_queue.put(data)
        except Exception as e:
            print(f"Audio worker error: {e}")
            break

audio_thread = threading.Thread(target=audio_worker, daemon=True)
audio_thread.start()

async def transcribe():
    timeout = 1.0
    chunks_processed = 0
    max_chunks = int(16000 * timeout / 4096)

    while chunks_processed < max_chunks:
        try:
            data = audio_queue.get(timeout=0.1)
            chunks_processed += 1
            if rec.AcceptWaveform(data):
                text =  json.loads(rec.Result()).get("text", "").strip()
                if text:
                    return text

        except queue.Empty:
            await asyncio.sleep(0.01)
            continue
        except Exception as e:
            print(f"Transcribe error: {e}")
            break
    
    return None

async def listen_for_wake_word():
    while running:
        try:
            data = audio_queue.get(timeout=0.1)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f"Heard: {text}")
                    if wake_word in text.lower():
                        wake_word_detected.set()
                        for callback in wake_word_callbacks:
                            await callback(text)

        except queue.Empty:
            await asyncio.sleep(0.01)
            continue
        except Exception as e:
            print(f"Wake word detection error: {e}")
            break

def cleanup():
    global running
    running = False
    if audio_thread.is_alive():
        audio_thread.join(timeout=1.0)
    stream.stop_stream()
    stream.close()
    p.terminate()
