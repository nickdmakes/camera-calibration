import math
import time
from datetime import datetime
import numpy as np
from PyQt6 import QtCore
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QProgressBar

from interface.app.main_window import Ui_MainWindow as MainWindow
from interface.calibration_command.ui.video_capture_window import VideoCaptureWindow

from interface.connection.capture_connection.capture_context_manager import CaptureContextManager
from interface.connection.serial_connection.serial_context_manager import SerialContextManager
from interface.connection.metadata_connection.metadata_context_manager import MetadataContextManager

from interface.calibration_command.data_browser.calibration_data_browser_controller import CalibrationDataBrowserController
from interface.session.calibration_session import CalibrationSession
from interface.session.models.data_model import CalibrationDataPoint, CalibrationDataModel
from interface.session.models.settings_model import SettingsModel
from interface.calibration_command.workers.run_image_gather import RunImageGatherWorker, RunImageGatherSignals, RunImageGatherException
from interface.calibration_command.workers.run_camera_calibration import RunCameraCalibrationWorker, RunCameraCalibrationSignals

from assets.assets import cancel, calculate, collect

from interface.calibration_command.calibration_utils import generate_focus_points, generate_zoom_points
from calibration.camera_calibration_api import calculate_corners, detect_checkerboard_motion, calibrate_camera, ImageCornersPayload

from network.cmotion.packet import CmotionPacket
from network.cmotion.api import send_ping, set_motor_pos

class CalibrationProgressBarController:
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



