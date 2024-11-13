import sys, traceback
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable

from interface.session.models.data_model import CalibrationDataPoint


class RunCameraCalibrationSignals(QObject):
    run_started = pyqtSignal()
    run_sampled = pyqtSignal(CalibrationDataPoint)
    run_success = pyqtSignal()
    run_error = pyqtSignal(tuple)
    run_finished = pyqtSignal()


class RunCameraCalibrationWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(RunCameraCalibrationWorker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = RunCameraCalibrationSignals()

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
