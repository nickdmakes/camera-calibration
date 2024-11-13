import threading
import sys
import os
import time
import numpy as np
import subprocess
import cv2
import enum

if __name__ == '__main__':
    import sys
    import os
    # add root directory to the path
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Base exception class for capture context
class FfmpegCaptureContextException(Exception):
    pass

# enum for capture context interface mode (decklink, dshow, avfoundation)
class CaptureContextInterfaceMode(enum.Enum):
    DECKLINK = 0
    DSHOW = 1
    AVFOUNDATION = 2

PIXEL_CONVERSION_MAP = {
    "uyvy422": cv2.COLOR_YUV2BGR_UYVY,
    "yuyv422": cv2.COLOR_YUV2BGR_YUY2,
}

class DecklinkCaptureFormat:
    def __init__(self, code: str, width: int, height: int, fps: str, pixel_format: str):
        self.code = code
        self.width = width
        self.height = height
        self.fps = fps
        self.pixel_format = pixel_format

    def __str__(self):
        return f"{self.code} {self.width}x{self.height} @ {self.fps}fps"
    
    def __repr__(self):
        return self.__str__()
    
class DShowCaptureFormat:
    def __init__(self, width: int, height: int, fps: str, pixel_format: str):
        self.width = width
        self.height = height
        self.fps = fps
        self.pixel_format = pixel_format

    def __str__(self):
        return f"{self.pixel_format} {self.width}x{self.height} @ {self.fps}fps"
    
    def __repr__(self):
        return self.__str__()

