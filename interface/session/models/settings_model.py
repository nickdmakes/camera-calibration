import json

class SettingsModelException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


LENS_ENCODER_MAP_JSON = {
    "camera": {
        "sensor_width": 36.7,
        "sensor_height": 25.54,
        "image_width": 1920,
        "image_height": 1080,
    },
    "capture": {
        "min_focus": 100,
        "max_focus": 600,
        "num_focus_points": 11,
        "is_prime": 1,
        "prime_zoom": 35,
        "min_zoom": 0,
        "max_zoom": 0,
        "num_zoom_points": 0,
        "num_images_per_config": 9,
        "image_gather_mode": 1,
        "time_to_hold_still": 2.0,
        "checkerboard_rows": 5,
        "checkerboard_columns": 7,
    },
    "calibration": {},
}


class SettingsModel:
    def __init__(self) -> None:
        self._calibration_settings_ = json.loads(json.dumps(LENS_ENCODER_MAP_JSON))

    def copy(self, cs: 'SettingsModel') -> None:
        self._calibration_settings_ = json.loads(json.dumps(cs._calibration_settings_))

    def equals(self, other: 'SettingsModel') -> bool:
        return self._calibration_settings_ == other._calibration_settings_
    
    def soft_equals(self, other: 'SettingsModel') -> bool:
        # check if the calibration settings are the same, excluding the checkerboard rows and columns
        this_copy = json.loads(json.dumps(self._calibration_settings_))
        this_copy["capture"]["checkerboard_rows"] = other.get_checkerboard_rows()
        this_copy["capture"]["checkerboard_columns"] = other.get_checkerboard_columns()
        
        return this_copy == other._calibration_settings_

    @staticmethod
    def from_dict(d: dict) -> 'SettingsModel':
        cs = SettingsModel()
        cs._calibration_settings_ = d
        return cs
    
    def to_dict(self) -> dict:
        return self._calibration_settings_
    
    def get_sensor_width(self) -> float:
        return self._calibration_settings_["camera"]["sensor_width"]
    
    def set_sensor_width(self, sensor_width: float) -> None:
        self._calibration_settings_["camera"]["sensor_width"] = sensor_width

    def get_sensor_height(self) -> float:
        return self._calibration_settings_["camera"]["sensor_height"]
    
    def set_sensor_height(self, sensor_height: float) -> None:
        self._calibration_settings_["camera"]["sensor_height"] = sensor_height

    def get_image_width(self) -> int:
        return self._calibration_settings_["camera"]["image_width"]
    
    def set_image_width(self, image_width: int) -> None:
        self._calibration_settings_["camera"]["image_width"] = image_width

    def get_image_height(self) -> int:
        return self._calibration_settings_["camera"]["image_height"]
    
    def set_image_height(self, image_height: int) -> None:
        self._calibration_settings_["camera"]["image_height"] = image_height

    def get_min_focus(self) -> int:
        return self._calibration_settings_["capture"]["min_focus"]

    def set_min_focus(self, min_focus: int) -> None:
        self._calibration_settings_["capture"]["min_focus"] = min_focus

    def get_max_focus(self) -> int:
        return self._calibration_settings_["capture"]["max_focus"]
    
    def set_max_focus(self, max_focus: int) -> None:
        self._calibration_settings_["capture"]["max_focus"] = max_focus

    def get_num_focus_points(self) -> int:
        return self._calibration_settings_["capture"]["num_focus_points"]
    
    def set_num_focus_points(self, num_focus_points: int) -> None:
        self._calibration_settings_["capture"]["num_focus_points"] = num_focus_points

    def get_is_prime(self) -> bool:
        return self._calibration_settings_["capture"]["is_prime"] == 1
    
    def set_is_prime(self, is_prime: bool) -> None:
        self._calibration_settings_["capture"]["is_prime"] = 1 if is_prime else 0

    def get_prime_zoom(self) -> int:
        return self._calibration_settings_["capture"]["prime_zoom"]
    
    def set_prime_zoom(self, prime_zoom: int) -> None:
        self._calibration_settings_["capture"]["prime_zoom"] = prime_zoom

    def get_min_zoom(self) -> int:
        return self._calibration_settings_["capture"]["min_zoom"]

    def set_min_zoom(self, min_zoom: int) -> None:
        self._calibration_settings_["capture"]["min_zoom"] = min_zoom

    def get_max_zoom(self) -> int:
        return self._calibration_settings_["capture"]["max_zoom"]

    def set_max_zoom(self, max_zoom: int) -> None:
        self._calibration_settings_["capture"]["max_zoom"] = max_zoom

    def get_num_zoom_points(self) -> int:
        return self._calibration_settings_["capture"]["num_zoom_points"]

    def set_num_zoom_points(self, num_zoom_points: int) -> None:
        self._calibration_settings_["capture"]["num_zoom_points"] = num_zoom_points

    def get_num_images_per_config(self) -> int:
        return self._calibration_settings_["capture"]["num_images_per_config"]
    
    def set_num_images_per_config(self, num_images_per_config: int) -> None:
        self._calibration_settings_["capture"]["num_images_per_config"] = num_images_per_config

    def get_image_gather_mode(self) -> int:
        return self._calibration_settings_["capture"]["image_gather_mode"]
    
    def set_image_gather_mode(self, image_gather_mode: int) -> None:
        self._calibration_settings_["capture"]["image_gather_mode"] = image_gather_mode

    def get_time_to_hold_still(self) -> float:
        return self._calibration_settings_["capture"]["time_to_hold_still"]
    
    def set_time_to_hold_still(self, time_to_hold_still: float) -> None:
        self._calibration_settings_["capture"]["time_to_hold_still"] = time_to_hold_still

    def get_checkerboard_rows(self) -> int:
        return self._calibration_settings_["capture"]["checkerboard_rows"]
    
    def set_checkerboard_rows(self, checkerboard_rows: int) -> None:
        self._calibration_settings_["capture"]["checkerboard_rows"] = checkerboard_rows

    def get_checkerboard_columns(self) -> int:
        return self._calibration_settings_["capture"]["checkerboard_columns"]
    
    def set_checkerboard_columns(self, checkerboard_columns: int) -> None:
        self._calibration_settings_["capture"]["checkerboard_columns"] = checkerboard_columns
