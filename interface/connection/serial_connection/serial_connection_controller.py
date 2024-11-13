import time
import serial
from PyQt6 import QtGui
from PyQt6.QtCore import QThreadPool
import os

from interface.app.main_window import Ui_MainWindow as MainWindow
from interface.connection.serial_connection.serial_context_manager import SerialContextManager
from interface.connection.serial_connection.workers.connect_port_worker import ConnectPortWorker, ConnectPortWorkerSignals
from interface.shared.standard_error_dialog import StandardErrorDialog

from assets.assets import connection_down, connection_up, connection_loading

from network.serial_context import SerialContext
from network.cmotion.api import send_ping


class SerialConnectionController:
    def __init__(self, mw: MainWindow, scm: SerialContextManager):
        super().__init__()
        self.mw = mw
        self.scm = scm
        self.setupSerialContext()
        self.setupUi()
        self.connectSignalsSlots()
        self.threadpool = QThreadPool()

    def setupSerialContext(self):
        port = self.mw.CB_SerialPortComboBox.currentText()
        self.scm.context.set_port(port)

    def setupUi(self):
        self._onSerialConnectionClosed()

    def connectSignalsSlots(self):
        self.scm.port_closed.connect(self._onSerialConnectionClosed)
        self.scm.port_opened.connect(self._onSerialConnectionOpened)
        self.mw.CB_SerialPortComboBox.currentTextChanged.connect(self._onSerialPortSelected)
        self.mw.B_ConnectSerialPortButton.clicked.connect(self._onConnectSerialPortButtonClicked)

    def _onSerialConnectionClosed(self):
        self.mw.B_ConnectSerialPortButton.setText("Connect")
        self.mw.B_ConnectSerialPortButton.setEnabled(True)
        self.mw.CB_SerialPortComboBox.setEnabled(True)
        self.mw.L_SerialPortStatusIcon.setPixmap(QtGui.QPixmap(connection_down))

    def _onSerialConnectionOpened(self):
        self.mw.B_ConnectSerialPortButton.setEnabled(True)
        self.mw.B_ConnectSerialPortButton.setText("Disconnect")
        self.mw.L_SerialPortStatusIcon.setPixmap(QtGui.QPixmap(connection_up))

    def _onSerialPortSelected(self):
        port = self.mw.CB_SerialPortComboBox.currentText()
        self.scm.context.set_port(port)

    def _onConnectSerialPortButtonClicked(self):
        if self.scm.context.is_running():
            self.scm.context.close()
        else:
            worker = self.makeConnectPortWorker()
            self.threadpool.start(worker)

    def connectSerialPort_fn(self, serial_context: SerialContext, signals: ConnectPortWorkerSignals):
        serial_context.open()
        time.sleep(0.1)

        # Send a ping to the camera to check if it is connected
        # If the camera does not respond, raise an exception
        send_ping(serial_context)
        if serial_context.is_running():
            for i in range(10):
                time.sleep(0.1)
                if serial_context.last_receive != None:
                    break
            if serial_context.last_receive == None:
                serial_context.close()
                raise Exception("Could not connect to camera")
        else:
            raise Exception("Port not open")
        signals.connect_handshake_success.emit()

    def makeConnectPortWorker(self):
        worker = ConnectPortWorker(self.connectSerialPort_fn, self.scm.context)
        worker.signals.connect_started.connect(self._s_connectStarted)
        worker.signals.connect_success.connect(self._s_connectSuccess)
        worker.signals.connect_finished.connect(self._s_connectFinished)
        worker.signals.connect_error.connect(self._s_connectError)
        return worker
    
    def _s_connectStarted(self):
        self.mw.B_ConnectSerialPortButton.setEnabled(False)
        self.mw.CB_SerialPortComboBox.setEnabled(False)
        self.mw.L_SerialPortStatusIcon.setPixmap(QtGui.QPixmap(connection_loading))
        
    def _s_connectSuccess(self):
        pass

    def _s_connectFinished(self):
        pass

    def _s_connectError(self, error):
        self._onSerialConnectionClosed()
        if error[0] == serial.SerialException:
            StandardErrorDialog(
                title="Serial Connection Error", 
                message=f"Error connecting to serial port {self.scm.context._port_}", 
                details="Ensure the correct port is selected and the camera is connected and powered on.")
        else:
            StandardErrorDialog(
                title="Camera Communication Error", 
                message="Error recieving packets from camera", 
                details="Ensure the camera is connected and powered on.")
