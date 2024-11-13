import sys, traceback
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable

from network.serial_context import SerialContext
from network.metadata_context import MetadataContext


class RunLensEncoderException(Exception):
    pass

class LensEncoderFitDataException(Exception):
    pass


class RunLensEncoderWorkerSignals(QObject):
    run_started = pyqtSignal()
    run_lem_cleared = pyqtSignal()
    run_sampled = pyqtSignal()
    run_success = pyqtSignal()
    run_error = pyqtSignal(tuple)
    run_finished = pyqtSignal()


class RunLensEncoderWorker(QRunnable):
    def __init__(self, fn, serial_context: SerialContext, metadata_context: MetadataContext, *args, **kwargs):
        super(RunLensEncoderWorker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = RunLensEncoderWorkerSignals()

        self.kwargs['sc'] = serial_context
        self.kwargs['mc'] = metadata_context
        self.kwargs['signals'] = self.signals

    @pyqtSlot()
    def run(self):
        try:
            self.signals.run_started.emit()
            self.fn(
                *self.args, **self.kwargs,
            )
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            self.signals.run_error.emit((exc_type, exc_value, traceback.format_tb(exc_tb)))
        else:
            self.signals.run_success.emit()
        finally:
            self.signals.run_finished.emit()
