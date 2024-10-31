import asyncio
import json
import sqlite3
import uuid
from pathlib import Path
from mutagen.mp3 import MP3
import settings
import shazam_api

import pysnooper


class PiMonoDB:
    def __init__(self):
        db_file = settings.databaseDir / "general.db"
        self.create_database(db_file)
        self.con = sqlite3.connect(db_file)

    def migrate(self):
        for file in settings.mp3Dir.glob("*.mp3"):
            #file = settings.mp3Dir / "RETAKE.mp3"
            new_uuid = str(uuid.uuid4())
            song_name = file.stem
            audio = MP3(file)
            duration = audio.info.length
            loop = asyncio.get_event_loop()
            meta_data = loop.run_until_complete(shazam_api.main(str(file)))
            if meta_data.get('matches'):
                artist_id = self.get_artist(meta_data.get("track").get("subtitle"))
            else:
                artist_id = None
                album_id = None

            self.add_track(new_uuid, song_name, artist_id, duration)

    def create_database(self, db_file):
        if not db_file.exists():
            db_file.touch()

    def init_tables(self):
        cur = self.con.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS
                Track(
                    ID uuid4 NOT NULL UNIQUE,
                    Title varchar(100),
                    ArtistID uuid4,
                    Duration FLOAT
                )
            """
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS
                Artist(
                    ID uuid4 NOT NULL UNIQUE,
                    Name varchar(100)
                )
            """
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS
                Playlist(
                    ID uuid4 NOT NULL UNIQUE,
                    Name varchar(100)
                )
            """
        )
        self.con.commit()

    @pysnooper.snoop()
    def add_track(self, id, title, artistId, duration):
        cur = self.con.cursor()
        cur.execute(
            f"""INSERT INTO
                Track(
                    ID,
                    Title,
                    ArtistID,
                    Duration
                )
                VALUES(
                    ?,
                    ?,
                    ?,
                    ?
                )""",
(
                id,
                title,
                artistId,
                duration
            )
        )
        self.con.commit()

    def artist_exists(self, name):
        cur = self.con.cursor()
        res = cur.execute(
            f"SELECT * FROM Artist WHERE Name='{name}'"
        )
        result = res.fetchone()
        if result:
            return result[0]

        return None

    def add_artist(self, id, name):
        cur = self.con.cursor()
        cur.execute(
            """INSERT INTO
                Artist(
                    ID,
                    Name
                )
                VALUES(
                    ?,
                    ?
                )""",
            (
                id,
                name
            )
        )
        self.con.commit()

    def get_artist(self, name):
        artist_id = self.artist_exists(name)
        if artist_id:
            return artist_id

        artist_id = str(uuid.uuid4())
        self.add_artist(artist_id, name)
        return artist_id

    def see_track(self):
        cur = self.con.cursor()
        res = cur.execute(f"SELECT ArtistId FROM Track WHERE Title='Simple & Sweet';")
        print(res.fetchall())

    def see_artist(self):
        cur = self.con.cursor()
        res = cur.execute("SELECT * FROM Artist;")
        print(res.fetchall())



    def get_track_by_id(self, id):
        pass


if __name__ == "__main__":
    database = PiMonoDB()
    #database.init_tables()
    database.see_track()
