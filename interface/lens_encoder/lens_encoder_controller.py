import math
import time
from datetime import datetime
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtCore import QThreadPool
from PyQt6.QtGui import QIcon
from PyQt6 import QtGui

from interface.app.main_window import Ui_MainWindow as MainWindow
from interface.session.calibration_session import CalibrationSession
from interface.lens_encoder.encoder_plot.encoder_plot_controller import LensEncoderPlotController
from interface.session.models.lens_encoder_model import LensEncoderModel, LENS_ENCODER_MAP_JSON
from interface.connection.serial_connection.serial_context_manager import SerialContextManager
from interface.connection.metadata_connection.metadata_context_manager import MetadataContextManager
from interface.lens_encoder.workers.run_lens_encoder import RunLensEncoderWorker, RunLensEncoderWorkerSignals, RunLensEncoderException, LensEncoderFitDataException
from interface.session.models.lens_encoder_model import LensEncoderModelException
from interface.shared.standard_error_dialog import StandardErrorDialog

from assets.assets import play, clear, cancel

from network.cmotion.api import set_motor_pos, send_ping
from network.metadata_context import MetadataContext
from network.serial_context import SerialContext
from network.cmotion.packet import CmotionPacket

# temp
import csv

GET_TWIN_DATA = False
GET_VALIDATION_DATA = False
VALIDATION_START_SAMPLE_COUNT = 4
VALIDATION_END_SAMPLE_COUNT = 100

class LensEncoderProgressBarController:
    def __init__(self, progress_bar: QProgressBar = None):
        self.progress_bar = progress_bar
        self.n_samples = 0
        self.samples_completed = 0
        self.start_time = 0
        self.setupUi()

    def setupUi(self):
        self.progress_bar.setValue(0)

    def reset(self):
        self.progress_bar.setValue(0)
        self.n_samples = 0
        self.samples_completed = 0
        self.start_time = 0

    def start_process(self, n_samples: int):
        self.reset()
        self.progress_bar.setValue(1)
        self.start_time = time.time()
        self.n_samples = n_samples

    def complete_nugget(self, n: int = 1):
        self.samples_completed += n
        self.progress_bar.setValue(self.percent_complete())

    def are_nuggets_done(self):
        return self.samples_completed == self.n_samples
    
    def percent_complete(self):
        return (self.samples_completed / self.n_samples) * 100

    def get_stats_str(self):
        elapsed_time = datetime.fromtimestamp(time.time() - self.start_time).strftime("%M:%S.%f")[:-4]
        return f"Time elapsed: {elapsed_time}"


