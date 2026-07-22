import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

BOT_PREFIX = "!"

FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            # 'options': '-vn -c:a libopus -b:a 96k', 
            "options": "-vn",
        }

YDL_OPTIONS = {
        'format': 'bestaudio[abr<96]/best',
        'noplaylist': True,
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
    }
