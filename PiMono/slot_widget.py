from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QHBoxLayout, QWidget


class TrackSlot(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setMinimumSize(QSize(765, 55))
        self.setMaximumSize(QSize(16777215, 55))
        self.setStyleSheet("""QFrame {color:#22262b; border-radius: 10px;}
                           QLabel {color:#96a4b8;}"""
        )
        self.ts_horizontalLayout = QHBoxLayout(self)
        self.ts_horizontalLayout.setObjectName(u"ts_horizontalLayout")
        self.ts_horizontalLayout.setContentsMargins(0, 0, 0, 0)
