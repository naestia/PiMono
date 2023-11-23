import os
from pathlib import Path

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = Path(SRC_DIR).parent
THUMBNAIL_DIR = WORK_DIR / "thumbnails"
MP4 = WORK_DIR / "music/mp4"
MP3 = WORK_DIR / "music/mp3"
appDir = Path.home() / "PiMono"
mediaDir = appDir / "Media"
mp3Dir = mediaDir / "Mp3"
dataDir = appDir / "Data"
logDir = appDir / "Logs"
jsonLogDir = logDir / "Json logs"
databaseDir = dataDir / ".database"
appDirList = [
            appDir,
            mediaDir,
            mp3Dir,
            dataDir,
            logDir,
            jsonLogDir,
            databaseDir,
        ]
