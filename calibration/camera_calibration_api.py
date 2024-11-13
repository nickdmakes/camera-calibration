import cv2
import imutils
import numpy as np

# This file will expose camera calibration functions and robust exception handling
# private functions will be prefixed with an underscore and will not be exposed

class CalibrationException(Exception):
    '''Exception raised for errors in the calibration process.'''
    pass

class CheckerboardNotFoundException(CalibrationException):
    '''Exception raised when the checkerboard corners are not found in the image.'''
    def __init__(self, message="Checkerboard corners not found in the image."):
        self.message = message
        super().__init__(self.message)

class CameraCalibrationException(CalibrationException):
    '''Exception raised when the camera calibration process fails.'''
    def __init__(self, message="Camera calibration failed."):
        self.message = message
        super().__init__(self.message)


# payload of data that is output from the calibration process
class ImageCalibrationPayload:
    def __init__(self, camera_matrix: np.ndarray, distortion_coefficients: np.ndarray, reproj_error: float = 0.0):
        self.camera_matrix = camera_matrix
        self.distortion_coefficients = distortion_coefficients
        self.reproj_error = reproj_error

    def to_dict(self) -> dict:
        return {
            "camera_matrix": self.camera_matrix.tolist(),
            "distortion_coefficients": self.distortion_coefficients.tolist(),
            "reproj_error": self.reproj_error,
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'ImageCalibrationPayload':
        return ImageCalibrationPayload(np.array(data["camera_matrix"]), np.array(data["distortion_coefficients"]), data["reproj_error"])
        

class ImageCornersPayload:
    def __init__(self, object_points: np.ndarray, image_points: np.ndarray, pattern_size: tuple, image_size: tuple = None):
        self.object_points = object_points
        self.image_points = image_points
        self.pattern_size = pattern_size
        self.image_shape = image_size

    def to_dict(self) -> dict:
        return {
            "pattern_size": self.pattern_size,
            "object_points": self.object_points.tolist(),
            "image_points": self.image_points.tolist(),
            "image_size": self.image_shape,
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'ImageCornersPayload':
        return ImageCornersPayload(np.array(data["object_points"], dtype=np.float32), np.array(data["image_points"], dtype=np.float32), data["pattern_size"], data["image_size"])

def calculate_corners(image, pattern_size: tuple) -> ImageCornersPayload:
    # Generate the object points
    object_points = _generate_object_points(pattern_size)

    # Refine the corner locations
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Find the checkerboard corners
    corners = find_checkerboard_corners(grey_image, pattern_size)
    if corners is None:
        return None
    image_points = cv2.cornerSubPix(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), corners, (11, 11), (-1, -1), criteria)

    # return the payload
    return ImageCornersPayload(object_points, image_points, pattern_size, grey_image.shape[::-1])

def paint_corner_image(image, pattern_size: tuple, image_points: np.ndarray) -> np.ndarray:
    cv2.drawChessboardCorners(image, pattern_size, image_points, True)
    return image

def find_checkerboard_corners(image, pattern_size) -> np.ndarray:
    ret, corners = cv2.findChessboardCorners(image, pattern_size, None)
    if not ret:
        return None
    return corners

def _generate_object_points(pattern_size: tuple[int, int]) -> np.ndarray:
    object_points = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    object_points[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
    return object_points

def calibrate_camera(object_points, image_points, image_size: tuple) -> ImageCalibrationPayload:
    ret, camera_matrix, distortion_coefficients, rvecs, tvecs = cv2.calibrateCamera(object_points, image_points, image_size, None, None)
    if not ret:
        return None
    reprojection_error = 0
    for i in range(len(object_points)):
        image_points2, _ = cv2.projectPoints(object_points[i], rvecs[i], tvecs[i], camera_matrix, distortion_coefficients)
        error = cv2.norm(image_points[i], image_points2, cv2.NORM_L2) / len(image_points2)
        reprojection_error += error
    reprojection_error /= len(object_points)
    return ImageCalibrationPayload(camera_matrix, distortion_coefficients, reprojection_error)

def get_calibration_matrix_values(cornerPayload: ImageCornersPayload, calibrationPaylaod: ImageCalibrationPayload, sensor_x: float, sensor_y: float) -> tuple:
    maxtrixValues = cv2.calibrationMatrixValues(cameraMatrix=calibrationPaylaod.camera_matrix,
                                                imageSize=cornerPayload.image_shape,
                                                apertureWidth=0,
                                                apertureHeight=0)
    return maxtrixValues

# function that will detect if the checkerboard is in motion
# The function inputs are the previous image, previous image points, current image, current image points
# The function will return a boolean value
def detect_checkerboard_motion(prev_image, curr_image) -> bool:
    prev_check = prev_image
    curr_check = curr_image

    # resize, convert to gray, and blur the images
    prev_check = imutils.resize(prev_check, width=500)
    curr_check = imutils.resize(curr_check, width=500)
    prev_check = cv2.cvtColor(prev_check, cv2.COLOR_BGR2GRAY)
    curr_check = cv2.cvtColor(curr_check, cv2.COLOR_BGR2GRAY)
    prev_check = cv2.GaussianBlur(prev_check, (21, 21), 0)
    curr_check = cv2.GaussianBlur(curr_check, (21, 21), 0)

    # calculate the difference between the images
    diff = cv2.absdiff(prev_check, curr_check)
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]

    # dilate the threshold image to fill in holes, then find contours on threshold image
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    # loop over the contours
    for contour in contours:
        if cv2.contourArea(contour) < 200:
            continue
        return True
    return False

if __name__ == "__main__":
    image = cv2.imread("calibration/test_image.jpg")
    image2 = cv2.imread("calibration/test_image.jpg")
    pattern_size = (9, 6)
    corner_payload = calculate_corners(image, pattern_size)
    corner_payload2 = calculate_corners(image2, pattern_size)

    image_points = corner_payload.image_points
    object_points = corner_payload.object_points

    print(object_points.shape)

    opl = object_points.tolist()

    opn = np.array(opl, dtype=np.float32)

    print(opn.shape)

    print(object_points)
    print(type(object_points))
    print(type(object_points[0]))
    print(type(object_points[0][0]))
    print("-------------")
    print(opn)
    print(type(opn))
    print(type(opn[0]))
    print(type(opn[0][0]))

    # change all numbers in opn to float32
    # opn = opn.astype(np.float32)

    

    min_x = None
    max_x = None
    min_y = None
    max_y = None

    for point in image_points:
        if min_x is None or point[0][0] < min_x:
            min_x = int(point[0][0])
        if max_x is None or point[0][0] > max_x:
            max_x = int(point[0][0])
        if min_y is None or point[0][1] < min_y:
            min_y = int(point[0][1])
        if max_y is None or point[0][1] > max_y:
            max_y = int(point[0][1])

    print(min_x, max_x, min_y, max_y)

    # crop the image
    cropped_image = image[min_y:max_y, min_x:max_x]

    cv2.imshow("Cropped Image", cropped_image)
    cv2.waitKey(0)

    # make the image gray
    grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # calculate the calibration
    calibration = calibrate_camera([object_points], [corner_payload.image_points], corner_payload.image_shape)
    print(calibration.camera_matrix)
    print(calibration.distortion_coefficients)
    print(calibration.reproj_error)
    cv2.waitKey(0)

    calibration = calibrate_camera([opn], [corner_payload.image_points], corner_payload.image_shape)

    # undistort the image
    undistorted_image = cv2.undistort(image, calibration.camera_matrix, calibration.distortion_coefficients)
    cv2.imshow("Undistorted Image", undistorted_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
