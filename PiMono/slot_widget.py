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
from PyQt5.QtWidgets import (QApplication, QFrame, QHBoxLayout, QSizePolicy,
    QWidget)

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
