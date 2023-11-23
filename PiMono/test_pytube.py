from ShazamAPI import Shazam
from settings import *
import json
import eyed3

song = ""

for i in os.listdir(MP3):
    if "Adagio" in i:
        song = i

song = "Puppeteer.mp3"
path = f"{mp3Dir}/{song}"
id3 = eyed3.load(str(Path(path))).tag

print(id3.title)

def do_shazam():
    with open(path, "rb") as file:
        path_to_song = file.read()

    shazam = Shazam(path_to_song)
    rec_gen = shazam.recognizeSong()

    while True:
        print(next(rec_gen))
        
    json_data = json.dumps(next(rec_gen), indent=2)
    song_info = json.loads(json_data)

    print(song_info)

    id3 = eyed3.load(str(path))
    id3.tag.title = str(song_info[1]["track"]["title"])
    print(id3.tag.title)

    with open(f"{WORK_DIR}/json_data/{song}.json", "w") as json_file:
        json_file.write(json_data)


do_shazam()