from enum import Enum


# Enum for the message identifier byte
class MessageIdentifier(Enum):
    MOTOR_COMMAND = 0x4F
    MOTOR_STATUS = 0x6F


# Class representation of a command data packet (4 bytes)
# - excecute_cmd: 1 bit
# - is_master: 1 bit
# - data_valid: 1 bit
# - calibrate_cmd: 1 bit
# - three_d_func: 1 bit
# - offset_command: 11 bits
# - motor_set_value: 16 bits
class CommandData:
    def __init__(self, excecute_cmd: int, is_master: int, data_valid: int, calibrate_cmd: int,
                three_d_func: int, offset_command: int, motor_set_value: int):
        self.excecute_cmd = excecute_cmd
        self.is_master = is_master
        self.data_valid = data_valid
        self.calibrate_cmd = calibrate_cmd
        self.three_d_func = three_d_func
        self.offset_command = offset_command
        self.motor_set_value = motor_set_value

        assert self.excecute_cmd in [0, 1]
        assert self.is_master in [0, 1]
        assert self.data_valid in [0, 1]
        assert self.calibrate_cmd in [0, 1]
        assert self.three_d_func in [0, 1]
        assert self.offset_command >= 0 and self.offset_command <= 2047
        assert self.motor_set_value >= 0 and self.motor_set_value <= 65535

    # Convert the command data into a bytearray (4 bytes)
    def make_bytes(self):
        bit_str = ""
        bit_str += str(self.excecute_cmd)
        bit_str += str(self.is_master)
        bit_str += str(self.data_valid)
        bit_str += str(self.calibrate_cmd)
        bit_str += str(self.three_d_func)
        bit_str += format(self.offset_command, '011b')
        bit_str += format(self.motor_set_value, '016b')

        data = bytearray()
        for i in range(0, len(bit_str), 8):
            data.append(int(bit_str[i:i+8], 2))

        return data
    
    def __str__(self):
        return "\n\texcecute_cmd: {}\n\tis_master: {}\n\tdata_valid: {}\n\tcalibrate_cmd: {}\n\tthree_d_func: {}\n\toffset_command: {}\n\tmotor_set_value: {}".format(
            # Get as hex string : convert int into binary string of bytes separated by spaces
            f'{hex(self.excecute_cmd)}: {format(self.excecute_cmd, "b")}',
            f'{hex(self.is_master)}: {format(self.is_master, "b")}',
            f'{hex(self.data_valid)}: {format(self.data_valid, "b")}',
            f'{hex(self.calibrate_cmd)}: {format(self.calibrate_cmd, "b")}',
            f'{hex(self.three_d_func)}: {format(self.three_d_func, "b")}',
            f'{hex(self.offset_command)}: {format(self.offset_command, "b")}',
            f'{hex(self.motor_set_value)}: {format(self.motor_set_value, "b")}'
        )
    

# Class representation of a status data packet (4 bytes)
# - mot_cal_req: 1 bit
# - mot_cal_run: 1 bit
# - mot_direction: 1 bit
# - request_control: 1 bit
# - mot_pos_valid: 1 bit
# - motor_pos: 16 bits
class StatusData:
    def __init__(self, mot_cal_req: int, mot_cal_run: int, mot_direction: int, request_control: int, mot_pos_valid: int, motor_pos: int):
        self.mot_cal_req = mot_cal_req
        self.mot_cal_run = mot_cal_run
        self.mot_direction = mot_direction
        self.request_control = request_control
        self.mot_pos_valid = mot_pos_valid
        self.motor_pos = motor_pos

        assert self.mot_cal_req in [0, 1]
        assert self.mot_cal_run in [0, 1]
        assert self.mot_direction in [0, 1]
        assert self.request_control in [0, 1]
        assert self.mot_pos_valid in [0, 1]
        assert self.motor_pos >= 0 and self.motor_pos <= 65535

    # Factory method to create a status data object from a bytearray (4 bytes)
    @staticmethod
    def from_bytes(buffer: bytearray):
        mot_cal_req = buffer[0] >> 4 & 0x01
        mot_cal_run = buffer[0] >> 3 & 0x01
        mot_direction = buffer[0] >> 2 & 0x01
        request_control = buffer[0] >> 1 & 0x01
        mot_pos_valid = buffer[0] & 0x01

        motor_pos = buffer[2] << 8 | buffer[3]

        return StatusData(mot_cal_req=mot_cal_req, 
                          mot_cal_run=mot_cal_run, 
                          mot_direction=mot_direction, 
                          request_control=request_control, 
                          mot_pos_valid=mot_pos_valid, 
                          motor_pos=motor_pos)

    def __str__(self):
        return "\n\tmot_cal_req: {}\n\tmot_cal_run: {}\n\tmot_direction: {}\n\trequest_control: {}\n\tmot_pos_valid: {}\n\tmotor_pos: {}".format(
            # Get as hex string : convert int into binary string of bytes separated by spaces
            f'{hex(self.mot_cal_req)}: {format(self.mot_cal_req, "b")}',
            f'{hex(self.mot_cal_run)}: {format(self.mot_cal_run, "b")}',
            f'{hex(self.mot_direction)}: {format(self.mot_direction, "b")}',
            f'{hex(self.request_control)}: {format(self.request_control, "b")}',
            f'{hex(self.mot_pos_valid)}: {format(self.mot_pos_valid, "b")}',
            f'{hex(self.motor_pos)}: {format(self.motor_pos, "b")}'
        )


