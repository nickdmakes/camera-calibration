import serial
import threading

# Base exception class for serial context
class SerialContextException(Exception):
    pass

# Class CmotionSerialContext
# This class is used to maintain the serial port context and expose a callback for received data
class SerialContext:
    def __init__(self, port: str=None, baud=38400, bits=serial.EIGHTBITS, stop_bits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE, timeout=3):

        assert baud <= 115200 and baud >= 50

        # Serial object variables
        self._port_ = port
        self._baud_ = baud
        self._data_bits_ = bits
        self._stop_bits_ = stop_bits
        self._parity_ = parity
        self._timeout_ = timeout

        # Context information
        self._is_running_ = False
        self._recv_count_ = 0
        self._sent_count_ = 0
        self._serial_port_ = None
        self._close_callback_ = lambda: None
        self._open_callback_ = lambda: None

        # recent packet information
        self.last_send = None
        self.last_receive = None

        # Received data thread variables
        self._received_thread_ = None
        self._recv_callback_ = lambda data: None

    def set_port(self, port: str):
        self._port_ = port

    def get_recv_count(self):
        return self._recv_count_
    
    def get_sent_count(self):
        return self._sent_count_
    
    def reset_recv_count(self):
        self._recv_count_ = 0

    def reset_sent_count(self):
        self._sent_count_ = 0

    def __recv_func__(self, context):
        while context.is_running():
            try:
                packet = context._serial_port_.read(17)
                if len(packet) == 0:
                    continue
                self.last_receive = packet
                context._recv_callback_(packet)
                buf_len = len(packet)
                self._recv_count_ += buf_len
            except serial.SerialException as e:
                context.close(join=False)
                context._on_recv_error_(e)
        self._close_callback_()

    def on_recv_error(self, error: Exception):
        raise SerialContextException(f"Serial Context Exception: {error}")
        
    def set_recv_callback(self, callback: callable):
        self._recv_callback_ = callback

    def set_close_callback(self, callback: callable):
        self._close_callback_ = callback

    def set_open_callback(self, callback: callable):
        self._open_callback_ = callback

    def open(self):
        if self._port_ is None:
            raise Exception("Cmotion context port is not set")

        self._serial_port_ = serial.Serial(self._port_, self._baud_, self._data_bits_, 
                                           self._parity_, self._stop_bits_, self._timeout_)
        self._received_thread_ = threading.Thread(target=self.__recv_func__, args=(self,))
        self._is_running_ = True
        self._received_thread_.setDaemon(True)
        self._received_thread_.setName("CmotionReceiverThread")
        self._received_thread_.start()
        self._open_callback_()

    def close(self, join=True):
        self._is_running_ = False
        if self._received_thread_ is not None and join:
            self._received_thread_.join()
        if self._serial_port_ is not None:
            self._serial_port_.close()

    def send(self, data: bytearray):
        if not self.is_running():
            raise Exception("Cmotion context port is not open")

        self._serial_port_.write(data)
        self.last_send = data
        data_len = len(data)
        self._sent_count_ += data_len

    def is_running(self):
        return self._is_running_ and self._serial_port_.is_open
