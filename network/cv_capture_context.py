import threading
import cv2
import time
import numpy as np

# Base exception class for capture context
class CvCaptureContextException(Exception):
    pass

# dictionary of corresponding resolution strings and OpenCV VideoCapture resolution codes
RESOLUTIONS = {
    "8k": (7680, 4320),
    "5k": (5120, 2880),
    "4k": (4096, 2160),
    "2160p": (3840, 2160),
    "1440p": (2560, 1440),
    "2k": (2048, 1080),
    "1080p": (1920, 1080),
    "720p": (1280, 720),
    "540p": (960, 540),
}

# Class CaptureContext
# This class is used to maintain the capture context and expose a callback for received frames OpenCV VideoCapture
class CvCaptureContext:
    def __init__(self, index: int=0, frame_width=1920, frame_height=1080, frame_rate=30):

        # OpenCV object variables
        self._index_ = index
        self._frame_width_ = frame_width
        self._frame_height_ = frame_height
        self._frame_rate_ = frame_rate

        # Context information
        self._is_running_ = False
        self._capture_ = None
        self._close_callback_ = lambda: None
        self._open_callback_ = lambda: None

        # Recent frame information
        self._last_frame_ = None

        # Received data thread variables
        self._received_thread_ = None
        self._recv_callback_ = lambda data: None

    def set_index(self, index: int):
        self._index_ = index

    def set_frame_width(self, width: int):
        self._frame_width_ = width

    def get_frame_width(self):
        return self._frame_width_

    def set_frame_height(self, height: int):
        self._frame_height_ = height

    def get_frame_height(self):
        return self._frame_height_

    def set_resolution(self, resolution: str):
        if resolution in RESOLUTIONS:
            self._frame_width_, self._frame_height_ = RESOLUTIONS[resolution]

    def set_frame_rate(self, rate: int):
        self._frame_rate_ = rate

    def get_last_frame(self):
        return self._last_frame_

    def __recv_func__(self, context):
        while context.is_running():
            try:
                ret, frame = context._capture_.read()
                if not ret:
                    continue
                context._last_frame_ = frame
                context._recv_callback_(frame)
            except Exception as e:
                context.close(join=False)
                context._close_callback_()
                context.on_recv_error(e)
        self._close_callback_()

    def on_recv_error(self, error: Exception):
        raise CvCaptureContextException(f"Capture Context Exception: {error}")

    def set_recv_callback(self, callback):
        self._recv_callback_ = callback

    def set_close_callback(self, callback):
        self._close_callback_ = callback

    def set_open_callback(self, callback):
        self._open_callback_ = callback

    def open(self):
        self._capture_ = cv2.VideoCapture(self._index_)

        if not self._capture_.isOpened():
            raise Exception("Could not open the camera {}".format(self._index_))

        self._capture_.set(cv2.CAP_PROP_FRAME_WIDTH, self._frame_width_)
        self._capture_.set(cv2.CAP_PROP_FRAME_HEIGHT, self._frame_height_)
        self._capture_.set(cv2.CAP_PROP_FPS, self._frame_rate_)
        self._received_thread_ = threading.Thread(target=self.__recv_func__, args=(self,))
        self._is_running_ = True
        self._received_thread_.setDaemon(True)
        self._received_thread_.setName("CvCaptureThread")
        self._received_thread_.start()

        for i in range(10):
            time.sleep(0.1)
            if self._last_frame_ is not None:
                break
        if self._last_frame_ is None:
            self.close()
            raise Exception("Camera capture failed to start")

        self._open_callback_()

    def close(self, join=True):
        self._is_running_ = False
        if self._received_thread_ is not None and join:
            self._received_thread_.join()
        if self._capture_ is not None:
            self._capture_.release()

    def is_running(self):
        return self._is_running_
