import numpy as np
from treelib import Tree

from calibration.camera_calibration_api import ImageCalibrationPayload, ImageCornersPayload


# class CalibrationDataPoint
# Single data point containing the calibration data for a single image. Used in the CalibrationDataModel
class CalibrationDataPoint():
    def __init__(self, focus: float, zoom: float, image: str, corner_payload: ImageCornersPayload, calibration_payload: ImageCalibrationPayload, image_data: np.ndarray):
        super().__init__()

        # ID values for the calibration data point
        self.focus = focus
        self.zoom = zoom
        self.image = image

        # Data payloads for the calibration data point
        self.corner_payload = corner_payload
        self.calibration_payload = calibration_payload

        # image data
        self.image_data = image_data

    def __str__(self) -> str:
        return f"({self.focus}:{self.zoom}:{self.image})"
    
    def __repr__(self) -> str:
        return f"({self.focus}:{self.zoom}:{self.image})"
    
    def __eq__(self, other) -> bool:
        return self.focus == other.focus and self.zoom == other.zoom and self.image == other.image

    def get_focus(self) -> str:
        return str(self.focus)
    
    def get_focus_id(self) -> str:
        return str(self.focus)
    
    def get_zoom_id(self) -> str:
        return f"{self.focus}:{self.zoom}"
    
    def get_image_id(self) -> str:
        return f"{self.focus}:{self.zoom}:{self.image}"
    
    def get_zoom(self) -> str:
        return str(self.zoom)
    
    def get_image(self) -> str:
        return self.image
    
    def to_dict(self) -> dict:
        corner_payload = None
        calibration_payload = None
        if self.corner_payload is not None:
            corner_payload = self.corner_payload.to_dict()
        if self.calibration_payload is not None:
            calibration_payload = self.calibration_payload.to_dict()
        return {
            "corner_payload": corner_payload,
            "calibration_payload": calibration_payload,
            # "image_data": self.image_data.tolist()
        }
    

