import sys, traceback
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable

from network.serial_context import SerialContext


class ConnectPortWorkerSignals(QObject):
    connect_started = pyqtSignal()
    connect_handshake_success = pyqtSignal()
    connect_success = pyqtSignal()
    connect_finished = pyqtSignal()
    connect_error = pyqtSignal(tuple)


class ConnectPortWorker(QRunnable):
    def __init__(self, fn, serial_context: SerialContext, *args, **kwargs):
        super(ConnectPortWorker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ConnectPortWorkerSignals()

        self.kwargs['serial_context'] = serial_context
        self.kwargs['signals'] = self.signals

    @pyqtSlot()
    def run(self):
        try:
            self.signals.connect_started.emit()
            self.fn(
                *self.args, **self.kwargs,
            )
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            self.signals.connect_error.emit((exc_type, exc_value, traceback.format_tb(exc_tb)))
        else:
            self.signals.connect_success.emit()
        finally:
            self.signals.connect_finished.emit()
