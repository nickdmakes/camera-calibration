import cv2
import time
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
from PyQt6.QtGui import QPixmap

from interface.app.main_window import Ui_MainWindow as MainWindow
from assets.assets import default_preview


class CapturePreview(QWidget):
    def __init__(self, main_window: MainWindow):
        super().__init__()
        # Create label for video frame and set the default pixmap
        self.frame = QLabel("Capture Preview")
        self.default_frame = cv2.imread(default_preview)

        # current image being displayed
        self.image = self.default_frame

        self.setupUi()

        self.set_frame(self.image)

        # on main window resize, resize the video frame
        main_window.resizeEvent = self.resizeEvent

    def setupUi(self):
        self.frame.setPixmap(QtGui.QPixmap(default_preview))
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumSize(1, 1)

        # Create label for top of layout
        self.top_label = QLabel("Capture Preview")
        self.setContentsMargins(0, 0, 0, 0)
        self.top_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # gray background with bold white text
        # Also make the corner of the top label square
        self.top_label.setStyleSheet("background-color: #333; color: white; font-weight: bold; border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom-right-radius: 0px; border-bottom-left-radius: 0px")
        self.top_label.setFixedHeight(30)

        # Create layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.top_label)
        self.layout.addWidget(self.frame)
        self.setLayout(self.layout)

        # left, right, and bottom border with color #333
        # top border is 30px and has a gray background with white text that says "Capture Preview"
        self.setStyleSheet("background-color: #333; border-left: 5px solid #333; border-right: 5px solid #333; border-bottom: 5px solid #333; border-top-left-radius: 0px; border-top-right-radius: 0px;")

    def set_frame(self, image: np.array):
        self.image = image
        pixmap = self._convertFrameToQImage(image)
        width, height = self.calcNewImageSize(image)
        self.frame.setFixedSize(width, height)
        self.setMinimumHeight(height + 30)
        pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)
        self.frame.setPixmap(pixmap)

    def reset_frame(self):
        self.set_frame(self.default_frame)

    def calcNewImageSize(self, image: np.array):
        aspect_ratio = image.shape[1] / image.shape[0]

        # if the pixmap height is greater than the height of this widget, calculate the new height based on the aspect ratio
        new_width = self.size().width()
        new_height = new_width / aspect_ratio
        return new_width, new_height

    def resizeEvent(self, event):
        self.set_frame(self.image)

    def _convertFrameToQImage(self, frame):
        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        qt_frame = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format.Format_BGR888)
        return QPixmap.fromImage(qt_frame)
        