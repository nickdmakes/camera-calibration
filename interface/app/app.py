import sys
import os
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt6 import QtGui
import qdarktheme

from interface.app.main_window import Ui_MainWindow
from interface.app.settings_window import Ui_D_CalibrationSettingsDialog
from interface.session.calibration_session import CalibrationSession
from interface.calibration_command.ui.video_capture_window import VideoCaptureWindow
from interface.connection.serial_connection.serial_context_manager import SerialContextManager
from interface.connection.capture_connection.capture_context_manager import CaptureContextManager
from interface.connection.metadata_connection.metadata_context_manager import MetadataContextManager

from assets.assets import app_logo_png, config_path, ffmpeg_path

from network.serial_context import SerialContext
from network.ffmpeg_capture_context import FFmpegCaptureContext
from network.metadata_context import MetadataContext

if sys.platform == 'win32':
    try:
        from ctypes import windll  # Only exists on Windows.
        myappid = 'mycompany.myproduct.subproduct.version'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

def start_app():
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Controller imports must be done here to avoid circular imports
        from interface.toolbar.calibration_toolbar_controller import CalibrationToolbarController
        from interface.toolbar.settings.calibration_settings_controller import CalibrationSettingsController
        from interface.connection.serial_connection.serial_connection_controller import SerialConnectionController
        from interface.connection.capture_connection.capture_connection_controller import CaptureConnectionController
        from interface.connection.metadata_connection.metadata_connection_controller import MetadataConnectionController
        from interface.manual_command.manual_command_controller import ManualCommandController
        from interface.calibration_command.calibration_command_controller import CalibrationCommandController
        from interface.lens_encoder.lens_encoder_controller import LensEncoderController

        self.setupUi(self)

        # Set window attributes
        load_dotenv(dotenv_path=config_path)
        app_name = os.environ.get('APP_NAME')
        app_version = os.environ.get('APP_VERSION')
        self.setWindowTitle(f"{app_name} v{app_version}")
        self.setWindowIcon(QtGui.QIcon(app_logo_png))

        # initialize other windows
        self.vc_window = VideoCaptureWindow()
        self.settings_dialog = SettingsDialog()

        # initialize session object for storing calibration progress
        session = CalibrationSession()

        # initialize context managers
        self.scm = SerialContextManager(serial_context=SerialContext())
        self.serial_connection_controller = SerialConnectionController(self, self.scm)

        self.mcm = MetadataContextManager(metadata_context=MetadataContext())
        self.metadata_connection_controller = MetadataConnectionController(self, self.mcm)

        self.ccm = CaptureContextManager(capture_context=FFmpegCaptureContext(path=ffmpeg_path))
        self.capture_connection_controller = CaptureConnectionController(self, self.ccm, self.vc_window)

        # initialize controllers
        self.settings_controller = CalibrationSettingsController(self, session, self.settings_dialog)
        
        self.toolbar_controller = CalibrationToolbarController(self, session, self.scm, self.mcm, self.ccm)

        self.calibration_command_controller = CalibrationCommandController(self, self.vc_window, session, self.scm, self.mcm, self.ccm)
        self.manual_command_controller = ManualCommandController(self, self.scm, self.mcm)
        self.lens_encoder_controller = LensEncoderController(self, session, self.scm, self.mcm)


    def closeEvent(self, event):
        self.vc_window.close()

        self.scm.context.close(join=True)
        self.mcm.context.close(join=True)
        self.ccm.context.close(join=True)


class SettingsDialog(QDialog, Ui_D_CalibrationSettingsDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
