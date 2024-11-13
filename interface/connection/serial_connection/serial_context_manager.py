from PyQt6.QtCore import QObject, pyqtSignal
from network.serial_context import SerialContext

# Class SerialContextManager
# The class registers callbacks for the serial context and emits signals when data is received or the port is closed
class SerialContextManager(QObject):
    data_received = pyqtSignal(bytes, name='serial_received')
    port_closed = pyqtSignal(name='serial_closed')
    port_opened = pyqtSignal(name='serial_opened')

    def __init__(self, serial_context: SerialContext):
        super().__init__()

        self.context = serial_context

        self.context.set_recv_callback(self.data_recv_fn)
        self.context.set_close_callback(self.port_closed_fn)
        self.context.set_open_callback(self.port_opened_fn)

    def data_recv_fn(self, data):
        self.data_received.emit(data)

    def port_closed_fn(self):
        self.port_closed.emit()
        
    def port_opened_fn(self):
        self.port_opened.emit()
