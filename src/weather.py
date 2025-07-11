import aiohttp
from tts import speak

# latitude, longitude = 26.50, 80.24  # Kanpur
latitude, longitude = 12.97, 77.59 # Bangalore
# latitude, longitude = 26.91, 75.78  # Jaipur

async def fetch_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast/?latitude={lat}&longitude={lon}&hourly=temperature_2m,is_day&current_weather=true&timezone=auto"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

def wc_extract(wc):
    wc = str(wc)
    if wc in ("0", "1"):
        return "Clear skies"
    elif wc == "2":
        return "Partly cloudy"
    elif wc in ("3", "45", "48"):
        return "Cloudy"
    elif wc in ("51", "53", "55", "61", "63", "65", "80", "81", "82"):
        return "Rainy"
    elif wc in ("56", "57", "66", "67", "85", "86"):
        return "Snow showers"
    elif wc in ("71", "73", "75", "77"):
        return "Snow fall"
    elif wc in ("95", "96", "99"):
        return "Thunderstorm"
    return "Unknown"

async def get_weather(lat=latitude, lon=longitude):
    data = await fetch_weather(lat, lon)
    current = data["current_weather"]
    temp = current["temperature"]
    wc = current["weathercode"]
    description = wc_extract(wc)

    if description.lower().startswith("Clear skies"):
        await speak(f"The sky is clear with a temperature of {temp} degrees celsius")
    else:
        await speak(f"It's {description.lower()} with a temperature of {temp} degrees celsius")
