import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QObject
from PyQt6 import QtCore

from interface.app.main_window import Ui_MainWindow as MainWindow
from interface.connection.capture_connection.capture_context_manager import CaptureContextManager
from interface.connection.serial_connection.serial_context_manager import SerialContextManager
from interface.connection.metadata_connection.metadata_context_manager import MetadataContextManager
from interface.session.calibration_session import CalibrationSession
from interface.toolbar.export.calibration_export import CalibrationExport

from assets.assets import new, open, save, saveas, export, settings, collect, calculate

# Class CalibrationToolbarController
# Controls the toolbar UI and exposes signals for when the user interacts with the toolbar
class CalibrationToolbarController(QObject):
    # expose signals
    session_opened = QtCore.pyqtSignal(name="CalibrationSessionLoaded")
    session_saved = QtCore.pyqtSignal(name="CalibrationSessionSaved")
    session_new = QtCore.pyqtSignal(name="CalibrationSessionNew")
    session_exported = QtCore.pyqtSignal(name="CalibrationSessionExported")
    session_settings = QtCore.pyqtSignal(name="CalibrationSessionSettings")
    session_gathered = QtCore.pyqtSignal(name="CalibrationSessionGathered")
    session_calculated = QtCore.pyqtSignal(name="CalibrationSessionCalculated")

    def __init__(self, mw: MainWindow, session: CalibrationSession, scm: SerialContextManager, mcm: MetadataContextManager, ccm: CaptureContextManager):
        super().__init__()
        self.mw = mw
        self.ccm = ccm
        self.scm = scm
        self.mcm = mcm
        self.session = session
        self.session_file_path = ""
        # toolbar buttons
        self.TB_new = self.mw.TB_CalibrationNewToolButton
        self.TB_open = self.mw.TB_CalibrationOpenToolButton
        self.TB_save = self.mw.TB_CalibrationSaveToolButton
        self.TB_save_as = self.mw.TB_CalibrationSaveAsToolButton
        self.TB_gather = self.mw.TB_CalibrationGatherToolButton
        self.TB_calc = self.mw.TB_CalibrationCalculateToolButton
        self.TB_export = self.mw.TB_CalibrationExportToolButton
        self.TB_settings = self.mw.TB_CalibrationSettingsToolButton
        self.SB_cb_rows = self.mw.SB_CalibrationCheckerboardRowsValueSpinBox
        self.SB_cb_cols = self.mw.SB_CalibrationCheckerboardColumnsValueSpinBox
        # settings controller and dialog
        self.settings = self.mw.settings_controller
        self.settings_dialog = self.mw.settings_dialog
        self.setupUi()
        self.connectSignalsSlots()

    def setupUi(self):
        # set icons and enable/disable toolbar buttons
        self.TB_new.setIcon(QIcon(new))
        self.TB_open.setIcon(QIcon(open))
        self.TB_save.setIcon(QIcon(save))
        self.TB_save_as.setIcon(QIcon(saveas))
        self.TB_gather.setIcon(QIcon(collect))
        self.TB_calc.setIcon(QIcon(calculate))
        self.TB_export.setIcon(QIcon(export))
        self.TB_settings.setIcon(QIcon(settings))
        self.TB_new.setEnabled(True)
        self.TB_open.setEnabled(True)
        self.TB_save.setEnabled(True)
        self.TB_save_as.setEnabled(True)
        self.TB_gather.setEnabled(False)
        self.TB_export.setEnabled(True)
        self._updateSessionProperties()

    def connectSignalsSlots(self):
        # context manager signals
        self.scm.port_opened.connect(self._onSerialOpened)
        self.scm.port_closed.connect(self._onSerialClosed)
        self.mcm.socket_opened.connect(self._onMetadataOpened)
        self.mcm.socket_closed.connect(self._onMetadataClosed)
        self.ccm.socket_opened.connect(self._onCaptureOpened)
        self.ccm.socket_closed.connect(self._onCaptureClosed)
        # toolbar signals
        self.TB_new.clicked.connect(self._onNewSessionClicked)
        self.TB_open.clicked.connect(self._onOpenSessionClicked)
        self.TB_save.clicked.connect(self._onSaveSessionClicked)
        self.TB_save_as.clicked.connect(self._onSaveSessionAsClicked)
        self.TB_export.clicked.connect(self._onExportSessionClicked)
        self.TB_settings.clicked.connect(self._onSettingsClicked)
        self.SB_cb_rows.valueChanged.connect(self._onCheckerboardRowsChanged)
        self.SB_cb_cols.valueChanged.connect(self._onCheckerboardColumnsChanged)

        self.session.lens_encoder_fitted.connect(self._onLensEncoderFitted)
        self.session.lens_encoder_cleared.connect(self._onLensEncoderCleared)

    def _updateSessionProperties(self):
        # Update file path label
        if self.session_file_path:
            self.mw.L_CalibrationPropertiesFilenameLabel.setText(os.path.basename(self.session_file_path))
        else:
            self.mw.L_CalibrationPropertiesFilenameLabel.setText("None")
        # Update checkerboard rows and columns
        self.SB_cb_rows.setValue(self.session.settings.get_checkerboard_rows())
        self.SB_cb_cols.setValue(self.session.settings.get_checkerboard_columns())

    def _onSerialOpened(self):
        if self.mcm.context.is_running() and self.mcm.context.is_running() and self.ccm.context.is_running() and self.session.lem.focus_is_fitted():
            self.TB_gather.setEnabled(True)

    def _onSerialClosed(self):
        self.TB_gather.setEnabled(False)

    def _onMetadataOpened(self):
        if self.scm.context.is_running() and self.mcm.context.is_running() and self.ccm.context.is_running() and self.session.lem.focus_is_fitted():
            self.TB_gather.setEnabled(True)

    def _onMetadataClosed(self):
        self.TB_gather.setEnabled(False)

    def _onCaptureOpened(self):
        if self.scm.context.is_running() and self.mcm.context.is_running() and self.ccm.context.is_running() and self.session.lem.focus_is_fitted():
            self.TB_gather.setEnabled(True)

    def _onCaptureClosed(self):
        self.TB_gather.setEnabled(False)

    def _onLensEncoderCleared(self):
        if not self.session.is_new:
            self.session.dirty = True
        self.TB_gather.setEnabled(False)

    def _onLensEncoderFitted(self):
        self.session.dirty = True
        if self.scm.context.is_running() and self.mcm.context.is_running() and self.ccm.context.is_running():
            self.TB_gather.setEnabled(True)

    def _onNewSessionClicked(self):
        self.mw.PB_CalibrationProgressBar.setValue(0)
        self.session_file_path = ""
        self.session.is_new = True
        self.session.dirty = False
        new_session = CalibrationSession()
        self.session.copy(new_session)
        self.session_file_path = ""
        self._updateSessionProperties()
        self.mw.L_CalibrationPropertiesFilenameLabel.setText("untitled.json")
        self.session.session_file_new.emit()

    def _onOpenSessionClicked(self):
        home_path = os.path.expanduser("~")
        file_dialog = QFileDialog(self.mw, "Open Calibration Session", home_path, "JSON files (*.json)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)
        if file_dialog.exec():
            try:
                file_path = file_dialog.selectedFiles()[0]
                new_session = CalibrationSession.from_file(file_path)
                self.session.copy(new_session)
            except Exception as e:
                print(e)
                return
            self.mw.PB_CalibrationProgressBar.setValue(0)
            self.session.is_new = False
            self.session_file_path = file_path
            self.session.session_file_loaded.emit()
            self._updateSessionProperties()

    def _onSaveSessionClicked(self):
        if self.session.is_new:
            self._onSaveSessionAsClicked()
        elif self.session.dirty:
            self.session.to_file(self.session_file_path)
            self.session.dirty = False
            self.session.session_file_saved.emit()
        else:
            pass

    def _onSaveSessionAsClicked(self):
        filename = self.mw.L_CalibrationPropertiesFilenameLabel.text()
        home_path = os.path.expanduser("~")
        file_dialog = QFileDialog.getSaveFileName(self.mw, "Save Calibration Session", home_path + f"/{filename}", "JSON files (*.json)")
        if file_dialog[0] != "":
            self.session_file_path = file_dialog[0]
            self.session.to_file(self.session_file_path)
            self.session.dirty = False
            self.session.is_new = False
            self._updateSessionProperties()
            self.session.session_file_saved.emit()

    def _onExportSessionClicked(self):
        filename = "untitled.ulens"
        exporter = CalibrationExport()
        home_path = os.path.expanduser("~")
        file_dialog = QFileDialog.getSaveFileName(self.mw, "Export Calibration Session", home_path + f"/{filename}", "uLens files (*.ulens)")
        if file_dialog[0] != "":
            exporter.export_session(self.session, file_dialog[0])

    def _onSettingsClicked(self):
        self.settings.show()

    def _onCheckerboardRowsChanged(self, value):
        self.settings._onCheckerboardSizeRowsSpinBoxChanged(value)

    def _onCheckerboardColumnsChanged(self, value):
        self.settings._onCheckerboardSizeColumnsSpinBoxChanged(value)
