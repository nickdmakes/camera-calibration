from PyQt6.QtWidgets import QButtonGroup
from PyQt6.QtCore import QObject
from PyQt6 import QtCore

from interface.app.main_window import Ui_MainWindow as MainWindow
from interface.app.settings_window import Ui_D_CalibrationSettingsDialog as SettingsWindow
from interface.session.calibration_session import CalibrationSession


class CalibrationSettingsController(QObject):
    def __init__(self, mw: MainWindow, session: CalibrationSession, sw: SettingsWindow):
        super().__init__()
        self.mw = mw
        self.sw = sw
        self.session = session
        self.setupUi()
        self.connectSignalsSlots()

    def setupUi(self):
        self.sw.SB_ImageResWidthValueSpinBox.setValue(self.session.settings.get_image_width())
        self.sw.SB_ImageResHeightValueSpinBox.setValue(self.session.settings.get_image_height())
        self.sw.SB_SensorSizeHeightValueSpinBox.setValue(self.session.settings.get_sensor_height())
        self.sw.SB_SensorSizeWidthValueSpinBox.setValue(self.session.settings.get_sensor_width())
        self.sw.SB_MinFocusDistanceSpinBox.setValue(self.session.settings.get_min_focus())
        self.sw.SB_MaxFocusDistanceSpinBox.setValue(self.session.settings.get_max_focus())
        self.sw.SB_FocusPointsValueSpinBox.setValue(self.session.settings.get_num_focus_points())
        self.sw.CB_IsPrimeValueCheckBox.setChecked(self.session.settings.get_is_prime())
        self.sw.SB_PrimeZoomValueSpinBox.setValue(self.session.settings.get_prime_zoom())
        self.sw.SB_MinZoomDistanceSpinBox.setValue(self.session.settings.get_min_zoom())
        self.sw.SB_MaxZoomDistanceSpinBox.setValue(self.session.settings.get_max_zoom())
        self.sw.SB_ZoomPointsValueSpinBox.setValue(self.session.settings.get_num_zoom_points())
        self._setPrimeEnabled(self.session.settings.get_is_prime())
        self.sw.CB_IsPrimeValueCheckBox.setChecked(self.session.settings.get_is_prime())
        self.sw.SB_SamplesPerConfigurationValueSpinBox.setValue(self.session.settings.get_num_images_per_config())
        self.sw.DSP_TimeToHoldStillValueDoubleSpinBox.setValue(self.session.settings.get_time_to_hold_still())
        self.ImageGatherModeButtonGroup = QButtonGroup()
        self.ImageGatherModeButtonGroup.addButton(self.sw.RB_ImageGatherModeTimedRadioButton, 0) # 0 is the id for timed mode
        self.ImageGatherModeButtonGroup.addButton(self.sw.RB_ImageGatherModeManualRadioButton, 1) # 1 is the id for manual mode
        
        # check the radio button id that is stored in the settings
        self.ImageGatherModeButtonGroup.button(self.session.settings.get_image_gather_mode()).setChecked(True)

    def connectSignalsSlots(self):
        self.sw.SB_ImageResWidthValueSpinBox.valueChanged.connect(self._onImageResWidthSpinBoxChanged)
        self.sw.SB_ImageResHeightValueSpinBox.valueChanged.connect(self._onImageResHeightSpinBoxChanged)
        self.sw.SB_SensorSizeHeightValueSpinBox.valueChanged.connect(self._onSensorSizeHeightSpinBoxChanged)
        self.sw.SB_SensorSizeWidthValueSpinBox.valueChanged.connect(self._onSensorSizeWidthSpinBoxChanged)
        self.sw.SB_MinFocusDistanceSpinBox.valueChanged.connect(self._onMinFocusDistanceSpinBoxChanged)
        self.sw.SB_MaxFocusDistanceSpinBox.valueChanged.connect(self._onMaxFocusDistanceSpinBoxChanged)
        self.sw.SB_FocusPointsValueSpinBox.valueChanged.connect(self._onFocusPointsSpinBoxChanged)
        self.sw.CB_IsPrimeValueCheckBox.clicked.connect(self._onIsPrimeCheckBoxChanged)
        self.sw.SB_PrimeZoomValueSpinBox.valueChanged.connect(self._onPrimeZoomSpinBoxChanged)
        self.sw.SB_MinZoomDistanceSpinBox.valueChanged.connect(self._onMinZoomDistanceSpinBoxChanged)
        self.sw.SB_MaxZoomDistanceSpinBox.valueChanged.connect(self._onMaxZoomDistanceSpinBoxChanged)
        self.sw.SB_ZoomPointsValueSpinBox.valueChanged.connect(self._onZoomPointsSpinBoxChanged)
        self.sw.SB_SamplesPerConfigurationValueSpinBox.valueChanged.connect(self._onSamplesPerConfigurationSpinBoxChanged)
        self.sw.DSP_TimeToHoldStillValueDoubleSpinBox.valueChanged.connect(self._onTimeToHoldStillSpinBoxChanged)
        self.ImageGatherModeButtonGroup.buttonClicked.connect(self._onImageGatherModeRadioButtonClicked)

        # session signals
        self.session.lens_encoder_fitted.connect(self._onLensEncoderFitted)
        self.session.session_file_loaded.connect(self._onSessionFileLoaded)
        self.session.session_file_new.connect(self._onSessionFileNew)

    def _onLensEncoderFitted(self):
        # set the min and max values for the focus range as the lem min and max values
        self.sw.SB_MinFocusDistanceSpinBox.setMinimum(self.session.lem.get_min_value("focus")*100)
        self.sw.SB_MaxFocusDistanceSpinBox.setMaximum(self.session.lem.get_max_value("focus")*100)

        # set the min and max values for the ranges as the lem min and max values
        if not self.session.settings.get_is_prime():
            self.sw.SB_MinZoomDistanceSpinBox.setMinimum(self.session.lem.get_min_value("zoom"))
            self.sw.SB_MaxZoomDistanceSpinBox.setMaximum(self.session.lem.get_max_value("zoom"))

    def _onSessionFileLoaded(self):
        self.setupUi()

    def _onSessionFileNew(self):
        self.setupUi()

    def show(self):
        self.sw.exec()

    def _onImageResWidthSpinBoxChanged(self, value: int):
        self.session.settings.set_image_width(value)
        self.session.dirty = True

    def _onImageResHeightSpinBoxChanged(self, value: int):
        self.session.settings.set_image_height(value)
        self.session.dirty = True

    def _onSensorSizeHeightSpinBoxChanged(self, value: int):
        self.session.settings.set_sensor_height(value)
        self.session.dirty = True

    def _onSensorSizeWidthSpinBoxChanged(self, value: int):
        self.session.settings.set_sensor_width(value)
        self.session.dirty = True

    def _onMinFocusDistanceSpinBoxChanged(self, value: int):
        self.session.settings.set_min_focus(value)
        self.session.dirty = True

    def _onMaxFocusDistanceSpinBoxChanged(self, value: int):
        self.session.settings.set_max_focus(value)
        self.session.dirty = True

    def _onFocusPointsSpinBoxChanged(self, value: int):
        self.session.settings.set_num_focus_points(value)
        self.session.dirty = True

    def _onIsPrimeCheckBoxChanged(self, checked: bool):
        self.session.settings.set_is_prime(checked)
        self._setPrimeEnabled(checked)
        self.session.dirty = True
        self.session.setting_prime_changed.emit(checked)

    def _setPrimeEnabled(self, enabled: bool):
        self.sw.SB_PrimeZoomValueSpinBox.setEnabled(enabled)
        self.sw.SB_MinZoomDistanceSpinBox.setEnabled(not enabled)
        self.sw.SB_MaxZoomDistanceSpinBox.setEnabled(not enabled)
        self.sw.SB_ZoomPointsValueSpinBox.setEnabled(not enabled)
        self.sw.L_PrimeZoomTitleLabel.setEnabled(enabled)
        self.sw.L_MinZoomDistanceLabel.setEnabled(not enabled)
        self.sw.L_MaxZoomDistanceLabel.setEnabled(not enabled)
        self.sw.L_ZoomPointsTitleLabel.setEnabled(not enabled)
        self.sw.L_ZoomRangeTitleLabel.setEnabled(not enabled)

    def _onPrimeZoomSpinBoxChanged(self, value: int):
        self.session.settings.set_prime_zoom(value)
        self.session.dirty = True

    def _onMinZoomDistanceSpinBoxChanged(self, value: int):
        self.session.settings.set_min_zoom(value)
        self.session.dirty = True

    def _onMaxZoomDistanceSpinBoxChanged(self, value: int):
        self.session.settings.set_max_zoom(value)
        self.session.dirty = True

    def _onZoomPointsSpinBoxChanged(self, value: int):
        self.session.settings.set_num_zoom_points(value)
        self.session.dirty = True

    def _onSamplesPerConfigurationSpinBoxChanged(self, value: int):
        self.session.settings.set_num_images_per_config(value)
        self.session.dirty = True

    def _onTimeToHoldStillSpinBoxChanged(self, value: float):
        self.session.settings.set_time_to_hold_still(value)
        self.session.dirty = True

    def _onImageGatherModeRadioButtonClicked(self, button):
        button_id = self.ImageGatherModeButtonGroup.id(button)
        self.session.settings.set_image_gather_mode(button_id)
        self.session.dirty = True
        # if the mode is manual, disable the time to hold still spin box and title label
        self.sw.L_TimeToHoldStillTitleLabel.setEnabled(button_id == 0)
        self.sw.DSP_TimeToHoldStillValueDoubleSpinBox.setEnabled(button_id == 0)

    def _onCheckerboardSizeColumnsSpinBoxChanged(self, value: int):
        self.session.settings.set_checkerboard_columns(value)
        self.session.dirty = True

    def _onCheckerboardSizeRowsSpinBoxChanged(self, value: int):
        self.session.settings.set_checkerboard_rows(value)
        self.session.dirty = True
