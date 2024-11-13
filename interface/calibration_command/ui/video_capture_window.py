import cv2
import time
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
from PyQt6.QtGui import QPixmap

from assets.assets import app_logo_png


class VideoCaptureWindow(QWidget):
    def __init__(self, image_width: int = 1920, image_height: int = 1080):
        super().__init__()
        # Create label for video frame and set the default pixmap
        self.frame_label = QLabel("Video Capture Window")
        self.pixmap = QtGui.QPixmap('interface/calibration_command/ui/default_video_frame.png')
        self.frame_label.setPixmap(self.pixmap)
        self.frame_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setWindowIcon(QtGui.QIcon(app_logo_png))

        # set flash timer
        self.flash_timer = time.time()
        self.flash_active = False

        # set move overlay timer
        self.text_overlay_timer = time.time()
        self.text_overlay_active = False
        self.text_overlay_text = "Move"

        # coverage overlay frame
        self.coverage_overlay_frame = np.zeros((image_height, image_width, 3), np.uint8)

        # set margin of window to 0
        self.setContentsMargins(0, 0, 0, 0)

        # Aspect ratio of the video frame
        self._image_width = image_width
        self._image_height = image_height
        self._aspect_ratio = self._image_width / self._image_height
        # Height of the top label
        self.top_label_height = 40
        self.top_label_font_size = 38

        self.setupUi()

        self.setMinimumSize(1, 1)
        self.resize(960, 540)

        self.installEventFilter(self)
        event = QtCore.QEvent(QtCore.QEvent.Type.Resize)
        self.eventFilter(self, event)

    def setupUi(self):
        # Set window title to Video Capture Window
        self.setWindowTitle("Video Capture Window")
        # Create main layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        # make horizontal layout for top labels
        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        # Create label for focus and zoom values
        self.left_label = QLabel()
        self.left_label.setFixedHeight(self.top_label_height)
        self.left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_label.setStyleSheet(f"color: red; background-color: black; font-size: {self.top_label_font_size}px")
        self.top_layout.addWidget(self.left_label)
        # Create label for info text
        self.center_label = QLabel()
        self.center_label.setFixedHeight(self.top_label_height)
        self.center_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_label.setStyleSheet(f"color: red; background-color: black; font-size: {self.top_label_font_size}px")
        self.top_layout.addWidget(self.center_label)
        # Create label for status text
        self.right_label = QLabel()
        self.right_label.setFixedHeight(self.top_label_height)
        self.right_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_label.setStyleSheet(f"color: red; background-color: black; font-size: {self.top_label_font_size}px")
        self.top_layout.addWidget(self.right_label)
        # capture button
        self.capture_button = QtWidgets.QPushButton("Capture")
        self.capture_button.setFixedHeight(self.top_label_height)
        self.capture_button.setFixedWidth(100)
        self.top_layout.addWidget(self.capture_button)
        # Add top layout and video frame to main layout
        self.layout.addLayout(self.top_layout)
        self.layout.addWidget(self.frame_label)
        self.setLayout(self.layout)

    def resetUi(self):
        self.frame_label.setPixmap(QtGui.QPixmap('interface/calibration_command/ui/default_video_frame.png'))

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.resetUi()
        super().closeEvent(event)

    def updateCenterLabel(self, text: str, sample_success: bool = False):
        if sample_success:
            self.center_label.setStyleSheet(f"color: green; background-color: green; font-size: {self.top_label_font_size}px")
            self.center_label.setText(text)
        else:
            self.center_label.setStyleSheet(f"color: red; background-color: black; font-size: {self.top_label_font_size}px")
            self.center_label.setText(text)

    def updateLeftLabel(self, text: str, sample_success: bool = False):
        if sample_success:
            self.left_label.setStyleSheet(f"color: green; background-color: green; font-size: {self.top_label_font_size}px")
            self.left_label.setText(text)
        else:
            self.left_label.setStyleSheet(f"color: red; background-color: black; font-size: {self.top_label_font_size}px")
            self.left_label.setText(text)

    def updateRightLabel(self, text: str, sample_success: bool = False):
        if sample_success:
            self.right_label.setStyleSheet(f"color: green; background-color: green; font-size: {self.top_label_font_size}px")
            self.right_label.setText(text)
        else:
            self.right_label.setStyleSheet(f"color: red; background-color: black; font-size: {self.top_label_font_size}px")
            self.right_label.setText(text)

    def clearTopLabels(self):
        self.updateCenterLabel("")
        self.updateLeftLabel("")
        self.updateRightLabel("")

    def addImagePointsToCoverageOverlay(self, image_points: np.array):
        colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255), (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0), (128, 0, 128)]
        num_points = len(image_points)
        for i in range(num_points):
            cv2.circle(self.coverage_overlay_frame, (int(image_points[i][0][0]), int(image_points[i][0][1])), 5, colors[i % 12], -1)

        for i in range(num_points - 1):
            cv2.line(self.coverage_overlay_frame, (int(image_points[i][0][0]), int(image_points[i][0][1])), (int(image_points[i + 1][0][0]), int(image_points[i + 1][0][1])), colors[i % 12], 2)

    def clearCoverageOverlay(self):
        self.coverage_overlay_frame = np.zeros((self._image_height, self._image_width, 3), np.uint8)

    def changeResolution(self, image_width: int, image_height: int):
        self._image_width = image_width
        self._image_height = image_height
        self._aspect_ratio = image_width / image_height
        self.clearCoverageOverlay()
        event = QtCore.QEvent(QtCore.QEvent.Type.Resize)
        self.eventFilter(self, event)

    def calculateNewSizeFromAspectRatio(self) -> tuple[int, int]:
        width = self.width()
        new_width = width
        new_height = round((width / self._aspect_ratio) + self.top_label_height)
        return new_width, new_height
    
    def flashFrame(self):
        self.flash_active = True
        self.flash_timer = time.time()

    def showTextOverlay(self, text: str = "Move"):
        self.text_overlay_active = True
        self.text_overlay_timer = time.time()
        self.text_overlay_text = text
    
    def updatePixmap(self, frame: np.array):
        frame = self.flashPipe(frame)
        frame = self.TextOverlayPipe(frame)
        frame = self.imagePointsCoveragePipe(frame)
        self.pixmap = self.convertFrameToQPixmap(frame)
        new_width, new_height = self.calculateNewSizeFromAspectRatio()
        self.frame_label.setPixmap(self.pixmap.scaled(new_width, new_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def flashPipe(self, frame: np.array) -> np.array:
        if self.flash_active:
            framec = np.copy(frame)
            flash_time_diff = time.time() - self.flash_timer
            if flash_time_diff < 1:
                # flash alpha starts at 255 and decreases to 0
                alpha = 255 - (flash_time_diff * 255)
                # add white overlay to frame that starts at 255 and decreases to 0
                framec[:, :, :] = (framec * (1 - alpha / 255) + alpha).astype(np.uint8)
                # add green border to frame
                two_percent_frame = round(framec.shape[0] * 0.02)
                framec[0:two_percent_frame, :, :] = [0, 255, 0]
                framec[framec.shape[0] - two_percent_frame:framec.shape[0], :, :] = [0, 255, 0]
                framec[:, 0:two_percent_frame, :] = [0, 255, 0]
                framec[:, framec.shape[1] - two_percent_frame:framec.shape[1], :] = [0, 255, 0]
                return framec
            else:
                self.flash_active = False
                return frame
        return frame
    
    def TextOverlayPipe(self, frame: np.array) -> np.array:
        if self.text_overlay_active:
            framec = np.copy(frame)
            move_overlay_time_diff = time.time() - self.text_overlay_timer
            if move_overlay_time_diff < 5:
                # draw a black rectangle at the center of the frame for the text to be displayed on
                framec[round(framec.shape[0] * 0.4):round(framec.shape[0] * 0.6), round(framec.shape[1] * 0.20):round(framec.shape[1] * 0.80), :] = [0, 0, 0]
                # add text to the frame
                letter_width = framec.shape[1] * (42 / 1920)
                letter_height = framec.shape[0] * (50 / 1080)
                horizontal_offset = round((len(self.text_overlay_text) * letter_width) / 2)
                vertical_offset = round(letter_height / 2)
                cv2.putText(framec, self.text_overlay_text, ((round(framec.shape[1] * 0.5) - horizontal_offset), round((framec.shape[0] * 0.5) + vertical_offset)), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 255), 4, cv2.LINE_AA)
                return framec
            else:
                self.text_overlay_active = False
                return frame
        return frame
    
    def imagePointsCoveragePipe(self, frame: np.array) -> np.array:
        framec = np.copy(frame)
        framec = cv2.addWeighted(framec, 1, self.coverage_overlay_frame, 0.5, 0)
        return framec

    def convertFrameToQPixmap(self, frame):
        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        qt_frame = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format.Format_BGR888)
        return QPixmap.fromImage(qt_frame)

    def resizeWindow(self, width: int, height: int):
        # calculate 10% of the height
        self.top_label_height = max(round(height * 0.05), 25)
        self.top_label_font_size = round(self.top_label_height * 0.65)
        self.center_label.setFixedHeight(self.top_label_height)
        self.center_label.setStyleSheet(f"color: red; background-color: black; font-size: {self.top_label_font_size}px")
        self.left_label.setFixedHeight(self.top_label_height)
        self.left_label.setStyleSheet(f"color: red; background-color: black; font-size: {self.top_label_font_size}px")
        self.right_label.setFixedHeight(self.top_label_height)
        self.right_label.setStyleSheet(f"color: red; background-color: black; font-size: {self.top_label_font_size}px")
        self.capture_button.setFixedHeight(self.top_label_height)
        self.resize(width, height)

    def eventFilter(self, widget: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.Resize:
            new_width, new_height = self.calculateNewSizeFromAspectRatio()
            self.resizeWindow(new_width, new_height)
            return True
        return super().eventFilter(widget, event)
