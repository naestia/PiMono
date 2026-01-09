import asyncio
import sys
import os
import random
import json

import requests
from pathlib import Path
from requests import ConnectionError, Timeout
import time
from moviepy.editor import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtWidgets import QApplication, QWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, QUrl
from PyQt5 import uic
from pytube import Search
from ShazamAPI import Shazam
from shazamio import Shazam as shazz
import eyed3

from track_widget import NewTrack
from settings import *
from slot_widget import TrackSlot
# import pimono_db


class PiMono(QWidget):
    def __init__(self, *args, **kwargs):
        """
        Initializing class method to set the most basic widgets
        and set up the application.
        """
        super(PiMono, self).__init__(*args, **kwargs)
        # Load form.ui to get the GUI
        self.file_path = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(f"{self.file_path}/forms/form.ui", self)
        self.create_application_directory()
        self.song = ""
        self.songs_played = []
        self.track_dict = {}
        self.playlist_track_dict = {}
        self.library_track_dict = {}
        self.song_library = []
        self.song_paths = []
        self.current_position = 0

        # Setup media player and playlist
        self.player = QMediaPlayer(self)
        self.playlist = QMediaPlaylist(self.player)
        self.playlist.setPlaybackMode(4)
        self.player.setPlaylist(self.playlist)
        self._isLibrarySet = False

        # Setup standard library
        self.setPlaylist(mp3Dir)

        # Startup page buttons
        self._convertButton.clicked.connect(self.videoTab)
        self._libraryButton.clicked.connect(self.libraryTab)
        self._playlistsButton.clicked.connect(self.playlistTab)
        self._myComputerButton.clicked.connect(self.myComputerTab)

        # Playlist page buttons
        self._newPlaylistButton.clicked.connect(self.showPlaylistCreation)

        self.search_results = []
        self.result_index = 0

        self.playButton.clicked.connect(self.playPause)
        self.nextButton.clicked.connect(self.nextSong)
        self.previousButton.clicked.connect(self.previousSong)

        # Running methods as initialization
        # Setting page indexes for initialization
        self.set_starting_pages()
        self.playlistTrackWidgets()
        self.libraryTrackWidgets()

        # Setting placeholder text for line edit fields
        self.lineEdit.setPlaceholderText("Search...")
        self.lineEdit_3.setPlaceholderText("Playlist Name...")
        self.search_field.setPlaceholderText("Enter YouTube Search...")
        self.lineEdit_3.hide()

        self._searchButton.clicked.connect(self.searchYoutube)
        self._previousResultButton.hide()
        self._nextResultButton.hide()
        self._previousResultButton.clicked.connect(self.showPreviousResult)
        self._nextResultButton.clicked.connect(self.showNextResult)
        self._downloadButton.clicked.connect(self.downloadFromYoutube)

        self.listWidget.itemDoubleClicked.connect(self.setPlaylistPage)
        self.playlist.currentIndexChanged.connect(self.setNowPlaying)

    def setCurrentSong(self, identifier):
        """

        :param identifier:
        :return:
        """
        song = self.track_dict[identifier]["Name"]
        self.song = song
        track = f"{song}.mp3"
        song_path = Path(f"{mp3Dir}/{track}")
        json_file = Path(f"{jsonLogDir}/{song}.json")
        for index in range(len(self.track_dict)):
            file_name = self.playlist.media(index).canonicalUrl().fileName()
            if file_name == track:
                if not self.playlist.currentIndex() == index:
                    self.playlist.setCurrentIndex(index)
                    self.player.play()
                    if json_file.exists():
                        self.setAlbumArt(json_file, song)
                    else:
                        self.setMetaData(song_path=song_path)

    def setAlbumArt(self, json_path, song):
        with json_path.open("r") as file:
            data = file.read()

        json_data = json.loads(data)
        cover_art = ""
        cover_art_path = f"{albumCovers}/{song}.jpg"
        track = {}
        if json_data:
            track = json_data.get("track")

        if track:
            images = track.get("images")
            if images:
                url = images.get("coverart")
            else:
                url = "https://images.pexels.com/photos/2170729/pexels-photo-2170729.jpeg"
        else:
            url = "https://images.pexels.com/photos/2170729/pexels-photo-2170729.jpeg"

        if not Path(cover_art_path).exists():
            try:
                cover_art = requests.get(timeout=3, url=url).content
            except ConnectionError:
                print("Check your internet connection")
            except Timeout:
                print("Request Timed out")

            if cover_art:
                with open(f"{cover_art_path}", "wb") as file:
                    file.write(cover_art)

        self.albumArt.setStyleSheet(f"border-image: url('{cover_art_path}');")

    def setNowPlaying(self):
        if not self.playlist.currentIndex() in self.songs_played:
            self.songs_played.append(self.playlist.currentIndex())

        now_playing = self.playlist.media(self.playlist.currentIndex()).canonicalUrl().fileName().replace('.mp3', '')
        identifier = self.getIdentifierFromName(now_playing)
        self.setCurrentSong(identifier)
        self._nowPlaying.setText(f"{now_playing}")

    def getIdentifierFromName(self, song_name):
        for track in self.track_dict:
            if self.track_dict[track]['Name'] == song_name:
                return track

    def playPause(self):
        if self.song:
            if self.player.state() == 2 or self.player.state() == 0:
                # Resume from the saved position if available
                if self.current_position > 0:
                    self.player.setPosition(self.current_position)
                self.player.play()
                self.setNowPlaying()
            elif self.player.state() == 1:
                # Save the current position before pausing
                self.current_position = self.player.position()
                self.player.pause()
                self._nowPlaying.clear()

    def nextSong(self):
        self.playlist.next()

    def previousSong(self):
        if self.playlist.currentIndex() in self.songs_played:
            self.songs_played.remove(self.playlist.currentIndex())

        self.playlist.previous()

    def setPlaylist(self, dir):
        self.clearPlaylist()
        for song in os.listdir(dir):
            if song.endswith(".mp3") and song not in self.song_library:
                self.playlist.addMedia(QMediaContent(QUrl().fromLocalFile(f"{dir}/{song}")))
                self.song_library.append(song)
                self.song_paths.append(f"{dir}/{song}")
    
    def clearPlaylist(self):
        self.playlist.clear()
        self.song_library.clear()
        self.song_paths.clear()
    
    def appendSong(self, song):
        self.playlist.addMedia(QMediaContent(QUrl().fromLocalFile(song)))
        self.song_library.append(Path(song).stem)
        self.song_paths.append(song)

    def showPreviousResult(self):
        """PyTube Method"""
        self.result_index -= 1
        self.displayResults()

    def showNextResult(self):
        """PyTube Method"""
        if self.result_index == (len(self.search_result) - 1):
            self.result_index = 0
        else:
            self.result_index += 1
        
        self.displayResults()

    def displayResults(self):
        """PyTube Method"""
        self.yt_video = self.search_result[self.result_index]
        title = self.yt_video.title
        duration_minutes = self.yt_video.length // 60
        duration_seconds = self.yt_video.length % 60
        if duration_seconds < 10:
            duration = f"{duration_minutes}:0{duration_seconds}"
        else:
            duration = f"{duration_minutes}:{duration_seconds}"
        thumbnail_url = self.yt_video.thumbnail_url
        video_details = self.yt_video.vid_info.get("videoDetails")
        video_id = video_details.get("videoId")

        self.setResultThumbnail(thumbnail_url, video_id)
        
        self.video_title.setText(title)
        self.video_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.duration_lbl.setText(duration)
        self.duration_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._downloadButton.setText("Download")
        self._previousResultButton.show()
        self._nextResultButton.show()
        
    def setResultThumbnail(self, url, vid_id):
        """PyTube Method"""
        data = requests.get(url).content
        img_name = f"{vid_id}.jpg"
        img_path = Path(f"{THUMBNAIL_DIR}/{img_name}")
        if not img_path.exists():
            with open(f"{img_path}", "wb") as file:
                file.write(data)

        self.label_5.setStyleSheet(f"border-image: url('{THUMBNAIL_DIR}/{img_name}');")

    def searchYoutube(self):
        """PyTube Method"""
        search_term = self.search_field.text()
        if search_term:
            search = Search(search_term)
            self.search_result = search.results
            self.result_index = 0
            self.displayResults()

    def downloadFromYoutube(self):
        """
        PyTube Method
        Downloads the YouTube Video and converts the MP4 to an MP3.
        """
        video = self.yt_video.streams.filter().get_highest_resolution()
        destination = MP4
        file_name = video.default_filename
        video.download(output_path=destination)
        destination_mp3 = f"{mp3Dir}/{file_name.replace('.mp4', '.mp3')}"
        destination_mp4 = f"{MP4}/{file_name}"
        self._convert_to_mp3(destination_mp4, destination_mp3)
        os.remove(f"{MP4}/{file_name}")
    
    def _convert_to_mp3(self, mp4, mp3):
        """PyTube Method"""
        print(mp4)
        if not os.path.exists(mp3):
            from_mp4 = AudioFileClip(mp4)
            from_mp4.write_audiofile(mp3)
            from_mp4.close()

        new_name = self.setMetaData(mp3)
        if self._isLibrarySet:    
            self.addSongToPlaylist(new_name, "lib")
        
        self.appendSong(new_name)
    
    def _get_meta_data(self, song=None):
        """PyTube Method"""
        if song:
            with open(song, "rb") as file:
                path_to_song = file.read()

            shazam = Shazam(path_to_song)
            rec_gen = shazam.recognizeSong()
            json_data = json.dumps(next(rec_gen), indent=2)
            song_info = json.loads(json_data)

            if song_info.get("matches"):
                try:
                    song_name = song_info[1]["track"]["title"]
                    artist = song_info[1]["track"]["subtitle"]
                except:
                    song_name = str(Path(song).stem)
                    artist = "Unknown"
                try:
                    album_name = song_info[1]['track']['sections'][0]['metadata'][0]['text']
                except KeyError:
                    album_name = 'Unknown'
                except IndexError:
                    album_name = 'Unknown'

            self.logJsonDump(song_name, json_data)
        
        return {"Title": song_name, "Artist": artist, "Album": album_name}

    async def getMetaDataDos(self, song):
        shazam = shazz()
        out = await shazam.recognize(str(song))
        song_name = str(Path(song).stem)
        artist = "Unknown"
        album_name = "Unknown"
        if out.get("matches"):
            track = out.get('track')
            try:
                song_name = track.get('title')
                artist = track.get('subtitle')
            except:
                print(f"Error getting meta data for {song}")
            try:
                album_name = track.get('sections')[0]['metadata'][0]['text']
            except KeyError:
                album_name = 'Unknown'
            except IndexError:
                album_name = 'Unknown'

            self.logJsonDump(song_name, out)

        return {"Title": song_name, "Artist": artist, "Album": album_name}

    def setMetaData(self, song_path):
        """
        PyTube Method
        Needs the entire song_path
        """
        print(song_path)
        loop = asyncio.get_event_loop()
        meta_data = loop.run_until_complete(self.getMetaDataDos(song_path))
        id3 = eyed3.load(song_path)
        id3.tag.title = meta_data["Title"]
        id3.tag.artist = meta_data["Artist"]
        id3.tag.album = meta_data["Album"]
        id3.tag.save()
        new_name = f"{mp3Dir}/{id3.tag.title}.mp3"
        os.rename(song_path, f"{mp3Dir}/{id3.tag.title}.mp3")
        return new_name

    def libraryTab(self):
        """
        Initializes library tab
        """
        self.setLibraryPage()
        if not self._isLibrarySet:
            for song in self.song_library:
                self.addSongToPlaylist(song, "lib")

        self._isLibrarySet = True

    def addTrackObject(self, identifier, name="Unknown", artist="Unknown", duration=120):
        self.track_dict[identifier] = {
            "Identifier": identifier,
            "Track Number": (len(self.track_dict) + 1),
            "Name": name,
            "Artist": artist,
            "Duration": duration
        }

    def addSongToPlaylist(self, song, typeOf=None):
        path_to_song = Path(f'{mp3Dir}/{song}')
        song = Path(song).stem
        id3 = eyed3.load(path_to_song)
        artist = id3.tag.artist if id3.tag.artist is    not None else "Unknown"
        index = len(self.track_dict) + 1
        self.new_track = NewTrack()
        if typeOf == "lib":
            track_slot = self.library_track_dict.get(index)
        else:
            track_slot = self.playlist_track_dict.get(index)
        track_slot.ts_horizontalLayout.addWidget(self.new_track)
        self.addTrackObject(
            identifier=self.new_track,
            name=song,
            artist=artist
        )
        if self.track_dict[self.new_track]["Track Number"] < 10:
            self.new_track.idLabel.setText(f"    {str(self.track_dict[self.new_track]['Track Number'])}")
        else:
            self.new_track.idLabel.setText(f"   {str(self.track_dict[self.new_track]['Track Number'])}")

        self.new_track.nameLabel.setText(f"   {str(self.track_dict[self.new_track]['Name'])}")
        self.new_track.artistLabel.setText(f"   {str(self.track_dict[self.new_track]['Artist'])}")
        self.new_track.durationLabel.setText(f"   {str(self.track_dict[self.new_track]['Duration'])}")

    def showPlaylistCreation(self):
        self.lineEdit_3.show()

    def _create_playlist(self, playlist_name: str):
        item = QListWidgetItem(playlist_name, self.listWidget)
        item.setSelected(False)

    def videoTab(self):
        self.stackedWidget_2.setCurrentIndex(2)

    def setPlaylistPage(self):
        self.stackedWidget_2.setCurrentIndex(1)
        if self.listWidget.item(self.listWidget.currentRow()):
            self._playlistNameLabel.setText(self.listWidget.item(self.listWidget.currentRow()).text())
            print(self.listWidget.item(self.listWidget.currentRow()).text())

        self.listWidget.setCurrentItem(None)

    def setLibraryPage(self):
        self.stackedWidget_2.setCurrentIndex(3)
        self._libraryLabel.setText("My Library")

    def libraryTrackWidgets(self):
        for track in range(1000):
            self.library_track_slot = TrackSlot()
            self.verticalLayout_13.addWidget(self.library_track_slot)
            self.library_track_dict[len(self.library_track_dict) + 1] = self.library_track_slot

    def playlistTrackWidgets(self):
        for track in range(1000):
            self.playlist_track_slot = TrackSlot()
            self.verticalLayout_3.addWidget(self.playlist_track_slot)
            self.playlist_track_dict[len(self.playlist_track_dict) + 1] = self.playlist_track_slot
 
    def playlistTab(self):
        self._myComputerButton.setStyleSheet("QPushButton {background-color:#282c32; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self._playlistsButton.setStyleSheet("QPushButton {background-color:#393e46; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self.stackedWidget_3.setCurrentIndex(1)

    def myComputerTab(self):
        self._playlistsButton.setStyleSheet("QPushButton {background-color:#282c32; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self._myComputerButton.setStyleSheet("QPushButton {background-color:#393e46; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self.hidePlaylistCreation()
        self.stackedWidget_3.setCurrentIndex(2)

    def hidePlaylistCreation(self):
        self.lineEdit_3.clear()
        self.lineEdit_3.hide()

    def keyPressEvent(self, event):
        if event.key() == 32:
            self.playPause()

        if self.search_field.text():
            if event.key() == 16777220:
                self._searchButton.click()
                self.search_field.clear()
        
        if self.lineEdit_3.text():
            if event.key() == 16777220:
                playlist_name = self.lineEdit_3.text()
                self._create_playlist(playlist_name)
                self.hidePlaylistCreation()
            if event.key() == 16777216:
                self.hidePlaylistCreation()

    def mouseDoubleClickEvent(self, event):
        """
        At doubleclick event, checks if any of the song objects are under the cursor
        """
        for identifier in self.track_dict:
            if identifier.underMouse():
                self.songs_played.clear()
                self.setCurrentSong(identifier)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            for track in self.track_dict:
                if track.underMouse():
                    track_number = self.track_dict[track]["Track Number"]
                    track.styleFrame.setStyleSheet(SELECTED)
                    self.playlist_track_dict[track_number].setStyleSheet("background-color: black;")
                else:
                    track.styleFrame.setStyleSheet(UNSELECTED)
            if self.listWidget.currentItem():
                self.listWidget.setCurrentItem(None)
        elif event.button() == Qt.MouseButton.RightButton:
            pass

    @staticmethod
    def create_application_directory():
        for directory in appDirList:
            if not directory.exists():
                directory.mkdir()
    
    def set_starting_pages(self):
        self.stackedWidget_2.setCurrentIndex(0)
        self.stackedWidget_3.setCurrentIndex(0)
        self.stackedWidget_4.setCurrentIndex(1)

    @staticmethod
    def logJsonDump(song=None, json_data=None):
        if jsonLogDir.exists() and song:
            log_file = Path(f"{jsonLogDir}/{song}.json")
            with log_file.open("w") as file:
                json.dump(json_data, file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = PiMono()
    widget.show()
    sys.exit(app.exec())