# class CalibrationDataModel
class CalibrationDataModel():
    def __init__(self):
        super().__init__()
        self.tree = Tree(deep=True)
        self.tree.create_node("Root", "root")

    def copy(self, data: 'CalibrationDataModel') -> 'None':
        self.tree = data.tree

    def add_image_node(self, image_data: CalibrationDataPoint = None, zoom_data: CalibrationDataPoint = None, focus_data: CalibrationDataPoint = None):
        if zoom_data is None:
            zoom_data = image_data
        if focus_data is None:
            focus_data = zoom_data

        if not self.tree.contains(image_data.get_focus_id()):
            self.add_from_focus(image_data, zoom_data, focus_data)
        elif not self.tree.contains(image_data.get_zoom_id()):
            self.add_from_zoom(image_data, zoom_data)
        elif not self.tree.contains(image_data.get_image_id()):
            self.add_from_image(image_data)
        else:
            # the image already exists, so replace it with the new data
            self.delete_node(image_data.get_image_id())
            self.add_from_image(image_data)

    def delete_node(self, id: str):
        self.remove_node(id)

    def delete_all_nodes(self):
        self.tree = Tree()
        self.tree.create_node("Root", "root")

    def add_from_focus(self, image_data: CalibrationDataPoint = None, zoom_data: CalibrationDataPoint = None, focus_data: CalibrationDataPoint = None):
        self.tree.create_node(image_data.get_focus(), image_data.get_focus_id(), parent="root", data=focus_data)
        self.tree.create_node(image_data.get_zoom(), image_data.get_zoom_id(), parent=image_data.get_focus_id(), data=zoom_data)
        self.tree.create_node(image_data.get_image(), image_data.get_image_id(), parent=image_data.get_zoom_id(), data=image_data)

    def add_from_zoom(self, image_data: CalibrationDataPoint, zoom_data: CalibrationDataPoint = None):
        self.tree.create_node(image_data.get_zoom(), image_data.get_zoom_id(), parent=image_data.get_focus_id(), data=zoom_data)
        self.tree.create_node(image_data.get_image(), image_data.get_image_id(), parent=image_data.get_zoom_id(), data=image_data)

    def add_from_image(self, image_data: CalibrationDataPoint):
        self.tree.create_node(image_data.get_image(), image_data.get_image_id(), parent=image_data.get_zoom_id(), data=image_data)

    def get_all_focus_nodes(self) -> list[CalibrationDataPoint]:
        return [node.data for node in self.tree.children("root")]
    
    def get_zoom_nodes_from_id(self, focus_id: str) -> list[CalibrationDataPoint]:
        return [node.data for node in self.tree.children(focus_id)]
    
    def get_all_zoom_nodes(self) -> list[CalibrationDataPoint]:
        zoom_nodes = []
        for focus_node in self.get_all_focus_nodes():
            zoom_nodes.extend(self.get_zoom_nodes_from_id(focus_node.get_focus_id()))
        return zoom_nodes
    
    def get_image_nodes_from_id(self, zoom_id: str) -> list[CalibrationDataPoint]:
        return [node.data for node in self.tree.children(zoom_id)]
    
    def get_image_node(self, image_id: str) -> CalibrationDataPoint:
        return self.tree.get_node(image_id).data
    
    def get_all_image_nodes(self) -> list[CalibrationDataPoint]:
        image_nodes = []
        for zoom_node in self.get_all_zoom_nodes():
            image_nodes.extend(self.get_image_nodes_from_id(zoom_node.get_zoom_id()))
        return image_nodes
    
    def get_leaf_nodes(self) -> list[CalibrationDataPoint]:
        return [node.data for node in self.tree.leaves()]
    
    def remove_node(self, node_id: str):
        self.tree.remove_node(node_id)

    def to_dict(self) -> dict:
        focus_nodes = self.get_all_focus_nodes()
        data = {}
        for focus_node in focus_nodes:
            focus_dict = {}
            zoom_nodes = self.get_zoom_nodes_from_id(focus_node.get_focus_id())
            for zoom_node in zoom_nodes:
                zoom_dict = {}
                image_nodes = self.get_image_nodes_from_id(zoom_node.get_zoom_id())
                for image_node in image_nodes:
                    zoom_dict[image_node.get_image()] = image_node.to_dict()
                focus_dict[zoom_node.get_zoom()] = zoom_dict
                if zoom_node.calibration_payload is not None:
                    focus_dict[zoom_node.get_zoom()]["calibration_payload"] = zoom_node.calibration_payload.to_dict()
                else:
                    focus_dict[zoom_node.get_zoom()]["calibration_payload"] = None
            data[focus_node.get_focus()] = focus_dict
        return data
    
    @staticmethod
    def from_dict(data: dict) -> 'CalibrationDataModel':
        model = CalibrationDataModel()
        for focus, focus_dict in data.items():
            for zoom, zoom_dict in focus_dict.items():
                zoom_dict_count = 0
                zoom_dict_images = dict(list(zoom_dict.items())[:-1])
                for image, image_dict in zoom_dict_images.items():
                    corner_payload = None
                    calibration_payload = None
                    if image_dict["corner_payload"] is not None:
                        corner_payload = ImageCornersPayload.from_dict(image_dict["corner_payload"])
                    if image_dict["calibration_payload"] is not None:
                        calibration_payload = ImageCalibrationPayload.from_dict(image_dict["calibration_payload"])
                    image_data_point = CalibrationDataPoint(float(focus), float(zoom), image, corner_payload, calibration_payload, None)
                    if zoom_dict_count == 0 and zoom_dict["calibration_payload"] is not None:
                        zoom_calibration_payload = ImageCalibrationPayload.from_dict(zoom_dict["calibration_payload"])
                        zoom_data_point = CalibrationDataPoint(float(focus), float(zoom), image, corner_payload, zoom_calibration_payload, None)
                        model.add_image_node(image_data_point, zoom_data_point)
                    else:
                        model.add_image_node(image_data_point)
                    zoom_dict_count += 1
        return model