class CalibrationCommandController:
    def __init__(self, mw: MainWindow, cw: VideoCaptureWindow, session: CalibrationSession, scm: SerialContextManager, mcm: MetadataContextManager, ccm: CaptureContextManager):
        super().__init__()
        self.mw = mw
        self.cw = cw
        self.session = session
        self.scm = scm
        self.mcm = mcm
        self.ccm = ccm
        self.last_run_settings = None
        self.is_resuming_run = False
        self.pb_controller = CalibrationProgressBarController(progress_bar=self.mw.PB_CalibrationProgressBar)
        self.db_controller = CalibrationDataBrowserController(mw, self.session)
        self.setupUi()
        self.connectSignalsSlots()
        self.capture_button_pressed = False
        self.gather_thread_is_cancelled = False
        self.calibrate_thread_is_cancelled = False
        self.calibration_threadpool = QtCore.QThreadPool()

    def setupUi(self):
        self.mw.PB_CalibrationProgressBar.setValue(0)

    def connectSignalsSlots(self):
        # Context Manager Signals
        self.ccm.frame_received.connect(self._captureFrameReceived)
        # Session Signals
        self.session.session_file_loaded.connect(self._onSessionFileLoaded)
        self.session.session_file_new.connect(self._onSessionFileNew)
        # Toolbar Signals
        self.mw.TB_CalibrationGatherToolButton.clicked.connect(self._onImageGatherClicked)
        self.mw.TB_CalibrationCalculateToolButton.clicked.connect(self._onCalibrateClicked)
        # Data Browser Signals
        self.session.data_updated.connect(self._onSessionDataUpdated)
        # Video Capture Window Signals
        self.cw.capture_button.pressed.connect(self._onCaptureButtonPressed)

    def _onSessionFileLoaded(self):
        self.db_controller.updateBrowser()
        self.db_controller.updateDataPreview()
        self.pb_controller.reset()

    def _onSessionFileNew(self):
        self.db_controller.updateBrowser()
        self.db_controller.updateDataPreview()
        self.pb_controller.reset()

    def _onSessionDataUpdated(self):
        self.session.dirty = True

    def _onCaptureButtonPressed(self):
        self.capture_button_pressed = True

    def _captureFrameReceived(self, frame):
        self.cw.updatePixmap(frame)

    def _onImageGatherClicked(self):
        if self.calibration_threadpool.activeThreadCount() > 0:
            self.gather_thread_is_cancelled = True
        else:
            if not self.db_controller.isFullyCollected():
                if self._showImageGatherDataExistsWindow():
                    self.is_resuming_run = True
                    if not self.last_run_settings.soft_equals(self.session.settings):
                        if self._showSettingsModifiedWindow():
                            self.session.settings.copy(self.last_run_settings)
                        else:
                            return
                else:
                    self.is_resuming_run = False
            self.mw.TB_CalibrationGatherToolButton.setIcon(QIcon(cancel))
            self.mw.TB_CalibrationGatherToolButton.setText("Cancel")
            worker = self._makeImageGatherWorker()
            self.calibration_threadpool.start(worker)
            self.last_run_settings = SettingsModel()
            self.last_run_settings.copy(self.session.settings)

    def _makeImageGatherWorker(self):
        worker = RunImageGatherWorker(self._runImageGather_fn)
        worker.signals.run_started.connect(self._s_imageGatherRunStarted)
        worker.signals.run_data_points_generated.connect(self._s_imageGatherRunPointsReady)
        worker.signals.run_sampled.connect(self._s_imageGatherRunSampled)
        worker.signals.run_success.connect(self._s_imageGatherRunSuccess)
        worker.signals.run_error.connect(self._s_imageGatherRunError)
        worker.signals.run_finished.connect(self._s_imageGatherRunFinished)
        return worker

    def _runImageGather_fn(self, signals: RunImageGatherSignals):
        iris_pos = self.session.lem.predict_iris_motor_pos(4)
        set_motor_pos(self.scm.context, value=iris_pos, type="i", excecute_cmd=0, percent=False)
        self.lensValueChangeLock_fiz(fmpf=-1, zmpf=-1, impf=iris_pos, timeout=10.0, interval=0.1)
        
        # make a copy of the session data
        data_copy = CalibrationDataModel()
        data_copy.copy(self.session.data)

        # get focus points and motor positions
        focus_points = generate_focus_points(self.session.settings, self.session.lem)
        zoom_points = generate_zoom_points(self.session.settings, self.session.lem)
        num_images = self.session.settings.get_num_images_per_config()
        is_prime = self.session.settings.get_is_prime()
        gather_mode = self.session.settings.get_image_gather_mode()
        hold_still_time = self.session.settings.get_time_to_hold_still() if gather_mode == 0 else 0
        total_num_images = len(focus_points)*len(zoom_points)*num_images
        
        self.pb_controller.start_process(n_samples=total_num_images) 
        signals.run_data_points_generated.emit([focus_points, zoom_points, num_images])

        self.capture_button_pressed = False

        try:
            for fpi, focus_point in enumerate(focus_points):
                self.cw.showTextOverlay(f"Move to {focus_point}cm")
                focus_motor_position = self.session.lem.predict_focus_motor_pos(focus_point)
                for zpi, zoom_point in enumerate(zoom_points):
                    if self.gather_thread_is_cancelled:
                        raise RunImageGatherException("Image gather cancelled")
                    zoom_motor_position = -1
                    if not is_prime:
                        zoom_motor_position = self.session.lem.predict_zoom_motor_pos(zoom_point)
                        set_motor_pos(self.scm.context, value=zoom_motor_position, type="z", excecute_cmd=0, percent=False)
                    set_motor_pos(self.scm.context, value=focus_motor_position, type="f", excecute_cmd=0, percent=False)
                    self.lensValueChangeLock_fiz(fmpf=focus_motor_position, zmpf=zoom_motor_position, impf=-1, timeout=10.0, interval=0.1)
                    self.cw.updateLeftLabel(f"Focus: {focus_point}cm")
                    self.cw.clearCoverageOverlay()
                    for i in range(num_images):
                        image_name = "image-" + str(i)
                        db_node = self.session.data.get_image_node(f"{focus_point:.1f}:{zoom_point:.1f}:{image_name}")
                        # if the target node already has a corner payload, reinsert the data into the session data and skip the image
                        if db_node.corner_payload is not None:
                            data_point = CalibrationDataPoint(float(focus_point), float(zoom_point), image_name, db_node.corner_payload, db_node.calibration_payload, image_data=db_node.image_data)
                            signals.run_sampled.emit(data_point)
                        else:
                            self.cw.updateRightLabel(f"Image Count: {num_images - i} -- {total_num_images - (fpi*len(zoom_points)*num_images + zpi*num_images + i)}")
                            # if in manual mode, wait for the user to press the capture button
                            if gather_mode == 1:
                                self.cw.updateCenterLabel("Press Capture")
                                while not self.capture_button_pressed:
                                    if self.gather_thread_is_cancelled:
                                        raise RunImageGatherException("Image gather cancelled")
                                    time.sleep(0.1)
                                self.capture_button_pressed = False
                            corner_payload, frame = self.checkerboardDetectionLock(motion_timein=hold_still_time)
                            self.cw.addImagePointsToCoverageOverlay(corner_payload.image_points)
                            data_point = CalibrationDataPoint(float(focus_point), float(zoom_point), image_name, corner_payload, None, image_data=frame)
                            signals.run_sampled.emit(data_point)
        except Exception as e:
            # self.session.data.copy(data_copy)
            raise e

            
    def checkerboardDetectionLock(self, motion_timein: float=2.0) -> tuple[ImageCornersPayload, np.array]:
        '''
        Function runs until checkerboard corners are detected and the checkerboard is stable
        @param pattern_size: Tuple of the checkerboard pattern size (rows, columns)
        @param motion_timein: Time in seconds to wait for the checkerboard to be stable
        @return: Tuple of the checkerboard corners and the frame the checkerboard was detected in
        '''
        last_frame = None
        last_corners = None
        motion_start_time = time.time()
        while True:
            if not self.ccm.context.is_running() or not self.scm.context.is_running() or not self.mcm.context.is_running():
                raise RunImageGatherException("Lost connection to serial port or metadata server or capture server")
            if self.gather_thread_is_cancelled:
                raise RunImageGatherException("Image gather cancelled")
            current_frame = self.ccm.context.get_last_frame()
            checkerboard_rows = self.session.settings.get_checkerboard_rows()
            checkerboard_columns = self.session.settings.get_checkerboard_columns()
            current_corners = calculate_corners(current_frame, (checkerboard_rows, checkerboard_columns))
            if current_corners is not None:
                if last_frame is not None and last_corners is not None and current_frame is not None and current_corners is not None:
                    motion = detect_checkerboard_motion(last_frame, current_frame)
                    if not motion:
                        motion_end_time = time.time()
                        time_diff = motion_end_time - motion_start_time
                        if time_diff > motion_timein:
                            print("------------------- Checkerboard Recorded -------------------")
                            self.cw.updateCenterLabel("Checkerboard Recorded", sample_success=True)
                            self.cw.flashFrame()
                            time.sleep(1)
                            return current_corners, current_frame
                        print("Still:", time_diff)
                        time.sleep(0.05)
                        time_till_motion = motion_timein - time_diff
                        self.cw.updateCenterLabel(f"Hold Still: {time_till_motion:.2f}")
                    else:
                        print("CHECKERBOARD MOTION DETECTED")
                        self.cw.updateCenterLabel("Checkerboard Motion Detected")
                        time.sleep(0.25)
                        motion_start_time = time.time()
            else:
                print("No corners detected")
                self.cw.updateCenterLabel("No Corners Detected")
                motion_start_time = time.time()
                time.sleep(0.25)
            last_frame = current_frame
            last_corners = current_corners

    def lensValueChangeLock_fiz(self, fmpf: int = -1, impf: int = -1, zmpf: int = -1, timeout: float=10.0, interval: float=0.1):
        '''
        Function runs until motor position and lens values have arrived at the desired position and are stable
        @param fmpf: Focus motor position final. If -1, the lock will not wait for the focus motor position to arrive at a specific value
        @param impf: Iris motor position final. If -1, the lock will not wait for the iris motor position to arrive at a specific value
        @param zmpf: Zoom motor position final. If -1, the lock will not wait for the zoom motor position to arrive at a specific value
        @param timeout: Time in seconds to wait for the lens values to arrive at the desired position
        @param interval: Time in seconds to wait between checking motor position and lens values
        '''
        n = 0
        while n < timeout:
            if not self.scm.context.is_running() or not self.mcm.context.is_running() or not self.mcm.context.is_running():
                raise RunImageGatherException("Lost connection to serial port or metadata server or capture server")
            if self.gather_thread_is_cancelled:
                raise RunImageGatherException("Image gather cancelled")
            send_ping(self.scm.context)
            fvc = self.mcm.context.get_focus(raw=True)
            ivc = self.mcm.context.get_iris(raw=True)
            zvc = self.mcm.context.get_zoom(raw=True)
            time.sleep(interval)
            fmp = fmpf
            imp = impf
            zmp = zmpf
            if fmpf > -1:
                fmp = float(CmotionPacket.read_status_packet(self.scm.context.last_receive).focus_status_data.motor_pos)
            if impf > -1:
                imp = float(CmotionPacket.read_status_packet(self.scm.context.last_receive).iris_status_data.motor_pos)
            if zmpf > -1:
                zmp = float(CmotionPacket.read_status_packet(self.scm.context.last_receive).zoom_status_data.motor_pos)
            fvn = self.mcm.context.get_focus(raw=True)
            ivn = self.mcm.context.get_iris(raw=True)
            zvn = self.mcm.context.get_zoom(raw=True)
            print(f"FMP: {round(fmpf, 3)} -> {round(fmp, 3)} // IMP: {round(impf, 3)} -> {round(imp, 3)} // ZMP: {round(zmpf, 3)} -> {round(zmp, 3)} |||| FVC: {round(fvc, 3)} -> {round(fvn, 3)} // IVC: {round(imp, 3)} -> {round(ivn, 3)} // ZVC: {round(zmp, 3)} -> {round(zvn, 3)}")
            if math.isclose(fmp, fmpf, abs_tol=5) and math.isclose(imp, impf, abs_tol=5) and math.isclose(zmp, zmpf, abs_tol=5):
                if math.isclose(fvc, fvn, abs_tol=3) and math.isclose(ivc, ivn, abs_tol=3) and math.isclose(zvc, zvn, abs_tol=3):
                    return
            n += interval
        raise RunImageGatherException("Lens value change lock timed out")

    def _s_imageGatherRunStarted(self):
        pass

    def _s_imageGatherRunPointsReady(self, points: list):
        if not self.is_resuming_run:
            self.db_controller.clearModelAndPreloadData(points[0], points[1], points[2])
            self.db_controller.updateDataPreview()

    def _s_imageGatherRunSampled(self, data_point: CalibrationDataPoint):
        self.db_controller.addData(data_point)
        self.pb_controller.complete_nugget()

    def _s_imageGatherRunSuccess(self):
        self.cw.updateLeftLabel("Complete")
        self.cw.updateRightLabel("Complete")
        self.cw.showTextOverlay("Image Gather Complete")

    def _s_imageGatherRunError(self, error):
        print(error)
        self.cw.clearTopLabels()
        self.pb_controller.reset()

    def _s_imageGatherRunFinished(self):
        self.mw.TB_CalibrationGatherToolButton.setIcon(QIcon(collect))
        self.mw.TB_CalibrationGatherToolButton.setText("Collect")
        self.db_controller.updateBrowser()
        if self.gather_thread_is_cancelled:
            self.cw.clearTopLabels()
        self.gather_thread_is_cancelled = False

    def _onCalibrateClicked(self):
        self.mw.TB_CalibrationCalculateToolButton.setIcon(QIcon(cancel))
        self.mw.TB_CalibrationCalculateToolButton.setText("Cancel")
        if self.calibration_threadpool.activeThreadCount() > 0:
            self.calibrate_thread_is_cancelled = True
        else:
            worker = self._makeCameraCalibrationWorker()
            self.calibration_threadpool.start(worker)

    def _makeCameraCalibrationWorker(self):
        worker = RunCameraCalibrationWorker(self._runCameraCalibration_fn)
        worker.signals.run_started.connect(self._s_cameraCalibrationRunStarted)
        worker.signals.run_sampled.connect(self._s_cameraCalibrationRunSampled)
        worker.signals.run_success.connect(self._s_cameraCalibrationRunSuccess)
        worker.signals.run_error.connect(self._s_cameraCalibrationRunError)
        worker.signals.run_finished.connect(self._s_cameraCalibrationRunFinished)
        return worker
    
    def _runCameraCalibration_fn(self, signals: RunCameraCalibrationSignals):
        backup_session = CalibrationSession()
        backup_session.copy(self.session)
        leaf_data = self.session.data.get_leaf_nodes()
        for leaf in leaf_data:
            corner_payload = leaf.corner_payload
            object_points = corner_payload.object_points
            image_points = corner_payload.image_points
            calibration_payload = calibrate_camera([object_points], [image_points], corner_payload.image_shape)
            if calibration_payload is not None:
                print("Image Node Camera calibration successful")
                new_calibration_payload = CalibrationDataPoint(leaf.focus, leaf.zoom, leaf.image, corner_payload, calibration_payload, leaf.image_data)
                signals.run_sampled.emit(new_calibration_payload)
                self.pb_controller.reset() 
            else:
                raise Exception("Camera calibration failed")
            
        # get all zoom nodes
        for focus_node in self.session.data.get_all_focus_nodes():
            focus_id = focus_node.get_focus_id()
            zoom_nodes = self.session.data.get_zoom_nodes_from_id(focus_id)
            for zoom_node in zoom_nodes:
                zoom_id = zoom_node.get_zoom_id()
                image_nodes = self.session.data.get_image_nodes_from_id(zoom_id)
                # make a list of object points and image points from each image node
                object_points = []
                image_points = []
                for image_node in image_nodes:
                    corner_payload = image_node.corner_payload
                    object_points.append(corner_payload.object_points)
                    image_points.append(corner_payload.image_points)
                # calculate camera calibration
                calibration_payload = calibrate_camera(object_points, image_points, corner_payload.image_shape)
                if calibration_payload is not None:
                    # calculate normalized camera intrinsics
                    zoom_node.calibration_payload = calibration_payload

        # if something goes wrong, recover the old data by copying the backup to self.session.data and reloading the data browser

    def _s_cameraCalibrationRunStarted(self):
        pass

    def _s_cameraCalibrationRunSampled(self, data_point: CalibrationDataPoint):
        self.db_controller.addData(data_point)

    def _s_cameraCalibrationRunSuccess(self):
        pass

    def _s_cameraCalibrationRunError(self, error):
        print(error) 

    def _s_cameraCalibrationRunFinished(self):
        self.mw.TB_CalibrationCalculateToolButton.setIcon(QIcon(calculate))
        self.mw.TB_CalibrationCalculateToolButton.setText("Calibrate")
        self.db_controller.updateBrowser()
        self.calibrate_thread_is_cancelled = False

    def _showErrorWindow(self, msg: str, details: str = None):
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Icon.Critical)
        mb.setWindowTitle("Error")
        mb.setText(str(msg))
        if details:
            mb.setDetailedText(details)
        mb.exec()

    def _showImageGatherDataExistsWindow(self):
        res = QMessageBox.question(self.mw, "Data Exists", "Data already exists for this session. Would you like to resume collecting images?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Reset)
        if res == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False
        
    def _showSettingsModifiedWindow(self):
        res = QMessageBox.question(self.mw, "Settings Modified", "When resuming image collection, settings must not change between runs. Would you like to revert settings back to the last run?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if res == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False
