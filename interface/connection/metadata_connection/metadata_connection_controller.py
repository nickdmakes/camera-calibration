import time
from PyQt6 import QtGui
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QMessageBox

from interface.app.main_window import Ui_MainWindow as MainWindow
from interface.connection.metadata_connection.metadata_context_manager import MetadataContextManager
from interface.connection.metadata_connection.workers.connect_metadata_worker import ConnectMetadataWorker, ConnectMetadataWorkerSignals
from interface.shared.standard_error_dialog import StandardErrorDialog

from assets.assets import connection_down, connection_up, connection_loading

from network.metadata_context import MetadataContext


class MetadataConnectionController:
    def __init__(self, mw: MainWindow, mcm: MetadataContextManager):
        super().__init__()
        self.mw = mw
        self.mcm = mcm
        self.setupUi()
        self.connectSignalsSlots()
        self.threadpool = QThreadPool()

    def setupUi(self):
        self._onMetadataConnectionClosed()

    def connectSignalsSlots(self):
        self.mcm.socket_closed.connect(self._onMetadataConnectionClosed)
        self.mcm.socket_opened.connect(self._onMetadataConnectionOpened)
        self.mw.B_ConnectMetadataStreamButton.clicked.connect(self._onConnectMetadataButtonClicked)

    def _onMetadataConnectionClosed(self):
        self.mw.B_ConnectMetadataStreamButton.setText("Stream")
        self.mw.B_ConnectMetadataStreamButton.setEnabled(True)
        self.mw.LE_MetadataPortLineEdit.setEnabled(True)
        self.mw.L_MetadataStreamStatusIcon.setPixmap(QtGui.QPixmap(connection_down))

    def _onMetadataConnectionOpened(self):
        self.mw.B_ConnectMetadataStreamButton.setText("Stop")
        self.mw.B_ConnectMetadataStreamButton.setEnabled(True)
        self.mw.LE_MetadataPortLineEdit.setEnabled(False)
        self.mw.L_MetadataStreamStatusIcon.setPixmap(QtGui.QPixmap(connection_up))

    def _onConnectMetadataButtonClicked(self):
        if self.mcm.context.is_running():
            self.mcm.context.close()
        else:
            worker = self.makeConnectMetadataWorker()
            self.threadpool.start(worker)

    def connectMetadata_fn(self, metadata_context: MetadataContext, signals: ConnectMetadataWorkerSignals):
        metadata_context.open()
        time.sleep(metadata_context._timeout_ + 0.1)
        if not metadata_context.is_running():
            raise Exception("Failed to open metadata context")
        
    def makeConnectMetadataWorker(self):
        worker = ConnectMetadataWorker(self.connectMetadata_fn, self.mcm.context)
        worker.signals.connect_started.connect(self._s_connectStarted)
        worker.signals.connect_success.connect(self._s_connectSuccess)
        worker.signals.connect_finished.connect(self._s_connectFinished)
        worker.signals.connect_error.connect(self._s_connectError)
        return worker
    
    def _s_connectStarted(self):
        self.mw.B_ConnectMetadataStreamButton.setEnabled(False)
        self.mw.LE_MetadataPortLineEdit.setEnabled(False)
        self.mw.L_MetadataStreamStatusIcon.setPixmap(QtGui.QPixmap(connection_loading))

    def _s_connectSuccess(self):
        pass

    def _s_connectFinished(self):
        pass

    def _s_connectError(self, error):
        print(error)
        StandardErrorDialog(
            title="Metadata Connection Error", 
            message="Failed to connect to metadata stream", 
            details="Make sure the UMC-4 is streaming in unicast mode to the IP of this computer and the port is correct"
        )