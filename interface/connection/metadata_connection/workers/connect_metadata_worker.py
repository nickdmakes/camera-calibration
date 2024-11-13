import sys, traceback
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable

from network.metadata_context import MetadataContext


class ConnectMetadataWorkerSignals(QObject):
    connect_started = pyqtSignal()
    connect_success = pyqtSignal()
    connect_finished = pyqtSignal()
    connect_error = pyqtSignal(tuple)


class ConnectMetadataWorker(QRunnable):
    def __init__(self, fn, metadata_context: MetadataContext, *args, **kwargs):
        super(ConnectMetadataWorker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ConnectMetadataWorkerSignals()

        self.kwargs['metadata_context'] = metadata_context
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
