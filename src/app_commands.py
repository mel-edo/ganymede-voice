import subprocess
import os
from tts import speak

# Opening and closing of system apps
# close zen, code doesen't word - issue with pkill n flag

apps = {
    ("browser", "zen", "then", "web browser"): {
        "open": "zen-browser",
        "type": "exec",
        "name": "Zen"
    },
    ("discord", "discard"): {
        "open": "discord &",
        "type": "shell",
        "name": "Discord"
    },
    "terminal": {
        "open": "alacritty",
        "type": "exec",
        "name": "Terminal"
    },
    ("code", "good"): {
        "open": "code",
        "type": "exec",
        "name": "VS Code"
    },
    "steam": {
        "open": "steam",
        "type": "exec",
        "name": "Steam"
    }
}

def find_app(alias: str):
    alias = alias.lower()
    for key, app in apps.items():
        if alias in key:
            print(alias, key)
            return app
    return None

async def launch_app(app_key):
    app = find_app(app_key)
    if not app:
        await speak(f"I don't know how to open {app_key}", cacheable=False)
        return

    try:
        if app["type"] == "exec":
            subprocess.Popen([app["open"]])
        else:
            os.system(app["open"])
        await speak(f"Opening {app['name']}")

    except Exception as e:
        print(e)
        await speak(f"Failed to open {app['name']}")

async def close_app(app_key):
    app = find_app(app_key)
    if not app:
        await speak(f"I don't know how to close {app_key}")
        return
    
    try:
        proc_name = app['open'].strip().split()[0]
        subprocess.Popen(["pkill", "-fn", proc_name])
        await speak(f"Closed {app['name']}")

    except Exception as e:
        print(e)
