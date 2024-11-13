from interface.session.models.data_model import CalibrationDataPoint, CalibrationDataModel
import json

if __name__ == "__main__":
    data = CalibrationDataPoint(1.0, 2.0, "image1", None, None, None)
    data2 = CalibrationDataPoint(1.0, 2.0, "image2", None, None, None)
    data3 = CalibrationDataPoint(2.0, 3.0, "image1", None, None, None)
    data4 = CalibrationDataPoint(2.0, 3.0, "image2", None, None, None)
    model = CalibrationDataModel()
    model.add_image_node(data)
    model.add_image_node(data2)
    model.add_image_node(data3)
    model.add_image_node(data4)
    print(model.tree)

    print(model.get_all_focus_nodes())
    print(model.get_zoom_nodes_from_id("1.0"))
    print(model.get_image_nodes_from_id("1.0:2.0"))
    print(model.get_image_nodes_from_id("2.0:3.0"))

    model_dict = model.to_dict()
    # convert to json
    model_json = json.dumps(model_dict)
    print(model_json)

    # convert back to model
    model2 = CalibrationDataModel.from_dict(model_dict)
    print(model2.tree)