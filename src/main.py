from speech_recognition import transcribe, cleanup, listen_for_wake_word, register_wake_word_callback, set_command_mode
from commands import handle_command
from ai_handler import cancel_task
from tts import reset_tts_interrupt
from typing import Optional
import time
import os
import subprocess
import asyncio

print("Listening...")

current_task: Optional[asyncio.Task] = None
wake_word_listener_task = None

async def listen_for_command(timeout=7):
    print("Listening for your command...")
    set_command_mode(True)
    start_time = time.time()

    try:
        while time.time() - start_time < timeout:
            text = await transcribe()
            if text:
                print("Command: ", text)
                await handle_command(text)
                return
        print("No command heard")
    finally:
        set_command_mode(False)

async def handle_wake_word(text):
    global current_task
    if current_task and not current_task.done():
        print("Interrupting...")
        cancel_task()
        current_task.cancel()
        try:
            await current_task
        except asyncio.CancelledError:
            pass
    
    set_command_mode(False)
    reset_tts_interrupt()
    await play_ping()
    current_task = asyncio.create_task(listen_for_command())

async def play_ping():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sound_path = os.path.join(base_dir, "models", "slick-notification.ogg")
    proc = await asyncio.create_subprocess_exec("ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", sound_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await proc.wait()

async def main():
    global current_task, wake_word_listener_task

    print("Assistant is listening for wake word...")

    register_wake_word_callback(handle_wake_word)

    wake_word_listener_task = asyncio.create_task(listen_for_wake_word())

    try:
        await wake_word_listener_task

    except KeyboardInterrupt:
        print("Exiting")
        if current_task and not current_task.done():
            current_task.cancel()
        if wake_word_listener_task and not wake_word_listener_task.done():
            wake_word_listener_task.cancel()
        cleanup()

if __name__ == "__main__":
    asyncio.run(main())
