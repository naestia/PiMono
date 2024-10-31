import sqlite3
from pathlib import Path
from settings import *
import uuid

for file in mp3Dir.glob("*.mp3"):

    new_uuid = uuid.uuid4()
    song_name = file.stem
    path = file


file_path = Path() / "testing.db"
if not file_path.exists():
    file_path.touch()

var = "movie"
con = sqlite3.connect(file_path)
cur = con.cursor()

cur.execute(f"CREATE TABLE {var}(title, year, score)")

res = cur.execute("SELECT name FROM sqlite_master")
print(res.fetchone())
