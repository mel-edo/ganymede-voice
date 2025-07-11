from tts import speak
from hypr import workspace_switcher
import webbrowser
import random

async def search_ddg(query: str):
    if not query.strip():
        await speak("What should I search for?")
        return
    url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    await speak(f"Searching duckduckgo for {query}", cacheable=False)
    await workspace_switcher("1")

async def jerk_it_a_little():
    danbooru = ["1girl", "blue_archive", "genshin_impact", "honkai_(series)", "zenless_zone_zero"]
    tag = random.choice(danbooru)
    url = f"https://danbooru.donmai.us/posts/random?tags=rating:q,s+{tag}+-male_focus"

    webbrowser.open(url)
    await speak("Very well")
    await speak("Jerking it, just a little")
    await workspace_switcher("1")