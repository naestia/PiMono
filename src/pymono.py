import sys
import os

import requests
import time
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLineEdit, QPushButton, QListWidgetItem
from PyQt6.QtGui import QPixmap, QColor, QPainter, QBrush
from PyQt6.QtCore import Qt
from PyQt6 import uic
from pytube import YouTube, Search

from track_widget import NewTrack
from settings import *
from slot_widget import TrackSlot


class PiMono(QWidget):
    def __init__(self, *args, **kwargs):
        """
        Most of the methods in this class are test methods for development.
        
        At the moment, the GUI is still under development so the actual code
        will not be prioritized.
        """
        super(PiMono, self).__init__(*args, **kwargs)
        # Load form.ui to get the GUI
        uic.loadUi("form.ui", self)
        self.file_path = os.path.dirname(os.path.abspath(__file__))
        self.track_dict = {}
        self.playlist_track_dict = {}
        self.library_track_dict = {}
        self.search_results = []
        self.result_index = 0
        self.w = None

        # Running methods as initialization
        self._playlist_track_widgets()
        self._library_track_widgets()
        
        # Setting page indexes for initialization
        self.stackedWidget_2.setCurrentIndex(0)
        self.stackedWidget_3.setCurrentIndex(0)
        self.stackedWidget_4.setCurrentIndex(1)

        # Setting placeholder text for line edit fields
        self.lineEdit.setPlaceholderText("Search...")
        self.lineEdit_3.setPlaceholderText("Playlist Name...")
        self.search_field.setPlaceholderText("Enter YouTube Search...")
        self.lineEdit_3.hide()

        self.convert_button.clicked.connect(self._video_tab)
        self.library_button.clicked.connect(self._playlist_tab)
        self.menu_playlists.clicked.connect(self._playlist_tab)
        self.menu_computer.clicked.connect(self._my_computer_tab)
        self.new_playlist.clicked.connect(self._show_playlist_creation)
        self.pushButton.clicked.connect(self._search_youtube)
        self.previous_result_button.hide()
        self.next_result_button.hide()
        self.previous_result_button.clicked.connect(self._show_previous_result)
        self.next_result_button.clicked.connect(self._show_next_result)

        self.listWidget.itemDoubleClicked.connect(self._test)
        self._push()
        

    def _show_previous_result(self):
        self.result_index -= 1
        self._display_results()

    def _show_next_result(self):
        if self.result_index == (len(self.search_result) - 1):
            self.result_index = 0
        else:
            self.result_index += 1
        
        self._display_results()

    def _display_results(self):
        self.yt_video = self.search_result[self.result_index]
        title = self.yt_video.title
        thumbnail_url = self.yt_video.thumbnail_url
        video_details = self.yt_video.vid_info.get("videoDetails")
        video_id = video_details.get("videoId")


        self._set_result_thumbnail(thumbnail_url, video_id)
        
        self.video_title.setText(title)
        self.video_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.download_button.setText("Download")
        self.previous_result_button.show()
        self.next_result_button.show()


    def _set_result_thumbnail(self, url, vid_id):
        data = requests.get(url).content
        img_name = f"{vid_id}.jpg"
        img_path = f"{THUMBNAIL_DIR}/{img_name}"
        if not os.path.exists(img_path):
            with open(f"{img_path}", "wb") as file:
                file.write(data)

        self.label_5.setStyleSheet(f"border-image: url('{THUMBNAIL_DIR}/{img_name}');")
        

    def _search_youtube(self):
        if self.search_field.text():
            search = Search(self.search_field.text())
            self.search_result = search.results
            self.result_index = 0
            self._display_results()
            

    def _download_from_youtube(self, yt):
        video = yt.streams.filter().get_highest_resolution()
        destination = f"{self.file_path}/../music/mp4"
        video.download(output_path=destination)

    def _library_tab(self):
        self.stackedWidget_2.setCurrentIndex(3)

    def _show_playlist_creation(self):
        self.lineEdit_3.show()

    def _create_playlist(self, playlist_name):
        item = QListWidgetItem(playlist_name, self.listWidget)
        item.setSelected(False)

    def _video_tab(self):
        self.stackedWidget_2.setCurrentIndex(2)

    def _test(self):
        self.stackedWidget_2.setCurrentIndex(1)
        self.playlist_name.setText(self.listWidget.item(self.listWidget.currentRow()).text())
        print(self.listWidget.item(self.listWidget.currentRow()).text())
        self.listWidget.setCurrentItem(None)

    def _library_track_widgets(self):
        for track in range(100):
            self.library_track_slot = TrackSlot()
            self.verticalLayout_11.addWidget(self.library_track_slot)
            self.library_track_dict[len(self.library_track_dict) + 1] = self.library_track_slot


    def _playlist_track_widgets(self):
        for track in range(100):
            self.playlist_track_slot = TrackSlot()
            self.verticalLayout_3.addWidget(self.playlist_track_slot)
            self.playlist_track_dict[len(self.playlist_track_dict) + 1] = self.playlist_track_slot
 
    def _playlist_tab(self):
        self.menu_computer.setStyleSheet("QPushButton {background-color:#282c32; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self.menu_playlists.setStyleSheet("QPushButton {background-color:#393e46; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self.stackedWidget_3.setCurrentIndex(1)
        
    
    def _my_computer_tab(self):
        self.menu_playlists.setStyleSheet("QPushButton {background-color:#282c32; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self.menu_computer.setStyleSheet("QPushButton {background-color:#393e46; color:#96a4b8;}\n"
            "QPushButton::hover {color:#c3d5f1;}\n"
            "QPushButton:pressed {color:white;}"
        )
        self._hide_playlist_creation()
        self.stackedWidget_3.setCurrentIndex(2)
        

    def _push(self):
        index = len(self.track_dict) + 1
        self.new_track = NewTrack()
        track_slot = self.playlist_track_dict.get(index)
        track_slot.ts_horizontalLayout.addWidget(self.new_track)
        self.track_dict[self.new_track] = [len(self.track_dict) + 1, "url", "Random song name", "Random artist", "3:11"]
        if self.track_dict[self.new_track][0] < 10:
            self.new_track.ID.setText(f"    {str(self.track_dict[self.new_track][0])}")
        else:
            self.new_track.ID.setText(f"   {str(self.track_dict[self.new_track][0])}")
        self.new_track.name.setText(f"   {str(self.track_dict[self.new_track][2])}")
        self.new_track.artist.setText(f"   {str(self.track_dict[self.new_track][3])}")
        self.new_track.duration.setText(f"   {str(self.track_dict[self.new_track][4])}")

    def _push_2(self):
        for track in self.track_dict:
            pass

        print(self.track_dict)

    def _hide_playlist_creation(self):
        self.lineEdit_3.clear()
        self.lineEdit_3.hide()

    def keyPressEvent(self, event):
        # print(event.key())

        if self.search_field.text():
            if event.key() == 16777220:
                self.pushButton.click()
        
        if self.lineEdit_3.text():
            if event.key() == 16777220:
                playlist_name = self.lineEdit_3.text()
                self._create_playlist(playlist_name)
                self._hide_playlist_creation()
            if event.key() ==  16777216:
                self._hide_playlist_creation()

    def mouseDoubleClickEvent(self, event):
        for track in self.track_dict:
            if track.underMouse():
                print(track)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            for track in self.track_dict:
                if track.underMouse():
                    track.setStyleSheet("QWidget {background-color: #393e46; border-radius: 10px;} QLabel {color:#96a4b8;}")
                else:
                    track.setStyleSheet("QWidget {background-color: #22262b; border-radius: 10px;} QLabel {color:#96a4b8;}")
            if self.listWidget.currentItem():
                self.listWidget.setCurrentItem(None)
        elif event.button() == Qt.MouseButton.RightButton:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = PiMono()
    widget.show()
    sys.exit(app.exec())
