import time

from PyQt6.QtCore import QThreadPool

from network.cmotion.api import set_motor_pos, send_ping
from network.cmotion.packet import CmotionPacket
from interface.session.models.lens_encoder_model import LensEncoderModel

from interface.connection.serial_connection.serial_context_manager import SerialContextManager
from interface.connection.metadata_connection.metadata_context_manager import MetadataContextManager
from interface.app.main_window import Ui_MainWindow as MainWindow


class ManualCommandController:
    def __init__(self, mw: MainWindow, scm: SerialContextManager, mcm: MetadataContextManager):
        super().__init__()
        self.mw = mw
        self.scm = scm
        self.mcm = mcm
        self.setupUi()
        self.connectSignalsSlots()
        self.threadpool = QThreadPool()

    def setupUi(self):
        pass

    def connectSignalsSlots(self):
        self.scm.port_closed.connect(self._serialConnectionClosed)
        self.scm.data_received.connect(self._serialDataReceived)
        self.mw.HSL_FocusMotorManualSlider.sliderReleased.connect(self._focusMotorManualSliderChanged)
        self.mw.HSL_IrisMotorManualSlider.sliderReleased.connect(self._irisMotorManualSliderChanged)
        self.mw.HSL_ZoomMotorManualSlider.sliderReleased.connect(self._zoomMotorManualSliderChanged)

    def _serialConnectionClosed(self):
        pass

    def _serialDataReceived(self, data):
        pass

    def _focusMotorManualSliderChanged(self):
        value = self.mw.HSL_FocusMotorManualSlider.value()
        set_motor_pos(self.scm.context, value, 'f', 0)

    def _irisMotorManualSliderChanged(self):
        value = self.mw.HSL_IrisMotorManualSlider.value()
        set_motor_pos(self.scm.context, value, 'i', 0)

    def _zoomMotorManualSliderChanged(self):
        value = self.mw.HSL_ZoomMotorManualSlider.value()
        set_motor_pos(self.scm.context, value, 'z', 0)
