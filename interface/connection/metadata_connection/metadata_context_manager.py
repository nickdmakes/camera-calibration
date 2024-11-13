from PyQt6.QtCore import QObject, pyqtSignal
from network.metadata_context import MetadataContext

# Class MetadataContextManager
# The class registers callbacks for the metadata context and emits signals when the UDP socket is opened or closed
class MetadataContextManager(QObject):
    data_received = pyqtSignal(dict, name='metadata_received')
    socket_closed = pyqtSignal(name='metadata_closed')
    socket_opened = pyqtSignal(name='metadata_opened')

    def __init__(self, metadata_context: MetadataContext):
        super().__init__()

        self.context = metadata_context

        self.context.set_recv_callback(self.data_recv_fn)
        self.context.set_close_callback(self.port_closed_fn)
        self.context.set_open_callback(self.port_opened_fn)

    def data_recv_fn(self, data):
        self.data_received.emit(data)

    def port_closed_fn(self):
        self.socket_closed.emit()

    def port_opened_fn(self):
        self.socket_opened.emit()