# Class FFmpegCaptureContext
# This class is used to maintain the capture context and expose a callback for received frames FFmpeg
class FFmpegCaptureContext:
    def __init__(self, path: str):
        # FFmpeg object variables
        self._exe_path_ = "ffmpeg"
        self._interface_mode_index = None
        self._selected_device_index = None
        self._selected_format_index = None
        self._modes_ = []
        self._devices_ = []
        self._formats_ = []
        self._valid_ = False

        # Context information
        self._is_running_ = False
        self._capture_ = None
        self._close_callback_ = lambda: None
        self._open_callback_ = lambda: None

        # Recent frame information
        self._last_frame_ = None

        # Received data thread variables
        self._received_thread_ = None
        self._recv_callback_ = lambda data: None

        self.setup_capture_context()

    def setup_capture_context(self):
        self._update_modes()
        self.set_interface_mode_index(0)

    def _update_validity(self):
            if self.no_devices_found() or self.no_formats_found() or self._selected_device_index is None or self._selected_format_index is None:
                self._valid_ = False
            else:
                self._valid_ = True

    def is_valid(self):
        return self._valid_

    def no_devices_found(self):
        return len(self._devices_) == 0
    
    def no_formats_found(self):
        return len(self._formats_) == 0
    
    def set_interface_mode_index(self, index: int):
        assert not self._modes_ == [], "No interface modes available"
        self._interface_mode_index = index

    def get_selected_interface_mode(self):
        return self._modes_[self._interface_mode_index]
    
    def get_interface_mode_list(self):
        return [self._get_interface_mode_string(mode) for mode in self._modes_]
    
    def _get_interface_mode_string(self, mode: CaptureContextInterfaceMode):
        if mode == CaptureContextInterfaceMode.DECKLINK:
            return "decklink"
        elif mode == CaptureContextInterfaceMode.DSHOW:
            return "dshow"
        elif mode == CaptureContextInterfaceMode.AVFOUNDATION:
            return "avfoundation"

    def set_selected_device_index(self, index: int):
        assert not self.no_devices_found(), "No devices found for selected interface mode"
        self._selected_device_index = index

    def get_selected_device(self):
        if self._selected_device_index is None:
            return None
        return self._devices_[self._selected_device_index]

    def get_device_list(self):
        return self._devices_

    def set_selected_format_index(self, index: int):
        assert not self.no_formats_found(), "No formats found for selected device"
        self._selected_format_index = index

    def get_selected_format(self):
        if self._selected_format_index is None:
            return None
        return self._formats_[self._selected_format_index]

    def get_format_list(self):
        return [str(format) for format in self._formats_]
    
    def get_last_frame(self):
        return self._last_frame_

    def _recv_func_(self, context):
        # set fps to 30 to avoid overloading the system using time
        st = time.time()
        while context.is_running():
            try:
                # read every 1/30 seconds
                while time.time() - st < 1/30:
                    time.sleep(0.001)
                st = time.time()
                width = context._formats_[context._selected_format_index].width
                height = context._formats_[context._selected_format_index].height
                frame = context._capture_.stdout.read(width*height*2)
                context._capture_.stdout.flush()
                if frame is None or len(frame) == 0:
                    continue
                frame = np.frombuffer(frame, dtype=np.uint8).reshape((height, width, 2))
                frame = cv2.cvtColor(frame, PIXEL_CONVERSION_MAP[context.get_selected_format().pixel_format])
                context._last_frame_ = frame
                context._recv_callback_(frame)
            except Exception as e:
                context.close(join=False)
                context.on_recv_error(e)
                return
        self._close_callback_()

    def set_recv_callback(self, callback):
        self._recv_callback_ = callback

    def on_recv_error(self, error: Exception):
        raise FfmpegCaptureContextException(f"FFmpeg Context Exception: {error}")

    def set_close_callback(self, callback):
        self._close_callback_ = callback

    def set_open_callback(self, callback):
        self._open_callback_ = callback

    def open(self):
        if self._is_running_:
            raise FfmpegCaptureContextException("Capture context is already running")
        elif not self._valid_:
            raise FfmpegCaptureContextException("Capture context is not valid")

        self._capture_ = self._open_capture()

        self._received_thread_ = threading.Thread(target=self._recv_func_, args=(self,))
        self._is_running_ = True
        self._received_thread_.setDaemon(True)
        self._received_thread_.setName("FFmpegCaptureThread")
        self._received_thread_.start()

        self._open_callback_()

    def close(self, join=True):
        self._is_running_ = False
        if self._received_thread_ is not None and join:
            self._received_thread_.join()
        if self._capture_ is not None:
            self._capture_.terminate()
            self._capture_.wait()
        self._close_callback_()

    def is_running(self):
        return self._is_running_
    
    def _update_modes(self):
        new_modes = []
        new_modes.append(CaptureContextInterfaceMode.DECKLINK)
        if sys.platform == "win32":
            new_modes.append(CaptureContextInterfaceMode.DSHOW)
        elif sys.platform == "darwin":
            new_modes.append(CaptureContextInterfaceMode.AVFOUNDATION)
        self._modes_ = new_modes
    
    def update_devices(self):
        mode = self.get_selected_interface_mode()
        if mode == CaptureContextInterfaceMode.DECKLINK:
            self._update_decklink_devices()
        elif mode == CaptureContextInterfaceMode.DSHOW:
            self._update_dshow_devices()
        elif mode == CaptureContextInterfaceMode.AVFOUNDATION:
            self._update_avfoundation_devices()
        self._update_validity()

    def update_formats(self):
        mode = self.get_selected_interface_mode()
        device = self.get_selected_device()
        if mode == CaptureContextInterfaceMode.DECKLINK:
            self._update_decklink_formats(device)
        elif mode == CaptureContextInterfaceMode.DSHOW:
            self._update_dshow_formats(device)
        elif mode == CaptureContextInterfaceMode.AVFOUNDATION:
            self._update_avfoundation_formats(device)
        self._update_validity()

    def _open_capture(self):
        mode = self.get_selected_interface_mode()
        if mode == CaptureContextInterfaceMode.DECKLINK:
            device = self.get_selected_device()
            format_code = self.get_selected_format().code
            return self.open_decklink_capture(device, format_code)
        elif mode == CaptureContextInterfaceMode.DSHOW:
            return self.open_dshow_capture()
        elif mode == CaptureContextInterfaceMode.AVFOUNDATION:
            self.open_avfoundation_capture()
    
    def _update_decklink_devices(self) -> list:
        command = [
            self._exe_path_,
            "-hide_banner",
            "-sources",
            "decklink"
        ]

        get_devices_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = get_devices_process.communicate(timeout=5)
        
        devices = []
        for line in output.decode().split("\n"):
            if line.startswith("  "):
                device = line[line.find("[")+1:line.rfind("]")]
                devices.append(device)

        self._devices_ = devices

    def _update_dshow_devices(self) -> list:
        command = [
            self._exe_path_,
            "-hide_banner",
            "-list_devices", "true",
            "-f", "dshow",
            "-i", "dummy"
        ]

        get_devices_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = get_devices_process.communicate(timeout=5)
        
        devices = []
        for line in error.decode().split("\n"):
            if "(video)" in line or "(audio, video)" in line:
                device = line[line.find('"')+1:line.rfind('"')]
                devices.append(device)

        self._devices_ = devices

    def _update_avfoundation_devices(self) -> list:
        pass
    
    def _update_decklink_formats(self, device: str):
        command = [
            self._exe_path_,
            "-hide_banner",
            "-f", "decklink",
            "-list_formats", "1",
            "-i", device
        ]

        get_formats_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = get_formats_process.communicate(timeout=5)

        formats = []
        for line in error.decode().split("\n"):
            if "fps" in line:
                parts = line.split("\t")
                code = parts[1].strip()
                format = parts[-1][:parts[-1].find("fps")]
                res_fps_parts = format.split(" ")
                resolution = res_fps_parts[0]
                width, height = resolution.split("x")
                fps_divide = res_fps_parts[2]
                operands = fps_divide.split("/")
                fps = round(float(operands[0]) / float(operands[1]), 2)
                formats.append(DecklinkCaptureFormat(code, int(width), int(height), str(fps), "uyvy422"))

        self._formats_ = formats

    def _update_dshow_formats(self, device: str):
        command = [
            self._exe_path_,
            "-hide_banner",
            "-list_options", "true",
            "-f", "dshow",
            "-i", f"video={device}"
        ]

        get_formats_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = get_formats_process.communicate(timeout=5)

        formats = []
        for line in error.decode().split("\n"):
            if "pixel_format" in line:
                parts = " ".join(line.split()).split(" ")
                pixel_format = parts[3][parts[3].find("=")+1:]
                resolution = parts[8][parts[8].find("=")+1:]
                width, height = resolution.split("x")
                fps = parts[9][parts[9].find("=")+1:]
                formats.append(DShowCaptureFormat(int(width), int(height), str(fps), pixel_format))

        self._formats_ = formats

    def _update_avfoundation_formats(self, device: str):
        pass
    
    def open_decklink_capture(self, device: str, format_code: str):
        command = [
            self._exe_path_, 
            "-hide_banner", 
            "-loglevel", "panic",
            "-raw_format", "uyvy422", 
            "-format_code", format_code,
            "-video_input", "sdi",
            "-f", "decklink",
            "-i", device, 
            "-preset", "ultrafast",
            "-threads", "2",
            "-r", "20",
            "-c:v", "rawvideo",
            "-an",
            "-f", "rawvideo",
            "pipe:1",
        ]

        width = self._formats_[self._selected_format_index].width
        height = self._formats_[self._selected_format_index].height
        capture_process = subprocess.Popen(command, 
                                           bufsize=height*width*2,
                                           shell=True,
                                           stdout=subprocess.PIPE)
        return capture_process
    
    def open_dshow_capture(self):
        device = self.get_selected_device()
        format = self.get_selected_format()
        command = [
            self._exe_path_,
            "-hide_banner",
            "-loglevel", "panic",
            "-rtbufsize", "1024M",
            "-video_size", f"{format.width}x{format.height}",
            "-pixel_format", format.pixel_format,
            "-framerate", format.fps,
            "-f", "dshow",
            "-i", f"video={device}",
            "-preset", "ultrafast",
            "-threads", "2",
            "-r", "20",
            "-an",
            "-f", "rawvideo",
            "pipe:1"
        ]

        width = format.width
        height = format.height
        capture_process = subprocess.Popen(command, 
                                            bufsize=height*width*2,
                                            shell=True,
                                            stdout=subprocess.PIPE)
        
        return capture_process
    
    def open_avfoundation_capture(self):
        pass

if __name__ == '__main__':
    context = FFmpegCaptureContext("ffmpeg")
    context.set_interface_mode_index(1)
    context.update_devices()
    context.set_selected_device_index(4)
    context.update_formats()
    context.set_selected_format_index(0)
    context._valid_ = True
    context.open()
    # loop for 10 seconds
    st = time.time()
    while time.time() - st < 10:
        frame = context.get_last_frame()
        if frame is not None:
            cv2.imshow("Frame", frame)
            cv2.waitKey(1)