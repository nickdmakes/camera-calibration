import json
import math
import numpy as np
from scipy.optimize import curve_fit, bisect


# custom exception for LensEncoderMap
class LensEncoderModelException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


LENS_ENCODER_MAP_JSON = {
    "focus": {
        "map": {
            "values": [],
            "motor_pos": [],
        },
        "curve": {
            "parameters": []
        }
    },
    "iris": {
        "map": {
            "values": [],
            "motor_pos": [],
        },
        "curve": {
            "parameters": []
        }
    },
    "zoom": {
        "map": {
            "values": [],
            "motor_pos": [],
        },
        "curve": {
            "parameters": []
        }
    }
}

# class LensEncoderModel
# models the mapping between lens value and motor encoder position
class LensEncoderModel:
    def __init__(self) -> None:
        self._lens_mappings_ = json.loads(json.dumps(LENS_ENCODER_MAP_JSON))

    def copy(self, lem: 'LensEncoderModel') -> None:
        self._lens_mappings_ = json.loads(json.dumps(lem._lens_mappings_))

    def to_dict(self) -> dict:
        return self._lens_mappings_

    @staticmethod
    def from_dict(d: dict) -> 'LensEncoderModel':
        lens_encoder_map = LensEncoderModel()
        lens_encoder_map._lens_mappings_ = d
        return lens_encoder_map

    def clear_mappings(self, type: str) -> None:
        if type == "all":
            self._lens_mappings_["focus"]["map"]["values"].clear()
            self._lens_mappings_["focus"]["map"]["motor_pos"].clear()
            self._lens_mappings_["focus"]["curve"]["parameters"].clear()
            self._lens_mappings_["iris"]["map"]["values"].clear()
            self._lens_mappings_["iris"]["map"]["motor_pos"].clear()
            self._lens_mappings_["iris"]["curve"]["parameters"].clear()
            self._lens_mappings_["zoom"]["map"]["values"].clear()
            self._lens_mappings_["zoom"]["map"]["motor_pos"].clear()
            self._lens_mappings_["zoom"]["curve"]["parameters"].clear()
        else:
            self._lens_mappings_[type]["map"]["values"].clear()
            self._lens_mappings_[type]["map"]["motor_pos"].clear()
            self._lens_mappings_[type]["curve"]["parameters"].clear()

    def add_mapping(self, type: str, value: float, motor_pos: int) -> None:
        self._lens_mappings_[type]["map"]["values"].append(value)
        self._lens_mappings_[type]["map"]["motor_pos"].append(motor_pos)

    def get_values(self, type: str) -> list:
        values = list(self._lens_mappings_[type]["map"]['values'])
        values_float = [float(value) for value in values]
        return values_float
    
    def get_min_value(self, type: str) -> float:
        return min(self.get_values(type))
    
    def get_max_value(self, type: str) -> float:
        return max(self.get_values(type))
    
    def get_parameters(self, type: str) -> list:
        return self._lens_mappings_[type]["curve"]["parameters"]
    
    def get_motor_positions(self, type: str) -> list:
        positions = list(self._lens_mappings_[type]["map"]['motor_pos'])
        positions_float = [float(position) for position in positions]
        return positions_float
    
    def focus_is_fitted(self) -> bool:
        return len(self.get_parameters("focus")) > 0
    
    def focus_fit_is_linear_interpolation(self) -> bool:
        return self.get_parameters("focus")[0] == -1 and self.get_parameters("focus")[1] == -1 and self.get_parameters("focus")[2] == -1
    
    def iris_is_fitted(self) -> bool:
        return len(self.get_parameters("iris")) > 0
    
    def iris_fit_is_linear_interpolation(self) -> bool:
        return self.get_parameters("iris")[0] == -1 and self.get_parameters("iris")[1] == -1 and self.get_parameters("iris")[2] == -1
    
    def zoom_is_fitted(self) -> bool:
        return len(self.get_parameters("zoom")) > 0

    def fit_focus_curve(self, force_linear=False) -> None:
        # put the focus values on a logarithmic scale
        xs = [np.log10(x+1) for x in self.get_values("focus")]
        ys = np.array(self.get_motor_positions("focus"))/10000

        if force_linear:
            self._lens_mappings_["focus"]["curve"]["parameters"] = [-1, -1, -1]
        else:
            # fit the data to a polytrope function with initial parameters
            p0 = (1, 1, 1)
            params, cv = curve_fit(self.polytrope_fn, xs, ys, p0=p0)
            a, b, c = params
            # determine quality of the fit
            squaredDiffs = np.square(ys - self.polytrope_fn(xs, a, b, c))
            squaredDiffsFromMean = np.square(ys - np.mean(ys))
            rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
            if rSquared < 0.98:
                raise LensEncoderModelException(f"R² = {rSquared} is too low")
            # update the curve parameters
            self._lens_mappings_["focus"]["curve"]["parameters"] = [a, b, c]

    def fit_iris_curve(self, force_linear=False) -> None:
        xs = np.array(self.get_values("iris"))
        ys = np.array(self.get_motor_positions("iris"))/10000

        if force_linear:
            self._lens_mappings_["iris"]["curve"]["parameters"] = [-1, -1, -1]
        else:
            # fit the data to a polytrope function with initial parameters
            p0 = (-15, 1, 7)
            params, cv = curve_fit(self.polytrope_fn, xs, ys, p0=p0)
            a, b, c = params
            # determine quality of the fit
            squaredDiffs = np.square(ys - self.polytrope_fn(xs, a, b, c))
            squaredDiffsFromMean = np.square(ys - np.mean(ys))
            rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
            if rSquared < 0.98:
                raise LensEncoderModelException(f"R² = {rSquared} is too low")
            # update the curve parameters
            self._lens_mappings_["iris"]["curve"]["parameters"] = [a, b, c]

    def fit_zoom_curve(self) -> None:
        xs = np.array(self.get_values("zoom"))
        ys = np.array(self.get_motor_positions("zoom"))/10000
        # fit the data to a linear function
        p0 = (1, 1)
        params, cv = curve_fit(lambda x, a, b: a*x + b, xs, ys, p0=p0)
        a, b = params
        # determine quality of the fit
        squaredDiffs = np.square(ys - (a*xs + b))
        squaredDiffsFromMean = np.square(ys - np.mean(ys))
        rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
        if rSquared < 0.98:
            raise LensEncoderModelException(f"R² = {rSquared} is too low")
        # update the curve parameters
        self._lens_mappings_["zoom"]["curve"]["parameters"] = [a, b]

    def predict_focus_motor_pos(self, value: float, imperial: bool = False) -> int:
        '''
        Predict the motor position for the focus encoder given a lens value in cm or inches
        @param value: the lens value in cm or inches
        @param imperial: True if the value is in inches, False if the value is in cm
        @return: the motor position
        '''
        if self.focus_is_fitted() is False:
                raise LensEncoderModelException("Focus curve is not fitted")
        # scale the cm value to ln(meters) (the curve is fitted to meters on a logarithmic scale)
        value_scaled = np.log10(value/100 + 1)
        if imperial:
            value_scaled = value_scaled * 2.54
        # If the number of values greater than 39, use linear interpolation
        # Otherwise, use the polytrope fitted interpolation
        values = [np.log10(x+1) for x in self.get_values("focus")]
        if self.focus_fit_is_linear_interpolation():
            # find the two points that the value lies between
            if value_scaled > max(values) or value_scaled < min(values):
                raise LensEncoderModelException("Value out of range")
            point_a = None
            point_b = None
            # values could be in ascending or descending order. 
            # Find the indices of the two points which the value lies between
            for i in range(len(values)-1):
                if values[i] <= value_scaled <= values[i+1]:
                    point_a = i
                    point_b = i+1
                    break
                elif values[i] >= value_scaled >= values[i+1]:
                    point_a = i
                    point_b = i+1
                    break
            # draw a line between the two points and predict the motor position
            x1, x2 = values[point_a], values[point_b]
            y1, y2 = self.get_motor_positions("focus")[point_a], self.get_motor_positions("focus")[point_b]
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope*x1
            motor_pos = slope*value_scaled + intercept
            return max(0, min(int(motor_pos), 65535))
        else:
            a, b, c = self._lens_mappings_["focus"]["curve"]["parameters"]
            motor_pos = self.polytrope_fn(value_scaled, a, b, c)*10000
            return max(0, min(int(motor_pos), 65535))
    
    def predict_iris_motor_pos(self, t_stop: float) -> int:
        if self.iris_is_fitted() is False:
                raise LensEncoderModelException("Iris curve is not fitted")
        # If the number of values is greater than 39, use linear interpolation
        # Otherwise, use the polytrope fitted interpolation
        values = self.get_values("iris")
        if self.iris_fit_is_linear_interpolation():
            # find the two points that the value lies between
            if t_stop > max(values) or t_stop < min(values):
                raise LensEncoderModelException("Value out of range")
            point_a = None
            point_b = None
            # values could be in ascending or descending order. 
            # Find the indices of the two points which the value lies between
            for i in range(len(values)-1):
                if values[i] <= t_stop <= values[i+1]:
                    point_a = i
                    point_b = i+1
                    break
                elif values[i] >= t_stop >= values[i+1]:
                    point_a = i
                    point_b = i+1
                    break
            # draw a line between the two points and predict the motor position
            x1, x2 = values[point_a], values[point_b]
            y1, y2 = self.get_motor_positions("iris")[point_a], self.get_motor_positions("iris")[point_b]
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope*x1
            motor_pos = slope*t_stop + intercept
            return max(0, min(int(motor_pos), 65535))
        else:
            a, b, c = self._lens_mappings_["iris"]["curve"]["parameters"]
            motor_pos = self.polytrope_fn(t_stop, a, b, c)*10000
            return max(0, min(int(motor_pos), 65535))
        
    def predict_zoom_motor_pos(self, value: float) -> int:
        if self.zoom_is_fitted() is False:
                raise LensEncoderModelException("Zoom curve is not fitted")
        a, b = self._lens_mappings_["zoom"]["curve"]["parameters"]
        motor_pos = a*value + b
        return max(0, min(int(motor_pos), 65535))
    
    def polytrope_fn(self, x, a, b, c):
        return a / np.power(x, b) + c
    
    def rmse_fn(self, actual, predicted): 
        se = np.square(np.subtract(actual,predicted))
        mse = np.mean(se)
        rmse = math.sqrt(mse)
        return rmse
