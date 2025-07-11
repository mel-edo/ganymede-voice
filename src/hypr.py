from tts import speak
import subprocess

# Add a check for which wm is in use. If condition to check

number_map = {
    "one": "1",
    "two": "2",
    "to": "2",
    "three": "3",
    "four": "4",
    "for": "4",
    "five": "5"
}

async def workspace_switcher(n: str):
    if n.isdigit():
        subprocess.run(["hyprctl", "dispatch", "workspace", n])
    else:
        try:
            await speak("Switching")
            subprocess.run(["hyprctl", "dispatch", "workspace", number_map[n]])
        except Exception as _:
            print("Key error, it heard something else")
    return