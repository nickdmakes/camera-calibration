import os
import csv
import json
import numpy as np


# opens a json file (LensEncoderMap) and converts it to a csv file
def create_test_file(path: str):
    with open(path) as json_file:
        data = json.load(json_file)

    expected_focus_values = data['focus']['map']['values']
    expected_focus_motor_pos = data['focus']['map']['motor_pos']

    expected_iris_values = data['iris']['map']['values']
    expected_iris_motor_pos = data['iris']['map']['motor_pos']

    zoom_values = data['zoom']['map']['values']
    zoom_motor_pos = data['zoom']['map']['motor_pos']

    # calculate motor position for focus using polytrope function
    focus_params = data['focus']['curve']['parameters']
    actual_focus_motor_pos = [round(polytrope_fn(x, *focus_params)*10000) for x in expected_focus_values]

    # calculate motor position for iris using polytrope function
    iris_params = data['iris']['curve']['parameters']
    actual_iris_motor_pos = [round(polytrope_fn(x, *iris_params)*10000) for x in expected_iris_values]

    # write to csv file
    with open("test/encoder_testing.csv", mode='w', newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Focus Value", "Expected", "Actual", "Iris Value", "Expected", "Actual"])
        for i in range(len(expected_focus_motor_pos)):
            writer.writerow([expected_focus_values[i], expected_focus_motor_pos[i], actual_focus_motor_pos[i],
                             expected_iris_values[i], expected_iris_motor_pos[i], actual_iris_motor_pos[i]])

def polytrope_fn(x, a, b, c):
    return a / np.power(x, b) + c

if __name__ == "__main__":
    create_test_file("test/encoder_testing.json")