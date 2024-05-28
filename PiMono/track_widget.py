import os

from PyQt5.QtWidgets import QWidget
from PyQt5 import uic


class NewTrack(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.file_path = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(f"{self.file_path}/forms/track.ui", self)