class LensEncoderController:
    def __init__(self, main_window: MainWindow, session: CalibrationSession, scm: SerialContextManager, mcm: MetadataContextManager):
        self.mw = main_window
        self.scm = scm
        self.mcm = mcm
        self.session = session
        self.pb_controller = LensEncoderProgressBarController(progress_bar=self.mw.PB_LensEncoderProgressBar)
        self.ep_controller =LensEncoderPlotController(main_window=self.mw, session=self.session)
        self.debug_window = self.mw.TB_LensEncoderDebugTextBrowser
        self.setupUi()
        self.connectSignalsSlots()
        self.encoder_thread_is_cancelled = False
        self.thread_pool = QThreadPool()

    def setupUi(self):
        self.mw.TB_LensEncoderClearToolButton.setIcon(QIcon(clear))
        self.mw.TB_LensEncoderStartToolButton.setIcon(QIcon(play))
        self.mw.TB_LensEncoderStartToolButton.setEnabled(False)
        self.ep_controller.updateAllGraphs()
        self._displayLensEncoderProperties()

    def connectSignalsSlots(self):
        self.scm.port_opened.connect(self._onSerialConnectionOpened)
        self.scm.port_closed.connect(self._onSerialConnectionClosed)
        self.mcm.socket_opened.connect(self._onMetadataConnectionOpened)
        self.mcm.socket_closed.connect(self._onMetadataConnectionClosed)
        self.mcm.data_received.connect(self._onMetadataDataReceived)
        self.mw.TB_LensEncoderClearToolButton.clicked.connect(self._onClearLensEncoderClicked)
        self.mw.TB_LensEncoderStartToolButton.clicked.connect(self._onStartLensEncoderClicked)

        self.session.session_file_loaded.connect(self._onSessionFileLoaded)
        self.session.session_file_new.connect(self._onSessionFileNew)
        self.session.setting_prime_changed.connect(self._onSettingPrimeChanged)

    def _displayLensEncoderProperties(self):
        if self.session.lem.focus_is_fitted():
            self.mw.L_LensEncoderSamples.setText(str(len(self.session.lem.get_values(type="iris"))))
        else:
            self.mw.L_LensEncoderSamples.setText("None")

    def _onSerialConnectionOpened(self):
        if self.mcm.context.is_running():
            self.mw.TB_LensEncoderStartToolButton.setEnabled(True)

    def _onSerialConnectionClosed(self):
        self.mw.TB_LensEncoderStartToolButton.setEnabled(False)

    def _onMetadataConnectionOpened(self):
        if self.scm.context.is_running():
            self.mw.TB_LensEncoderStartToolButton.setEnabled(True)

    def _onMetadataDataReceived(self, data: dict):
        fv = round(self.mcm.context.get_focus(), 3)
        iv = round(self.mcm.context.get_iris(), 3)
        zv = round(self.mcm.context.get_zoom(), 3)
        self.mw.L_FocusEncoderLiveLabel.setText(str(fv) if fv >= 0 else "NA")
        self.mw.L_IrisEncoderLiveLabel.setText(str(iv) if iv >= 0 else "NA")
        self.mw.L_ZoomEncoderLiveLabel.setText(str(zv) if zv >= 0 else "NA")

    def _onMetadataConnectionClosed(self):
        self.mw.TB_LensEncoderStartToolButton.setEnabled(False)
        self.mw.L_FocusEncoderLiveLabel.setText("NA")
        self.mw.L_IrisEncoderLiveLabel.setText("NA")
        self.mw.L_ZoomEncoderLiveLabel.setText("NA")

    def _onClearLensEncoderClicked(self):
        new_lem = LensEncoderModel()
        self.session.lem.copy(new_lem)
        self.ep_controller.updateAllGraphs()
        self._displayLensEncoderProperties()
        self.pb_controller.reset()
        self.debug_window.clear()
        self._writeToEncoderDebugWindow(level="info", msg="Created new lens encoder mapping")
        self.session.lens_encoder_cleared.emit()

    def writeValidationToFile(self):
        # This function will be called after runLensEncoder_fn is finished
        sample_count = self.mw.SB_LensEncoderSampleSpinBox.value()
        ttr = round(time.time() - self.data_start_time, 3)
        focus_rmse = "-"
        focus_params = self.session.lem.get_parameters(type="focus")
        if focus_params != []:
            a, b, c = focus_params[0], focus_params[1], focus_params[2]
            xs = []
            ys = []
            with open("focus_twin_data.csv", "r") as f:
                lines = f.readlines()
                for line in lines:
                    xs.append(float(line.split(",")[0].strip()))
                    ys.append(float(line.split(",")[1].strip()))
            xs = np.array(xs)
            xs = [np.log10(x+1) for x in xs]
            ys = np.array(ys)/10000
            focus_rmse = round(np.sqrt(np.mean((ys - self.session.lem.polytrope_fn(xs, a, b, c))**2))*10000, 3)

        iris_rmse = "-"
        iris_params = self.session.lem.get_parameters(type="iris")
        if iris_params != []:
            a, b, c = iris_params[0], iris_params[1], iris_params[2]
            # get xs from iris_twin_data.csv. the x values are in the first column
            xs = []
            ys = []
            with open("iris_twin_data.csv", "r") as f:
                lines = f.readlines()
                for line in lines:
                    xs.append(float(line.split(",")[0].strip()))
                    ys.append(float(line.split(",")[1].strip()))
            xs = np.array(xs)
            ys = np.array(ys)/10000
            iris_rmse = round(np.sqrt(np.mean((ys - self.session.lem.polytrope_fn(xs, a, b, c))**2))*10000, 3)

        with open("focus_validation_rmse.csv", "a") as f:
            f.write(f"{focus_rmse}, ")
        with open("iris_validation_rmse.csv", "a") as f:
            f.write(f"{iris_rmse}, ")
        with open("focus_validation_ttr.csv", "a") as f:
            f.write(f"{ttr}, ")
        with open("iris_validation_ttr.csv", "a") as f:
            f.write(f"{ttr}, ")
        

    def _onStartLensEncoderClicked(self):
        self.mw.TB_LensEncoderStartToolButton.setIcon(QIcon(cancel))
        self.mw.TB_LensEncoderStartToolButton.setText("Cancel")
        self.mw.TB_LensEncoderClearToolButton.setEnabled(False)
        if self.thread_pool.activeThreadCount() > 0:
            self.encoder_thread_is_cancelled = True
        else:
            # temp
            if GET_TWIN_DATA:
                self.mw.SB_LensEncoderSampleSpinBox.setValue(300)
            elif GET_VALIDATION_DATA:
                self.mw.SB_LensEncoderSampleSpinBox.setValue(VALIDATION_START_SAMPLE_COUNT)

            self.pb_controller.start_process(n_samples=self.mw.SB_LensEncoderSampleSpinBox.value())
            worker = self.makeRunLensEncoderWorker()
            self.thread_pool.start(worker)

    def runLensEncode_fn(self, sc: SerialContext, mc: MetadataContext, signals: RunLensEncoderWorkerSignals):
        # make copy of lens encoder map
        lem_copy = LensEncoderModel()
        lem_copy.copy(self.session.lem)

        try:
            self.session.lem.clear_mappings(type="all")
            use_zoom = not self.session.settings.get_is_prime()

            min_motor_pos = 300
            max_motor_pos = 65535
            num_motor_pos = self.mw.SB_LensEncoderSampleSpinBox.value()

            # Generate evenly spaced motor positions between min and max motor positions
            motor_positions = []
            motor_positions.append(min_motor_pos)
            for i in range(1, num_motor_pos-1):
                motor_positions.append(i*(max_motor_pos-min_motor_pos)//(num_motor_pos-1))
            motor_positions.append(max_motor_pos)

            print("Motor Positions: ", motor_positions)

            for i in motor_positions:
                if self.encoder_thread_is_cancelled:
                    raise RunLensEncoderException("Lens encoder process cancelled")
                set_motor_pos(sc=self.scm.context, value=i, type="all", excecute_cmd=0, percent=False)
                self.lensValueChangeLock(mpf=float(i), use_focus=True, use_iris=True, use_zoom=use_zoom)
                fv = mc.get_focus()
                iv = mc.get_iris()
                zv = mc.get_zoom()
                if fv > 0:
                    self.session.lem.add_mapping("focus", fv, i)
                if iv > 0: 
                    self.session.lem.add_mapping("iris", iv, i)
                if zv > 0 and use_zoom:
                    self.session.lem.add_mapping("zoom", zv, i)
                signals.run_sampled.emit()
            # temp
            if GET_VALIDATION_DATA:
                self.validationFitLinePlotCurves()
            else:
                self.fitLinePlotCurves()
            self._displayLensEncoderProperties()
        except RunLensEncoderException as e:
            self.session.lem.copy(lem_copy)
            raise e
        except LensEncoderFitDataException as e:
            raise e

    def lensValueChangeLock(self, mpf: float, use_focus: bool=True, use_iris: bool=True, use_zoom: bool=True, timeout: float=10.0, interval: float=0.1):
        '''
        Function runs until motor position and lens values have arrived at the desired position and are stable
        @param mpf: Motor position final
        @param use_focus: Use focus motor
        @param use_iris: Use iris motor
        @param use_zoom: Use zoom motor
        '''
        n = 0
        while n < timeout:
            if self.encoder_thread_is_cancelled:
                raise RunLensEncoderException("Lens encoder process cancelled")
            send_ping(self.scm.context)
            fvc = self.mcm.context.get_focus(raw=True)
            ivc = self.mcm.context.get_iris(raw=True)
            zvc = self.mcm.context.get_zoom(raw=True)
            time.sleep(interval)
            fmp = mpf
            imp = mpf
            zmp = mpf
            if use_focus:
                fmp = float(CmotionPacket.read_status_packet(self.scm.context.last_receive).focus_status_data.motor_pos)
            if use_iris:
                imp = float(CmotionPacket.read_status_packet(self.scm.context.last_receive).iris_status_data.motor_pos)
            if use_zoom:
                zmp = float(CmotionPacket.read_status_packet(self.scm.context.last_receive).zoom_status_data.motor_pos)
            fvn = self.mcm.context.get_focus(raw=True)
            ivn = self.mcm.context.get_iris(raw=True)
            zvn = self.mcm.context.get_zoom(raw=True)
            print(f"{round(mpf, 3)} -> {round(fmp, 3)}, {round(imp, 3)}, {round(zmp, 3)} //// {round(fvc, 3)}, {round(ivc, 3)}, {round(zvc, 3)} -> {round(fvn, 3)}, {round(ivn, 3)}, {round(zvn, 3)}")

            if math.isclose(fmp, mpf, abs_tol=5) and math.isclose(imp, mpf, abs_tol=5) and math.isclose(zmp, mpf, abs_tol=5):
                if math.isclose(fvc, fvn, abs_tol=3) and math.isclose(ivc, ivn, abs_tol=3) and math.isclose(zvc, zvn, abs_tol=3):
                    return
            n += interval
        raise RunLensEncoderException("Lens encoder process timed out")
    
    # temp
    def validationFitLinePlotCurves(self):
        try:
            self.session.lem.fit_focus_curve()
        except Exception as e:
            self.session.lem._lens_mappings_["focus"]["curve"]["parameters"] = []
        try:
            self.session.lem.fit_iris_curve()
        except Exception as e:
            self.session.lem._lens_mappings_["iris"]["curve"]["parameters"] = []
    
    def fitLinePlotCurves(self):
        focus_fit_error = False
        iris_fit_error = False
        zoom_fit_error = False
        # Fit the data
        # If the R^2 value is less than 0.98, LensEncoderModelException is caught
        # If the line could not be fit via polytrope, try linear interpolation if there are more than 40 samples

        # FOCUS
        try:
            self.session.lem.fit_focus_curve()
        except LensEncoderModelException as e:
            focus_fit_error = True
        except Exception as e:
            if len(self.session.lem.get_values(type="focus")) >= 40:
                self._writeToEncoderDebugWindow(level="warning", msg=f"Error fitting curve to focus data. Using linear interpolation")
                self.session.lem.fit_focus_curve(force_linear=True)
            else:
                self._writeToEncoderDebugWindow(level="error", msg=f"Error fitting focus data")
                focus_fit_error = True
        # IRIS
        try:
            self.session.lem.fit_iris_curve()
        except LensEncoderModelException as e:
            iris_fit_error = True
        except Exception as e:
            if len(self.session.lem.get_values(type="iris")) >= 40:
                self._writeToEncoderDebugWindow(level="warning", msg=f"Error fitting curve to iris data. Using linear interpolation")
                self.session.lem.fit_iris_curve(force_linear=True)
            else:
                self._writeToEncoderDebugWindow(level="error", msg=f"Error fitting iris curve")
                iris_fit_error = True
        # ZOOM
        if not self.session.settings.get_is_prime():
            try:
                self.session.lem.fit_zoom_curve() 
            except Exception as e:
                self._writeToEncoderDebugWindow(level="error", msg=f"Error fitting zoom curve")
                zoom_fit_error = True

        print(self.session.lem.get_parameters(type="focus"))
        print(self.session.lem.get_parameters(type="iris"))
        
        # If any of the fits failed, raise the exception
        if focus_fit_error or iris_fit_error or zoom_fit_error:
            error_target = []
            if focus_fit_error:
                error_target.append("FOCUS")
            if iris_fit_error:
                error_target.append("IRIS")
            if zoom_fit_error:
                error_target.append("ZOOM")
            raise LensEncoderFitDataException(f"Error fitting {error_target} data.\n\nTry again or consider increasing the number of samples to greater than 39 to force a linear interpolation of the data")

    def makeRunLensEncoderWorker(self):
        worker = RunLensEncoderWorker(self.runLensEncode_fn, serial_context=self.scm.context, metadata_context=self.mcm.context)
        worker.signals.run_started.connect(self._s_runStarted)
        worker.signals.run_lem_cleared.connect(self._s_runLensEncoderCleared)
        worker.signals.run_sampled.connect(self._s_runSampled)
        worker.signals.run_success.connect(self._s_runSuccess)
        worker.signals.run_error.connect(self._s_runError)
        worker.signals.run_finished.connect(self._s_runFinished)
        return worker
    
    def _s_runStarted(self):
        # temp
        self.data_start_time = time.time()
        self._writeToEncoderDebugWindow(level="success", msg=f"Beginning Sample Collection...")

    def _s_runLensEncoderCleared(self):
        self.ep_controller.updateAllGraphs()

    def _s_runSampled(self):
        self.ep_controller.updateAllLineGraphs()
        self.pb_controller.complete_nugget()
        current_motor_pos = float(CmotionPacket.read_status_packet(self.scm.context.last_receive).focus_status_data.motor_pos)
        current_focus_val = self.mcm.context.get_focus(raw=True)
        current_iris_val = self.mcm.context.get_iris(raw=True)
        current_zoom_val = self.mcm.context.get_zoom(raw=True)
        if self.thread_pool.activeThreadCount() > 0:
            self._writeToEncoderDebugWindow(level="info", msg=f"Sampled: Focus ({current_focus_val}, {current_motor_pos}) Iris ({current_iris_val}, {current_motor_pos}) Zoom ({current_zoom_val}, {current_motor_pos})")

    def _s_runSuccess(self):
        self._displayLensEncoderProperties()
        self._writeToEncoderDebugWindow(level="success", msg=f"Sample Collection Successful!")
        self.session.lens_encoder_fitted.emit()

    def _s_runError(self, exc_info: tuple):
        if exc_info[0] == RunLensEncoderException:
            self._writeToEncoderDebugWindow(level="warning", msg=exc_info[1])
        elif exc_info[0] == LensEncoderFitDataException:
            StandardErrorDialog(title="Lens Encoder Fit Error", message=str(exc_info[1]))
        
        self.pb_controller.reset()
        self.ep_controller.updateAllGraphs()

    def _s_runFinished(self):
        self.debug_window.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.mw.TB_LensEncoderStartToolButton.setIcon(QIcon(play))
        self.mw.TB_LensEncoderStartToolButton.setText("Start")
        self.mw.TB_LensEncoderClearToolButton.setEnabled(True)
        self.encoder_thread_is_cancelled = False
        self.ep_controller.updateAllGraphs()
        # temp
        if GET_VALIDATION_DATA:
            self.writeValidationToFile()
            if VALIDATION_START_SAMPLE_COUNT != VALIDATION_END_SAMPLE_COUNT:
                VALIDATION_START_SAMPLE_COUNT += 2
                self._onStartLensEncoderClicked()

        if GET_TWIN_DATA:
            # write the focus values and motor positions to a csv file called focus_twin_data.csv
            focus_values = self.session.lem.get_values(type="focus")
            focus_motor_positions = self.session.lem.get_motor_positions(type="focus")
            # write two rows of data to the csv file. Row 1 is the focus values and row 2 is the motor positions
            with open("focus_twin_data.csv", "w", newline='') as f:
                writer = csv.writer(f)
                for i in range(len(focus_values)):
                    writer.writerow([focus_values[i], focus_motor_positions[i]])
            # write the iris values and motor positions to a csv file called iris_twin_data.csv
            iris_values = self.session.lem.get_values(type="iris")
            iris_motor_positions = self.session.lem.get_motor_positions(type="iris")
            with open("iris_twin_data.csv", "w", newline='') as f:
                writer = csv.writer(f)
                for i in range(len(iris_values)):
                    writer.writerow([iris_values[i], iris_motor_positions[i]])

    def _onSessionFileLoaded(self):
        self.ep_controller.updateAllGraphs()
        self._displayLensEncoderProperties()
        self.debug_window.clear()
        self.pb_controller.reset()
        if not self.session.lem.get_values(type="focus"):
            self._writeToEncoderDebugWindow(level="warning", msg=f"No focus mappings found for focus")
        else:
            self.mw.SB_LensEncoderSampleSpinBox.setValue(len(self.session.lem.get_values(type="iris")))
            if self.session.lem.focus_is_fitted():
                self.session.lens_encoder_fitted.emit()
        if not self.session.lem.get_values(type="iris"):
            self._writeToEncoderDebugWindow(level="warning", msg=f"No iris mappings found for iris")
        if not self.session.lem.get_values(type="zoom"):
            self._writeToEncoderDebugWindow(level="warning", msg=f"No zoom mappings found for zoom")

    def _onSessionFileNew(self):
        self.ep_controller.updateAllGraphs()
        self._displayLensEncoderProperties()
        self.pb_controller.reset()
        self.debug_window.clear()
        self._writeToEncoderDebugWindow(level="info", msg="Created new lens encoder mapping")
        self.session.lens_encoder_cleared.emit()

    def _onSettingPrimeChanged(self, is_prime: bool):
        self.ep_controller.updateAllGraphs()
        self.mw.L_ZoomEncoderGraphLabel.setEnabled(not is_prime)

    def _writeToEncoderDebugWindow(self, level: str, msg: str):
        assert level in ['info', 'warning', 'error', 'success']
        level_cmap = {"info": "white", "warning": "yellow", "error": "red", "success": "green"}
        self.debug_window.append(f"<font color='{level_cmap[level]}'>{msg}</font>")
