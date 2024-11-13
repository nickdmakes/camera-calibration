import threading
import socket
import json
import time

# Base exception class for metadata context
class MetaDataContextException(Exception):
    pass

# Class MetaDataContext
# This class is used to maintain the metadata context streamed from the UMC 4
class MetadataContext:
    def __init__(self, port: int=5432, buffer_size=3000, address="", timeout=2):

        # OpenCV object variables
        self._port_ = port
        self._buffer_size_ = buffer_size
        self._address_ = address
        self._timeout_ = timeout

        # Context information
        self._is_running_ = False
        self._socket_ = None
        self._close_callback_ = lambda: None
        self._open_callback_ = lambda: None

        # Recent frame information
        self._last_metadata_ = None

        # Received data thread variables
        self._received_thread_ = None
        self._recv_callback_ = lambda data: None

    def get_focus(self, imperial=False, raw: bool=False) -> float:
        if self._last_metadata_ is None:
            raise MetaDataContextException("Socket is not open or metadata is not received")
        try:
            if imperial:
                imperial_raw = self._last_metadata_["camera"]["optic"]["lens"]["lensState"]["lensFocusDistanceImperial"]
                if float(imperial_raw) < 0:
                    return -1
                if raw:
                    return float(imperial_raw)
                return float(imperial_raw)/1000
            else:
                metric_raw = self._last_metadata_["camera"]["optic"]["lens"]["lensState"]["lensFocusDistanceMetric"]
                if float(metric_raw) < 0:
                    return -1
                if raw:
                    return float(metric_raw)
                return float(metric_raw)/1000
        except KeyError as e:
            return -1
        
    def get_iris(self, raw: bool=False) -> float:
        if self._last_metadata_ is None:
            raise MetaDataContextException("Socket is not open or metadata is not received")
        try:
            iris_raw = self._last_metadata_["camera"]["optic"]["lens"]["lensState"]["lensIris"]
            if iris_raw == "-1":
                raise MetaDataContextException("Invalid iris value: -1")
            elif iris_raw == "-2":
                raise MetaDataContextException("Close iris value: -2")
            elif iris_raw == "-3":
                raise MetaDataContextException("Near close iris value: -3")
            if raw:
                return float(iris_raw)
            n = (float(iris_raw)/1000) - 1
            t_stop = 2**(n/2)
            return round(t_stop, 3)
        except KeyError as e:
            return -1
        
    def get_zoom(self, raw: bool=False) -> float:
        if self._last_metadata_ is None:
            raise MetaDataContextException("Socket is not open or metadata is not received")
        try:
            zoom_raw = self._last_metadata_["camera"]["optic"]["lens"]["lensState"]["lensFocalLength"]
            if float(zoom_raw) < 0:
                return -1
            if raw:
                return float(zoom_raw)
            return float(zoom_raw)/1000
        except KeyError as e:
            return -1

    def __recv_func__(self, context):
        while context.is_running():
            try:
                data, addr = context._socket_.recvfrom(context._buffer_size_)
                json_data = json.loads(data.decode('utf-8'), strict=False)
                self._last_metadata_ = json_data
                context._recv_callback_(json_data)
            except Exception as e:
                context.close(join=False)
                context._close_callback_()
                context.on_recv_error(e)
        self._close_callback_()

    def on_recv_error(self, error: Exception):
        raise MetaDataContextException(f"Metadata Context Exception: {error}")
    
    def set_recv_callback(self, callback):
        self._recv_callback_ = callback

    def set_close_callback(self, callback):
        self._close_callback_ = callback

    def set_open_callback(self, callback):
        self._open_callback_ = callback

    def open(self):
        self._socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self._socket_.bind((self._address_, self._port_))
        self._socket_.bind(("", self._port_))
        self._socket_.settimeout(self._timeout_)

        self._received_thread_ = threading.Thread(target=self.__recv_func__, args=(self,))
        self._is_running_ = True
        self._received_thread_.setDaemon(True)
        self._received_thread_.setName("MetaDataReceiverThread")
        self._received_thread_.start()

        self._open_callback_()

    def close(self, join=True):
        self._is_running_ = False
        if self._received_thread_ is not None and join:
            self._received_thread_.join()
        if self._socket_ is not None:
            self._socket_.close()

    def is_running(self):
        return self._is_running_
