from PyQt6.QtCore import QObject, pyqtSignal

from interface.session.models.data_model import CalibrationDataModel
from interface.session.models.lens_encoder_model import LensEncoderModel
from interface.session.models.settings_model import SettingsModel
import json


# custom exception for CalibrationSession
class CalibrationSessionException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


CALIBRATION_SESSION_JSON = {
    "data": None,
    "map": None,
    "settings": None,
}


# Class CalibrationSession
class CalibrationSession(QObject):
    # lens encoder signals
    lens_encoder_fitted = pyqtSignal(name="lensEncoderFitted")
    lens_encoder_cleared = pyqtSignal(name="lensEncoderCleared")

    # settings signals
    setting_prime_changed = pyqtSignal(bool, name="settingPrimeChanged")

    # data signals
    data_updated = pyqtSignal(name="dataUpdated")
    data_gathered = pyqtSignal(name="dataGathered")
    data_calibrated = pyqtSignal(name="dataCalibrated")
    
    # file signals
    session_file_loaded = pyqtSignal(name="fileSessionLoaded")
    session_file_saved = pyqtSignal(name="fileSessionSaved")
    session_file_new = pyqtSignal(name="fileSessionNew")

    def __init__(self) -> None:
        super(CalibrationSession, self).__init__()
        self._json_ = json.loads(json.dumps(CALIBRATION_SESSION_JSON))
        self.dirty = False
        self.is_new = True
        self.data = CalibrationDataModel()
        self.lem = LensEncoderModel()
        self.settings = SettingsModel()

    def copy(self, session: 'CalibrationSession') -> None:
        self._json_ = json.loads(json.dumps(session._json_))
        self.dirty = session.dirty
        self.is_new = session.is_new
        self.data = session.data
        self.lem = session.lem
        self.settings = session.settings

    @staticmethod
    def from_file(file_path: str) -> 'CalibrationSession':
        session = CalibrationSession()
        with open(file_path, "r") as f:
            try:
                session._json_ = json.load(f)
                session.data = CalibrationDataModel.from_dict(session._json_["data"])
                session.lem = LensEncoderModel.from_dict(session._json_["map"])
                session.settings = SettingsModel.from_dict(session._json_["settings"])
            except Exception as e:
                print(e)
                raise CalibrationSessionException(f"Failed to load calibration session from file: {e}")

        return session

    def to_file(self, file_path: str) -> None:
        self._json_["data"] = self.data.to_dict()
        self._json_["map"] = self.lem.to_dict()
        self._json_["settings"] = self.settings.to_dict()
        with open(file_path, "w") as f:
            json.dump(self._json_, f, indent=4)
