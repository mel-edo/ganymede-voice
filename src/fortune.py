import subprocess
from tts import speak

# Quote integration

async def get_fortune():
    quote = subprocess.run(["fortune", "-s"], capture_output=True, text=True)
    await speak(quote.stdout, cacheable=False)