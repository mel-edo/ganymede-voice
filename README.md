# Ganymede - A Voice Assistant for linux

A lightweight, privacy focused voice assistant that runs locally on your machine.

## Features

### System Control

- Volume control
- Brightness control
- Workspace switching (currently only on hyprland due to the usage of hyprctl)

### Music

- Supports playing songs through youtube. Just say play (song-name)
- Stop, resume and pausing works

### Web search

- Supports searching on duckduckgo

### Application management

- Launching and closing (limited to specific apps currently)

### Utility commands

- Ask for current time
- Fetches weather from open meteo (requires lat and long to be set)
- Greetings
- Exitting the program

## Known Issues

- gemma3:1b talks for too long
- says links

## Todo:

- identifying song playing from playback devices
- screenshot/screen recording start,stop
- timer/alarm for x minutes
- reminders
- definition, translation of things - could be done by ai model
- system temps, uptime, lockscreen, sleep, restart, toggle dnd etc.
- what's this song, identify song feature using shazamIO
- what's on my screen summarize using ocr
- summarize selected text (as highlighted text will be available on clipboard)
- add gemini 2.5 flash (can also help for what's on my screen)
- add option to use local model or gemini

- make it a cli program with flags for logging, setting api keys, lat long, wakeword

## Installation

Prerequisites: 
- Python 3.8+
- Linux system (tested on systems with Hyprland)

Dependencies:
- FFmpeg for audio playback
- Pipewire
- brightnessctl
- mpv
- ollama (for local models)
- yt-dlp

Python Dependencies:
```
pip install vosk pyaudio rapidfuzz word2number asyncio aiohttp
```

## Usage

```
chmod +x run.sh
./run.sh
```

## Credits

- Ping sound from [Notification Sounds](https://notificationsounds.com/)
- include links for vosk and piper tts models here