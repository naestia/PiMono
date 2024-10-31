import os
from pathlib import Path

# These paths are for code related stuff
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = Path(SRC_DIR).parent
THUMBNAIL_DIR = WORK_DIR / "thumbnails"
MP4 = WORK_DIR / "music/mp4"
MP3 = WORK_DIR / "music/mp3"

# These paths are for app related stuff
appDir = Path.home() / "PiMono"
mediaDir = appDir / "Media"
mp3Dir = mediaDir / "Mp3"
dataDir = appDir / "Data"
logDir = appDir / "Logs"
jsonLogDir = logDir / "Json logs"
databaseDir = dataDir / ".database"
albumCovers = mediaDir / "Images"

# appDirList is for creating all directories when starting up the app
appDirList = [
    MP4,
    MP3,
    THUMBNAIL_DIR,
    appDir,
    mediaDir,
    mp3Dir,
    dataDir,
    logDir,
    jsonLogDir,
    databaseDir,
    albumCovers,
]
