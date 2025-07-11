from tts import speak, interrupt_current_tts, reset_tts_interrupt
import asyncio
import aiohttp
import json
import re

api_url = "http://localhost:11434/api/chat"
model = "gemma3:1b-it-q8_0"

task_cancelled = asyncio.Event()

async def speaker_worker(play_queue):
    while True:
        try:
            text = await asyncio.wait_for(play_queue.get(), timeout=0.1)
            if text is None:
                break
            if task_cancelled.is_set():
                break
            await speak(text, cacheable=False)
            play_queue.task_done()
        except asyncio.TimeoutError:
            if task_cancelled.is_set():
                break
            continue
        except asyncio.CancelledError:
            interrupt_current_tts()
            break

def clean_markdown(text: str) -> str:
    # Remove bold, italic, underline, code
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # bold
    text = re.sub(r"\*(.*?)\*", r"\1", text)      # italic
    text = re.sub(r"__(.*?)__", r"\1", text)      # underline
    text = re.sub(r"_(.*?)_", r"\1", text)        # italic/underline
    text = re.sub(r"`{1,3}(.*?)`{1,3}", r"\1", text)  # inline code

    # Remove markdown links but keep text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove raw URLs
    text = re.sub(r"https?://\S+", "", text)

    # Remove stray markdown or formatting characters
    text = re.sub(r"[*_`:\[\]<>•]+", "", text)

    # Remove excess whitespace
    text = re.sub(r"\s{2,}", " ", text)
    
    return text.strip()

async def handle_ai_query(text: str):
    global task_cancelled
    task_cancelled.clear()
    reset_tts_interrupt()

    print("AI is thinking...")
    retries = 2
    delay = 2
    play_queue = asyncio.Queue()
    speaker_task = asyncio.create_task(speaker_worker(play_queue))

    await play_queue.put("Let me think...")

    try:
        for attempt in range(1, retries + 1):
            if task_cancelled.is_set():
                break

            buffer = ""
            try:
                headers = {
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": text}
                    ],
                    "stream": True,
                    "options": {
                        "system": "You are a concise, natural-sounding voice assistant. Always speak in 1-2 clear, short sentences. Never use symbols, markdown, or links. Do not ask follow-up questions."
                    },
                    "max_tokens": 200,
                    "temperature": 0.7,
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(api_url, headers=headers, json=payload) as response:
                        if response.status != 200:
                            raise Exception(f"API request failed with status {response.status}")
                        
                        async for chunk_bytes in response.content.iter_any():
                            if task_cancelled.is_set():
                                break

                            line = chunk_bytes.decode("utf-8").strip()
                            if not line:
                                continue
                            try:
                                chunk = json.loads(line)
                                content = chunk.get("message", {}).get("content", "")
                                if content:
                                    buffer += content
                                    if buffer.endswith((".", "!", "?")):
                                        cleaned = clean_markdown(buffer.strip())
                                        print("[BUFFER]: ", cleaned)
                                        if cleaned and len(cleaned.split()) >= 2:
                                            await play_queue.put(cleaned)
                                        buffer = ""
                            except json.JSONDecodeError:
                                continue

                if buffer.strip() and not task_cancelled.is_set():
                    await play_queue.put(buffer.strip())

            except Exception as e:
                print(f"[Attempt {attempt}], Error: {e}")

                if attempt < retries:
                    await asyncio.sleep(delay)
                else:
                    await play_queue.put("Sorry, I couldn't generate a response")
        
        await play_queue.put(None)
        await speaker_task
    except asyncio.CancelledError:
        interrupt_current_tts()
        await play_queue.put(None)
        try:
            await speaker_task
        except asyncio.CancelledError:
            pass
        raise

def cancel_task():
    global task_cancelled
    task_cancelled.set()
    interrupt_current_tts()