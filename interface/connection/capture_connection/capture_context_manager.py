import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

from network.ffmpeg_capture_context import FFmpegCaptureContext

# Class CaptureContextManager
# The class registers callbacks for the capture context and emits signals when frames are received or the socket is closed/opened
class CaptureContextManager(QObject):
    frame_received = pyqtSignal(np.ndarray, name='frame_received')
    socket_closed = pyqtSignal(name='frame_closed')
    socket_opened = pyqtSignal(name='frame_opened')

    def __init__(self, capture_context: FFmpegCaptureContext):
        super().__init__()

        self.context = capture_context

        self.context.set_recv_callback(self.data_recv_fn)
        self.context.set_close_callback(self.socket_closed_fn)
        self.context.set_open_callback(self.socket_opened_fn)

    def data_recv_fn(self, frame: np.ndarray):
        self.frame_received.emit(frame)

    def socket_closed_fn(self):
        self.socket_closed.emit()

    def socket_opened_fn(self):
        self.socket_opened.emit()
