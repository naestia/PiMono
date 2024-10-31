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

        # Setup media player and playlist
        self.player = QMediaPlayer(self)
        self.playlist = QMediaPlaylist(self.player)
        self.playlist.setPlaybackMode(4)
        self.player.setPlaylist(self.playlist)
        self._isLibrarySet = False

        # Setup standard library
        self._set_playlist(mp3Dir)

        # Startup page buttons
        self._convertButton.clicked.connect(self._video_tab)
        self._libraryButton.clicked.connect(self._library_tab)
        self._playlistsButton.clicked.connect(self._playlist_tab)
        self._myComputerButton.clicked.connect(self._my_computer_tab)

        # Playlist page buttons
        self._newPlaylistButton.clicked.connect(self._show_playlist_creation)

        self.search_results = []
        self.result_index = 0

        self.playButton.clicked.connect(self._play_pause)
        self.nextButton.clicked.connect(self._next_song)
        self.previousButton.clicked.connect(self._previous_song)

        # Running methods as initialization
        # Setting page indexes for initialization
        self.set_starting_pages()
        self._playlist_track_widgets()
        self._library_track_widgets()

        # Setting placeholder text for line edit fields
        self.lineEdit.setPlaceholderText("Search...")
        self.lineEdit_3.setPlaceholderText("Playlist Name...")
        self.search_field.setPlaceholderText("Enter YouTube Search...")
        self.lineEdit_3.hide()

        self._searchButton.clicked.connect(self._search_youtube)
        self._previousResultButton.hide()
        self._nextResultButton.hide()
        self._previousResultButton.clicked.connect(self._show_previous_result)
        self._nextResultButton.clicked.connect(self._show_next_result)
        self._downloadButton.clicked.connect(self._download_from_youtube)

        self.listWidget.itemDoubleClicked.connect(self._set_playlist_page)
        self.playlist.currentIndexChanged.connect(self._set_now_playing)

    def _set_current_song(self, identifier):
        """

        :param identifier:
        :return:
        """
        song = self._get_song(identifier)
        track = f"{song}.mp3"
        song_path = Path(f"{mp3Dir}/{track}")
        json_file = Path(f"{jsonLogDir}/{song}.json")
        for index in range(len(self.track_dict)):
            file_name = self.playlist.media(index).canonicalUrl().fileName()
            if file_name == track:
                self.playlist.setCurrentIndex(index)
                self.player.play()
                if json_file.exists():
                    self._set_album_art(json_file, song)
                else:
                    self._set_meta_data(song_path=song_path)

    def _set_album_art(self, json_path, song):
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

    def _get_song(self, identifier):
        return self.track_dict[identifier]["Name"]

    def _set_now_playing(self):
        if not self.playlist.currentIndex() in self.songs_played:
            self.songs_played.append(self.playlist.currentIndex())

        now_playing = self.playlist.media(self.playlist.currentIndex()).canonicalUrl().fileName().replace('.mp3', '')
        identifier = self._get_identifier_from_name(now_playing)
        self._set_current_song(identifier)
        self._nowPlaying.setText(f"{now_playing}")

    def _get_identifier_from_name(self, song_name):
        for track in self.track_dict:
            if self.track_dict[track]['Name'] == song_name:
                return track

    def _play_pause(self):
        if self.player.state() == 2 or self.player.state() == 0:
            self.player.play()
            self._set_now_playing()
        elif self.player.state() == 1:
            self.player.pause()
            self._nowPlaying.clear()

    def _next_song(self):
        self.playlist.next()

    def _previous_song(self):
        if self.playlist.currentIndex() in self.songs_played:
            self.songs_played.remove(self.playlist.currentIndex())

        self.playlist.previous()

    def _set_playlist(self, dir):
        self._clear_playlist()
        for song in os.listdir(dir):
            if song.endswith(".mp3") and song not in self.song_library:
                self.playlist.addMedia(QMediaContent(QUrl().fromLocalFile(f"{dir}/{song}")))
                self.song_library.append(song)
                self.song_paths.append(f"{dir}/{song}")
    
    def _clear_playlist(self):
        self.playlist.clear()
        self.song_library.clear()
        self.song_paths.clear()
    
    def _append_song(self, song):
        self.playlist.addMedia(QMediaContent(QUrl().fromLocalFile(song)))
        self.song_library.append(Path(song).stem)
        self.song_paths.append(song)

    def _show_previous_result(self):
        """PyTube Method"""
        self.result_index -= 1
        self._display_results()

    def _show_next_result(self):
        """PyTube Method"""
        if self.result_index == (len(self.search_result) - 1):
            self.result_index = 0
        else:
            self.result_index += 1
        
        self._display_results()

    def _display_results(self):
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

        self._set_result_thumbnail(thumbnail_url, video_id)
        
        self.video_title.setText(title)
        self.video_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.duration_lbl.setText(duration)
        self.duration_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._downloadButton.setText("Download")
        self._previousResultButton.show()
        self._nextResultButton.show()
        
    def _set_result_thumbnail(self, url, vid_id):
        """PyTube Method"""
        data = requests.get(url).content
        img_name = f"{vid_id}.jpg"
        img_path = Path(f"{THUMBNAIL_DIR}/{img_name}")
        if not img_path.exists():
            with open(f"{img_path}", "wb") as file:
                file.write(data)

        self.label_5.setStyleSheet(f"border-image: url('{THUMBNAIL_DIR}/{img_name}');")

    def _search_youtube(self):
        """PyTube Method"""
        search_term = self.search_field.text()
        if search_term:
            search = Search(search_term)
            self.search_result = search.results
            self.result_index = 0
            self._display_results()

    def _download_from_youtube(self):
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

        new_name = self._set_meta_data(mp3)
        if self._isLibrarySet:    
            self._add_song_to_playlist(new_name, "lib")
        
        self._append_song(new_name)
    
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

            self._log_json_dump(song_name, json_data)
        
        return {"Title": song_name, "Artist": artist, "Album": album_name}

    async def _get_meta_data_dos(self, song):
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

            self._log_json_dump(song_name, out)

        return {"Title": song_name, "Artist": artist, "Album": album_name}

    def _set_meta_data(self, song_path):
        """
        PyTube Method
        Needs the entire song_path
        """
        print(song_path)
        loop = asyncio.get_event_loop()
        meta_data = loop.run_until_complete(self._get_meta_data_dos(song_path))
        id3 = eyed3.load(song_path)
        id3.tag.title = meta_data["Title"]
        id3.tag.artist = meta_data["Artist"]
        id3.tag.album = meta_data["Album"]
        id3.tag.save()
        new_name = f"{mp3Dir}/{id3.tag.title}.mp3"
        os.rename(song_path, f"{mp3Dir}/{id3.tag.title}.mp3")
        return new_name

    def _library_tab(self):
        """
        Initializes library tab
        """
        self._set_library_page()
        if not self._isLibrarySet:
            for song in self.song_library:
                self._add_song_to_playlist(song, "lib")

        self._isLibrarySet = True

    def _add_track_object(self, identifier, name="Unknown", artist="Unknown", duration=120):
        self.track_dict[identifier] = {
            "Identifier": identifier,
            "Track Number": (len(self.track_dict) + 1),
            "Name": name,
            "Artist": artist,
            "Duration": duration
        }

    def _add_song_to_playlist(self, song, typeOf=None):
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
        self._add_track_object(
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

    def _show_playlist_creation(self):
        self.lineEdit_3.show()

    def _create_playlist(self, playlist_name: str):
        item = QListWidgetItem(playlist_name, self.listWidget)
        item.setSelected(False)

    def _video_tab(self):
        self.stackedWidget_2.setCurrentIndex(2)

    def _set_playlist_page(self):
        self.stackedWidget_2.setCurrentIndex(1)
        if self.listWidget.item(self.listWidget.currentRow()):
            self._playlistNameLabel.setText(self.listWidget.item(self.listWidget.currentRow()).text())
            print(self.listWidget.item(self.listWidget.currentRow()).text())

        self.listWidget.setCurrentItem(None)

    def _set_library_page(self):
        self.stackedWidget_2.setCurrentIndex(3)
        self._libraryLabel.setText("My Library")

    def _library_track_widgets(self):
        for track in range(1000):
            self.library_track_slot = TrackSlot()
            self.verticalLayout_13.addWidget(self.library_track_slot)
            self.library_track_dict[len(self.library_track_dict) + 1] = self.library_track_slot

    def _playlist_track_widgets(self):
        for track in range(1000):
            self.playlist_track_slot = TrackSlot()
            self.verticalLayout_3.addWidget(self.playlist_track_slot)
            self.playlist_track_dict[len(self.playlist_track_dict) + 1] = self.playlist_track_slot
 
    def _playlist_tab(self):
        self._myComputerButton.setStyleSheet("QPushButton {background-color:#282c32; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self._playlistsButton.setStyleSheet("QPushButton {background-color:#393e46; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self.stackedWidget_3.setCurrentIndex(1)

    def _my_computer_tab(self):
        self._playlistsButton.setStyleSheet("QPushButton {background-color:#282c32; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self._myComputerButton.setStyleSheet("QPushButton {background-color:#393e46; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self._hide_playlist_creation()
        self.stackedWidget_3.setCurrentIndex(2)

    def _hide_playlist_creation(self):
        self.lineEdit_3.clear()
        self.lineEdit_3.hide()

    def keyPressEvent(self, event):
        if event.key() == 32:
            self._play_pause()

        if self.search_field.text():
            if event.key() == 16777220:
                self._searchButton.click()
                self.search_field.clear()
        
        if self.lineEdit_3.text():
            if event.key() == 16777220:
                playlist_name = self.lineEdit_3.text()
                self._create_playlist(playlist_name)
                self._hide_playlist_creation()
            if event.key() == 16777216:
                self._hide_playlist_creation()

    def mouseDoubleClickEvent(self, event):
        for track in self.track_dict:
            if track.underMouse():
                self.songs_played.clear()
                self._set_current_song(track)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            for track in self.track_dict:
                if track.underMouse():
                    track_number = self.track_dict[track]["Track Number"]
                    track.styleFrame.setStyleSheet("QFrame {background-color: #393e46; border-radius: 10px;} QLabel {color:#96a4b8;}")
                    self.playlist_track_dict[track_number].setStyleSheet("background-color: black;")
                else:
                    track.styleFrame.setStyleSheet("QFrame {background-color: #22262b; border-radius: 10px;} QLabel {color:#96a4b8;}")
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
    def _log_json_dump(song=None, json_data=None):
        if jsonLogDir.exists() and song:
            log_file = Path(f"{jsonLogDir}/{song}.json")
            with log_file.open("w") as file:
                json.dump(json_data, file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = PiMono()
    widget.show()
    sys.exit(app.exec())
