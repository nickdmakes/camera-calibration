import json
from interface.session.calibration_session import CalibrationSession
from interface.session.models.data_model import CalibrationDataPoint

CALIBRATION_EXPORT_JSON = {
	"metadata":
	{
		"type": "LensFile",
		"version": "0.0.0",
		"lensInfo":
		{
			"serialNumber": "",
			"modelName": "",
			"distortionModel": "spherical"
		},
		"name": "",
		"nodalOffsetCoordinateSystem": "OpenCV",
		"fxFyUnits": "Normalized",
		"cxCyUnits": "Normalized",
		"userMetadata": []
	},
	"sensorDimensions":
	{
		"width": None,
		"height": None,
		"units": "Millimeters"
	},
	"imageDimensions":
	{
		"width": None,
		"height": None
	},
	"cameraParameterTables": [
		{
			"parameterName": "FocalLengthTable",
			"header": "FocusEncoder, ZoomEncoder, Fx, Fy",
			"data": ""
		},
		{
			"parameterName": "ImageCenterTable",
			"header": "FocusEncoder, ZoomEncoder, Cx, Cy",
			"data": ""
		},
		{
			"parameterName": "NodalOffsetTable",
			"header": "FocusEncoder, ZoomEncoder, Qx, Qy, Qz, Qw, Tx, Ty, Tz",
			"data": ""
		},
		{
			"parameterName": "DistortionTable",
			"header": "FocusEncoder, ZoomEncoder, K1, K2, K3, P1, P2",
			"data": ""
		}
	],
	"encoderTables": [
		{
			"parameterName": "Focus",
			"header": "FocusEncoder, FocusCM",
			"data": ""
		},
		{
			"parameterName": "Iris",
			"header": "IrisEncoder, IrisFstop",
			"data": ""
		}
	]
}

# class CalibrationExport
# models the calibration export
class CalibrationExport:
	def __init__(self) -> None:
		self._calibration_export = json.loads(json.dumps(CALIBRATION_EXPORT_JSON))

	def copy(self, ce: 'CalibrationExport') -> None:
		self._calibration_export = json.loads(json.dumps(ce._calibration_export))

	def to_file(self, file_path: str) -> None:
		with open(file_path, "w") as f:
			json.dump(self._calibration_export, f, indent=4)

	def export_session(self, session: CalibrationSession, output_file_path: str) -> None:
		# set image and sensor dimensions
		self._calibration_export["sensorDimensions"]["width"] = session.settings.get_sensor_width()
		self._calibration_export["sensorDimensions"]["height"] = session.settings.get_sensor_height()
		self._calibration_export["imageDimensions"]["width"] = session.settings.get_image_width()
		self._calibration_export["imageDimensions"]["height"] = session.settings.get_image_height()

		self._calibration_export["metadata"]["name"] = "LF_Zeiss_CP35_CC"
		zoom_nodes = session.data.get_all_zoom_nodes()
		for i, zoom in enumerate(zoom_nodes):
			temp_image_node = session.data.get_image_nodes_from_id(zoom.get_zoom_id())[0]
			# image height and width
			h = temp_image_node.corner_payload.image_shape[1]
			w = temp_image_node.corner_payload.image_shape[0]
			self._add_distortion_data(data_point=zoom, height=h, width=w, is_last=(i == len(zoom_nodes) - 1))
		
		self.to_file(file_path=output_file_path)

	def _add_distortion_data(self, data_point: CalibrationDataPoint, height: int, width: int, is_last: bool = False) -> None:
		focus_encoder = data_point.get_focus()
		zoom_encoder = data_point.get_zoom()
		terminating_char = "" if is_last else "; "

		# Add to distortion table
		k1 = data_point.calibration_payload.distortion_coefficients[0][0]
		k2 = data_point.calibration_payload.distortion_coefficients[0][1]
		p1 = data_point.calibration_payload.distortion_coefficients[0][2]
		p2 = data_point.calibration_payload.distortion_coefficients[0][3]
		k3 = data_point.calibration_payload.distortion_coefficients[0][4]
		self._calibration_export["cameraParameterTables"][3]["data"] += f"{focus_encoder}, {zoom_encoder}, {k1}, {k2}, {k3}, {p1}, {p2}{terminating_char}"

		# Add to focal length table
		fx = data_point.calibration_payload.camera_matrix[0][0]
		fy = data_point.calibration_payload.camera_matrix[1][1]
		fx_normal = round(fx / width, 2)
		fy_normal = round(fy / height, 2)
		self._calibration_export["cameraParameterTables"][0]["data"] += f"{focus_encoder}, {zoom_encoder}, {fx_normal}, {fy_normal}{terminating_char}"

		# Add to image center table
		cx = data_point.calibration_payload.camera_matrix[0][2]
		cy = data_point.calibration_payload.camera_matrix[1][2]
		cx_normal = round(cx / width, 2)
		cy_normal = round(cy / height, 2)
		self._calibration_export["cameraParameterTables"][1]["data"] += f"{focus_encoder}, {zoom_encoder}, {cx_normal}, {cy_normal}{terminating_char}"
