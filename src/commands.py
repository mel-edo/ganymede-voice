import subprocess
import datetime
import re
from rapidfuzz import process, fuzz
from tts import speak
from music import stream_music, stop_music, resume_music
from fortune import get_fortune
from ai_handler import handle_ai_query
from app_commands import launch_app, close_app
from web_commands import search_ddg, browse_random_art
from hypr import workspace_switcher
from weather import get_weather
from word2number import w2n

# Command registry
command_map = {}

# Helper functions
def register(phrases, func):
    for phrase in phrases:
        command_map[phrase.lower()] = func

def normalize_number(text: str):
    words = text.lower().split()
    for i, word in enumerate(words):
        try:
            number = w2n.word_to_num(word)
            words[i] = str(number)
        except ValueError:
            continue
    return ' '.join(words)

def format_time(dt: datetime.datetime):
    hour = dt.strftime('%I').lstrip("0")
    minute = dt.minute
    if minute == 0:
        minute_str = ""
    elif minute < 10:
        minute_str = f"oh {minute}"
    else:
        minute_str = f"{minute}"
    period = dt.strftime('%p').lower().replace('am', 'A M').replace('pm', 'P M')
    return f"{hour} {minute_str} {period}"

# Action functions
async def tell_time():
    now = datetime.datetime.now()
    time_str = format_time(now)
    await speak(f"The time is {time_str}", cacheable=False)

async def greet():
    await speak("Hey! How can I help you?")

async def brightness_inc():
    subprocess.run(["brightnessctl", "s", "10%+"])
    await speak("Brightness increased")

async def brightness_dec():
    subprocess.run(["brightnessctl", "s", "10%-"])
    await speak("Brightness decreased")

async def brightness_set(n: int):
    subprocess.run(["brightnessctl", "s", f"{n}%"])
    await speak(f"Brightness set to {n} percent", cacheable=False)

async def vol_set(n: int):
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{n}%"])
    await speak(f"Volume set to {n} percent", cacheable=False)

async def vol_inc():
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+10%"])
    await speak("Volume increased")

async def vol_dec():
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-10%"])
    await speak("Volume decreased")

async def kill():
    await speak("Exiting")
    exit(0)

async def weather_fetch():
    await get_weather()

async def art():
    await browse_random_art()

async def stop_music_cmd():
    await stop_music()

async def resume_music_cmd():
    await resume_music()

async def get_quote():
    await get_fortune()


# Register commands
register(["what time is it", "what's the time", "time now"], tell_time)
register(["hey", "hello", "hi", "yo"], greet)
register(["increase volume", "raise volume"], vol_inc)
register(["decrease volume", "lower volume"], vol_dec)
register(["increase brightness", "raise brightness"], brightness_inc)
register(["decrease brightness", "lower brightness"], brightness_dec)
register(["exit", "quit", "kill yourself"], kill)
register(["stop music"], stop_music_cmd)
register(["resume music", "pause music", "boss music"], resume_music_cmd)
register(["tell me a quote"], get_quote)
register(["what's the weather", "weather"], weather_fetch)
register(["browse art", "random art", "show me art"], art)
register(["stop", "nothing", "cancel"], lambda: None)


# Regex matchers
regex_patterns = [
    (re.compile(r"(?:set|change) volume to (\d{1,3})%?"), vol_set, 1),
    (re.compile(r"(?:set|change) brightness to (\d{1,3}%?)"), brightness_set, 1),
    (re.compile(r"play (.+)"), stream_music, 1),
    (re.compile(r"open (.+)"), launch_app, 1),
    (re.compile(r"close (.+)"), close_app, 1),
    (re.compile(r"search(?: for)? (.+)"), search_ddg, 1),
    (re.compile(r"(?:switch|change|move) to (\w+)"), workspace_switcher, 1),
]


# Main handler
async def handle_command(text: str):
    
    # Keyword based handler
    normalized_text = normalize_number(text.lower().strip())
    for pattern, func, group_index in regex_patterns:
        match = pattern.search(normalized_text)
        if match:
            arg = match.group(group_index)
            await func(arg)
            return


    # Fuzzy command handler
    commands = list(command_map.keys())
    match, score, _ = process.extractOne(text, commands, scorer=fuzz.partial_ratio)

    if score > 75:
        print(f"Matched: {match} ({score}%)")
        await command_map[match]()
    else:
        # AI handler
        return await handle_ai_query(text)