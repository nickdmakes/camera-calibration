import sys
from PyQt6 import QtGui
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QMessageBox

from interface.app.main_window import Ui_MainWindow as MainWindow
from interface.calibration_command.ui.video_capture_window import VideoCaptureWindow
from interface.connection.capture_connection.capture_context_manager import CaptureContextManager
from interface.connection.capture_connection.workers.connect_capture_worker import ConnectCaptureWorker, ConnectCaptureWorkerSignals
from interface.shared.standard_error_dialog import StandardErrorDialog

from network.ffmpeg_capture_context import FFmpegCaptureContext

from assets.assets import connection_down, connection_up, connection_loading


class CaptureConnectionController:
    def __init__(self, mw: MainWindow, ccm: CaptureContextManager, vc_window: VideoCaptureWindow):
        super().__init__()
        self.mw = mw
        self.ccm = ccm
        self.vc_window = vc_window
        self.setupUi()
        self.connectSignalsSlots()
        self.threadpool = QThreadPool()

    def setupUi(self):
        self._onCaptureConnectionClosed()

        self.mw.CB_CaptureInterfaceModeComboBox.addItems(self.ccm.context.get_interface_mode_list())
        self._onCaptureInterfaceModeChanged(0)

        # Attach the close event of the context manager to the close event of the video capture window
        self.vc_window.closeEvent = self.ccm.context.close

    def connectSignalsSlots(self):
        self.ccm.socket_closed.connect(self._onCaptureConnectionClosed)
        self.ccm.socket_opened.connect(self._onCaptureConnectionOpened)
        self.mw.CB_CaptureInterfaceModeComboBox.currentIndexChanged.connect(self._onCaptureInterfaceModeChanged)
        self.mw.CB_CaptureConnectionDeviceComboBox.currentIndexChanged.connect(self._onCaptureDeviceChanged)
        self.mw.CB_CaptureConnectionFormatComboBox.currentIndexChanged.connect(self._onCaptureFormatChanged)
        self.mw.B_ConnectCaptureButton.clicked.connect(self._onConnectCaptureButtonClicked)

    def _onCaptureConnectionClosed(self):
        self.mw.L_CaptureConnectionStatusIcon.setPixmap(QtGui.QPixmap(connection_down))
        self._setConfigurationEnabled(True)
        self.mw.B_ConnectCaptureButton.setText("Capture")
        self.mw.B_ConnectCaptureButton.setEnabled(True)
        self.vc_window.close()

    def _onCaptureConnectionOpened(self):
        self.mw.L_CaptureConnectionStatusIcon.setPixmap(QtGui.QPixmap(connection_up))
        self._setConfigurationEnabled(False)
        self.mw.B_ConnectCaptureButton.setText("Stop")
        self.mw.B_ConnectCaptureButton.setEnabled(True)
        self.vc_window.show()

    def _onCaptureInterfaceModeChanged(self, index):
        if index == -1:
            return
        self.ccm.context.set_interface_mode_index(index)
        self.mw.CB_CaptureConnectionDeviceComboBox.clear()
        self.mw.CB_CaptureConnectionFormatComboBox.clear()
        self.ccm.context.update_devices()
        if not self.ccm.context.no_devices_found():
            self.ccm.context.set_selected_device_index(0)
            self.mw.CB_CaptureConnectionDeviceComboBox.addItems(self.ccm.context.get_device_list())
            self.ccm.context.update_formats()
            if not self.ccm.context.no_formats_found():
                self.ccm.context.set_selected_format_index(0)
                self.mw.CB_CaptureConnectionFormatComboBox.addItems(self.ccm.context.get_format_list())

    def _onCaptureDeviceChanged(self, index):
        if index == -1:
            return
        self.ccm.context.set_selected_device_index(index)
        self.mw.CB_CaptureConnectionFormatComboBox.clear()
        self.ccm.context.update_formats()
        if not self.ccm.context.no_formats_found():
            self.ccm.context.set_selected_format_index(0)
            self.mw.CB_CaptureConnectionFormatComboBox.addItems(self.ccm.context.get_format_list())

    def _onCaptureFormatChanged(self, index):
        if index == -1:
            return
        self.ccm.context.set_selected_format_index(index)
        # Update the aspect ratio of the video capture window
        width = self.ccm.context.get_selected_format().width
        height = self.ccm.context.get_selected_format().height
        self.vc_window.changeResolution(width, height)

    def _onConnectCaptureButtonClicked(self):
        if self.ccm.context.no_devices_found():
            self._noDevicesError()
            return

        if self.ccm.context.is_running():
            self.ccm.context.close()
        else:
            worker = self.makeConnectCaptureWorker()
            self.threadpool.start(worker)

    def connectCapture_fn(self, capture_context: FFmpegCaptureContext, signals: ConnectCaptureWorkerSignals):
        capture_context.open()

    def makeConnectCaptureWorker(self):
        worker = ConnectCaptureWorker(self.connectCapture_fn, self.ccm.context)
        worker.signals.connect_started.connect(self._s_connectStarted)
        worker.signals.connect_success.connect(self._s_connectSuccess)
        worker.signals.connect_finished.connect(self._s_connectFinished)
        worker.signals.connect_error.connect(self._s_connectError)
        return worker
    
    def _setConfigurationEnabled(self, enabled: bool):
        self.mw.CB_CaptureInterfaceModeComboBox.setEnabled(enabled)
        self.mw.CB_CaptureConnectionFormatComboBox.setEnabled(enabled)
        self.mw.CB_CaptureConnectionDeviceComboBox.setEnabled(enabled)
    
    def _s_connectStarted(self):
        self._setConfigurationEnabled(False)
        self.mw.B_ConnectCaptureButton.setEnabled(False)
        self.mw.L_CaptureConnectionStatusIcon.setPixmap(QtGui.QPixmap(connection_loading))

    def _s_connectSuccess(self):
        pass

    def _s_connectFinished(self):
        pass

    def _s_connectError(self, error):
        self._onCaptureConnectionClosed()
        StandardErrorDialog(
            title="Capture Connection Error",
            message="Failed to connect to video capture device",
            details="Make sure the camera is connected to a decklink capture device and the format is supported"
        )
    
    def _noDevicesError(self):
        StandardErrorDialog(
            title="Capture Connection Error",
            message="No video capture devices found",
            details="Make sure there is a Decklink capture device connected to the system and the drivers are installed properly"
        )