# Class representation of a cmotion packet (17 bytes)
# - start_id: 1 byte
# - packet_length: 1 byte
# - message_id: 1 byte
# - focus_status_data: 4 bytes or focus_command_data: 4 bytes
# - iris_status_data: 4 bytes or iris_command_data: 4 bytes
# - zoom_status_data: 4 bytes or zoom_command_data: 4 bytes
# - checksum: 1 byte
# - end_id: 1 byte
class CmotionPacket:
    def __init__(self, message_id: MessageIdentifier, 
                 focus_status_data: StatusData = None, 
                 iris_status_data: StatusData = None,
                 zoom_status_data: StatusData = None,
                 focus_command_data: CommandData = None, 
                 iris_command_data: CommandData = None, 
                 zoom_command_data: CommandData = None):
        self.start_id = 0x02
        self.packet_length = 0x11
        self.end_id = 0x33
        self.message_id = message_id.value
        self.focus_status_data = focus_status_data
        self.iris_status_data = iris_status_data
        self.zoom_status_data = zoom_status_data
        self.focus_command_data = focus_command_data
        self.iris_command_data = iris_command_data
        self.zoom_command_data = zoom_command_data

        # assert that either all status data is not None OR all command data is not None
        assert message_id == MessageIdentifier.MOTOR_COMMAND and focus_command_data is not None and iris_command_data is not None and zoom_command_data is not None or \
                message_id == MessageIdentifier.MOTOR_STATUS and focus_status_data is not None and iris_status_data is not None and zoom_status_data is not None
    
    # Convert the cmotion packet into a bytearray (17 bytes)
    # Used for SENDING the packet over serial
    def make_command_packet(self):
        packet = bytearray(17)
        packet[0] = self.start_id
        packet[1] = self.packet_length
        packet[2] = self.message_id

        focus_packet = self.focus_command_data.make_bytes()
        iris_packet = self.iris_command_data.make_bytes()
        zoom_packet = self.zoom_command_data.make_bytes()

        packet[3:7] = focus_packet
        packet[7:11] = iris_packet
        packet[11:15] = zoom_packet

        checksum = packet[0]
        for i in range(1, 15):
            checksum ^= packet[i]

        packet[15] = checksum
        packet[16] = self.end_id

        return packet
    
    # Factory method to create a cmotion packet from a bytearray (17 bytes)
    # Used for RECIEVING the packet over serial
    @staticmethod
    def read_status_packet(buffer: bytearray):
        start_id = buffer[0]
        packet_length = buffer[1]
        message_id = buffer[2]

        if start_id != 0x02 or packet_length != 0x11 or message_id != MessageIdentifier.MOTOR_STATUS.value:
            raise Exception("Invalid packet")

        checksum = buffer[15]
        cs = buffer[0]
        for i in range(1, 15):
            cs ^= buffer[i]

        if cs != checksum:
            raise Exception("Invalid checksum")
        
        zoom_status_data = StatusData.from_bytes(buffer[11:15])
        iris_status_data = StatusData.from_bytes(buffer[7:11])
        focus_status_data = StatusData.from_bytes(buffer[3:7])

        return CmotionPacket(message_id=MessageIdentifier.MOTOR_STATUS, 
                             focus_status_data=focus_status_data, 
                             iris_status_data=iris_status_data, 
                             zoom_status_data=zoom_status_data)

    def __str__(self):
        if self.message_id == MessageIdentifier.MOTOR_COMMAND.value:
            return "start_id: {}\npacket_length: {}\nmessage_id: {}\nfocus_cmd: {}\niris_cmd: {}\nzoom_cmd: {}\nend_id: {}".format(
                # Get as hex string : binary string of bytes separated by spaces
                f'{hex(self.start_id)}: {" ".join(format(x, "08b") for x in bytearray([self.start_id]))}',
                f'{hex(self.packet_length)}: {" ".join(format(x, "08b") for x in bytearray([self.packet_length]))}',
                f'{hex(self.message_id)}: {" ".join(format(x, "08b") for x in bytearray([self.message_id]))}',
                f'{str(self.focus_command_data)}',
                f'{str(self.iris_command_data)}',
                f'{str(self.zoom_command_data)}',
                f'{hex(self.end_id)}: {" ".join(format(x, "08b") for x in bytearray([self.end_id]))}'
            )
        elif self.message_id == MessageIdentifier.MOTOR_STATUS.value:
            return "start_id: {}\npacket_length: {}\nmessage_id: {}\nfocus_status: {}\niris_status: {}\nzoom_status: {}\nend_id: {}".format(
                # Get as hex string : binary string of bytes separated by spaces
                f'{hex(self.start_id)}: {" ".join(format(x, "08b") for x in bytearray([self.start_id]))}',
                f'{hex(self.packet_length)}: {" ".join(format(x, "08b") for x in bytearray([self.packet_length]))}',
                f'{hex(self.message_id)}: {" ".join(format(x, "08b") for x in bytearray([self.message_id]))}',
                f'{str(self.focus_status_data)}',
                f'{str(self.iris_status_data)}',
                f'{str(self.zoom_status_data)}',
                f'{hex(self.end_id)}: {" ".join(format(x, "08b") for x in bytearray([self.end_id]))}'
            )
