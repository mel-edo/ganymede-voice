import yt_dlp
from tts import speak
import subprocess
import threading

# add mix playlist support
# add lower mpv volume when wake word is heard
# kill mpv processes if program ends abruptly
# music takes long to load even after the speak has finished

music_playing = False
current_process = None

async def stop_music():
    global music_playing, current_process
    if music_playing:
        subprocess.run(["playerctl", "--player=mpv", "stop"], stderr=subprocess.DEVNULL)

        if current_process and current_process.poll() is None:
            current_process.terminate()
            current_process = None
        await speak("Music Stopped")
        music_playing = False

async def resume_music():
    global music_playing
    if not music_playing and current_process is not None:
        await speak("Resuming")
        subprocess.run(["playerctl", "--player=mpv", "play-pause"])
        music_playing = True
    elif current_process is None:
        await speak("Nothing is currently playing")
    else:
        subprocess.run(["playerctl", "--player=mpv", "play-pause"])
        music_playing = False

def get_video_info(query):
    ydl_opts = {
        'quiet': True,
        'default_search': 'ytsearch1',
        'noplaylist': True,
        'skip_download': True,
        'extract_flat': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if not info or 'entries' not in info or not info['entries']:
            return None
        
        video = info['entries'][0]
        return {
            'id': video['id'],
            'title': video.get('title', 'Unknown Title'),
            'uploader': video.get('Uploader', 'Unknown Artist'),
            'duration': video.get('duration', 0),
            'url': f"https://www.youtube.com/watch?v={video['id']}"
        }

def monitor_music_process():
    global music_playing, current_process

    if current_process:
        current_process.wait()
        music_playing = False
        current_process = None

async def stream_music(query):
    global music_playing, current_process
    await stop_music()

    await speak("Searching for music...")

    video_info = get_video_info(query)
    if not video_info:
        await speak("Sorry, I couldn't find that song")
        return

    title = video_info['title']

    title = title.replace(" (Official Video)", "").replace(" (Official Music Video)", "")
    title = title.replace(" - Topic", "").replace(" (Lyrics)", "")
    title = title.replace(" (Official Audio)", "")
    title = title.replace(" Audio", "")

    await speak(f"Playing {title}", cacheable=False)
    
    mpv_args = [
        'mpv',
        video_info['url'],
        "--no-video",
        "--no-terminal",
        "--force-window=no",
    ]

    try:
        current_process = subprocess.Popen(mpv_args)
        music_playing = True

        monitor_thread = threading.Thread(target=monitor_music_process, daemon=True)
        monitor_thread.start()
    except Exception as e:
        await speak("Sorry, I couldn't play that song")
        print(f"Error starting mpv: {e}")