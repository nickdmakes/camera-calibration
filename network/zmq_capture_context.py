import threading
import cv2
import zmq
import time
import numpy as np

# Class CaptureContext
# This class is used to maintain the capture context and expose a callback for received frames from a zmq socket
class ZmqCaptureContext:
    def __init__(self, address: str="127.0.0.1", port: str="5555"):

        self._zmq_context_ = zmq.Context(io_threads=1)

        # ZMQ object variables
        self._address_ = address
        self._port_ = port
        self._socket_ = None

        # ZMQ context information
        self._is_running_ = False
        self._close_callback_ = lambda: None
        self._open_callback_ = lambda: None

        # Recent frame information
        self._last_frame_ = None

        # Received data thread variables
        self._received_thread_ = None
        self._recv_callback_ = lambda data: None

    def set_port(self, port: str):
        self._port_ = port

    def get_last_frame(self):
        return self._last_frame_

    def __recv_func__(self, context):
        while context.is_running():
            try:
                frame_bytes = context._socket_.recv()
                frame = np.frombuffer(frame_bytes, dtype=np.uint8)
                frame = frame.reshape(1080, 1920, 3)
                context._last_frame_ = frame
                context._recv_callback_(frame)
                pass
            except zmq.error.ZMQError as e:
                print(e)
                break
        self._close_callback_()

    def set_recv_callback(self, callback):
        self._recv_callback_ = callback

    def set_close_callback(self, callback):
        self._close_callback_ = callback

    def set_open_callback(self, callback):
        self._open_callback_ = callback

    def open(self):
        self._socket_ = self._zmq_context_.socket(zmq.SUB)
        self._socket_.connect(f"tcp://{self._address_}:{self._port_}")
        self._socket_.setsockopt(zmq.SUBSCRIBE, b'')

        self._received_thread_ = threading.Thread(target=self.__recv_func__, args=(self,))
        self._is_running_ = True
        self._received_thread_.setDaemon(True)
        self._received_thread_.setName("CmotionReceiverThread")
        self._received_thread_.start()
        self._open_callback_()

    def close(self):
        self._is_running_ = False
        self._received_thread_.join()
        self._socket_.disconnect(zmq.LAST_ENDPOINT)
        self._socket_.close()

    def is_running(self):
        return self._is_running_ and self._socket_.closed == False
