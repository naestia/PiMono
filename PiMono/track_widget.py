# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'track.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PyQt5.QtWidgets import (QLabel, QApplication, QFrame, QHBoxLayout, QSizePolicy,
    QWidget)

class NewTrack(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setObjectName("track")
        self.setMinimumSize(QSize(765, 55))
        self.setMaximumSize(QSize(16777215, 55))
        self.setStyleSheet("QFrame {color:#22262b; border-radius: 10px;} QLabel {color:#96a4b8;}"
        )
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(12)
        font.setBold(False)
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 5, 5, 6)
        self.ID = QLabel()
        self.ID.setFont(font)
        self.ID.setObjectName(u"ID")
        self.ID.setMinimumSize(QSize(44, 44))
        self.ID.setMaximumSize(QSize(44, 44))

        self.horizontalLayout.addWidget(self.ID)

        self.art = QLabel()
        self.art.setFont(font)
        self.art.setObjectName(u"art")
        self.art.setMinimumSize(QSize(44, 44))
        self.art.setMaximumSize(QSize(44, 44))

        self.horizontalLayout.addWidget(self.art)

        self.name = QLabel()
        self.name.setFont(font)
        self.name.setObjectName(u"name")
        self.name.setMinimumSize(QSize(200, 0))

        self.horizontalLayout.addWidget(self.name)

        self.artist = QLabel()
        self.artist.setFont(font)
        self.artist.setObjectName(u"artist")

        self.horizontalLayout.addWidget(self.artist)

        self.duration = QLabel()
        self.duration.setFont(font)
        self.duration.setObjectName(u"duration")
        self.duration.setMinimumSize(QSize(70, 0))
        self.duration.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout.addWidget(self.duration)
