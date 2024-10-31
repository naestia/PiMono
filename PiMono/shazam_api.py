# from ShazamAPI import Shazam
import json
from pathlib import Path
from pytube import YouTube
import asyncio
from shazamio import Shazam


async def main(song_path: str = None):
    if not song_path:
        path = Path.home() / "PiMono/Media/Mp3/Warhola.mp3"
    else:
        path = song_path

    shazam = Shazam()
    out = await shazam.recognize(str(path))
    return out

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
