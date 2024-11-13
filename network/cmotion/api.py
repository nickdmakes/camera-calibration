from network.serial_context import SerialContext
from network.cmotion.packet import CmotionPacket, CommandData, MessageIdentifier

import time


def set_motor_pos(sc: SerialContext, value: int, type: str, excecute_cmd: int, percent: bool = True, clamp: bool = True):
    ''' Function to set the motor position of the focus, iris, or zoom motor
    @param sc: SerialContext object
    @param value: The value to set the motor to
    @param type: The type of motor to set [f, i, z]
    @param excecute_cmd: NOT SURE WHAT THIS IS YET
    '''

    assert type in ['f', 'i', 'z', 'all'], "Invalid motor type"
    assert clamp or ((percent and value >= 0 and value <= 100) or (not percent and value >= 0 and value <= 65535)), "Invalid value for motor position"
    assert excecute_cmd in [0, 1], "Invalid excecute_cmd value: must be 0 or 1"
    assert sc.is_running(), "SerialContext is not running"
    assert sc.last_receive != None, "SerialContext has no current state: last_receive is None"

    current_state = CmotionPacket.read_status_packet(sc.last_receive)
    value_normalized = value
    if percent:
        value_normalized = round(65535 * (value / 100))

    if clamp:
        value_normalized = max(0, min(65535, value_normalized))

    focus_value = current_state.focus_status_data.motor_pos
    iris_value = current_state.iris_status_data.motor_pos
    zoom_value = current_state.zoom_status_data.motor_pos

    if type == 'f':
        focus_value = value_normalized
    elif type == 'i':
        iris_value = value_normalized
    elif type == 'z':
        zoom_value = value_normalized
    elif type == 'all':
        focus_value = value_normalized
        iris_value = value_normalized
        zoom_value = value_normalized

    offset = 0
    if excecute_cmd == 1:
        offset = 2047

    focus_data = CommandData(excecute_cmd=excecute_cmd, is_master=1, data_valid=1, calibrate_cmd=0, three_d_func=0, offset_command=offset, motor_set_value=focus_value)
    iris_data = CommandData(excecute_cmd=excecute_cmd, is_master=1, data_valid=1, calibrate_cmd=0, three_d_func=0, offset_command=offset, motor_set_value=iris_value)
    zoom_data = CommandData(excecute_cmd=0, is_master=1, data_valid=1, calibrate_cmd=0, three_d_func=0, offset_command=0, motor_set_value=zoom_value)
    packet = CmotionPacket(message_id=MessageIdentifier.MOTOR_COMMAND, focus_command_data=focus_data, iris_command_data=iris_data, zoom_command_data=zoom_data)
    sc.send(packet.make_command_packet())

# Send a single CMotionPacket to the serial port
def send_ping(sc: SerialContext):
    focus_data = CommandData(excecute_cmd=1, is_master=1, data_valid=1, calibrate_cmd=0, three_d_func=0, offset_command=0, motor_set_value=65535)
    iris_data = CommandData(excecute_cmd=1, is_master=1, data_valid=1, calibrate_cmd=0, three_d_func=0, offset_command=0, motor_set_value=65535)
    zoom_data = CommandData(excecute_cmd=1, is_master=1, data_valid=1, calibrate_cmd=0, three_d_func=0, offset_command=0, motor_set_value=65535)
    packet = CmotionPacket(message_id=MessageIdentifier.MOTOR_COMMAND, focus_command_data=focus_data, iris_command_data=iris_data, zoom_command_data=zoom_data)
    sc.send(packet.make_command_packet())
