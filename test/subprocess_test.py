import subprocess

# add root directory to the python path
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from assets.assets import ffmpeg_path

def get_decklink_devices() -> list:
    # make ffmpeg command to list available devices
    command = [
        ffmpeg_path,
        "-hide_banner",
        "-sources",
        "decklink"
    ]

    # start the ffmpeg process
    capture = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    output, error = capture.communicate()

    if error:
        raise Exception(error.decode())
    
    devices = []
    for line in output.decode().split("\n"):
        if line.startswith("  "):
            device = line[line.find("[")+1:line.rfind("]")]
            devices.append(device)

    return devices

def get_decklink_formats(device: str):
    # make ffmpeg command to list available devices
    command = [
        ffmpeg_path,
        "-hide_banner",
        "-f",
        "decklink",
        "-list_formats",
        "1",
        "-i",
        device
    ]

    # start the ffmpeg process
    capture = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    output, error = capture.communicate()

    formats = []
    for line in error.decode().split("\n"):
        if "fps" in line:
            parts = line.split("\t")
            code = parts[1].strip()
            format = parts[-1][:parts[-1].find("fps")]
            res_fps_parts = format.split(" ")
            resolution = res_fps_parts[0]
            fps_divide = res_fps_parts[2]
            operands = fps_divide.split("/")
            fps = round(float(operands[0]) / float(operands[1]), 2)
            formats.append((code, resolution, str(fps)))

    return formats

def capture_decklink_3_seconds(device: str, format_code: str, output_file: str):
    # make ffmpeg command to list available devices
    command = [
        ffmpeg_path, 
        "-hide_banner", 
        "-raw_format", "uyvy422", 
        "-format_code", format_code,
        "-video_input", "hdmi",
        "-f", "decklink",
        "-i", device, 
        "-c:a", "copy", 
        "-c:v", "copy",
        "-t", "3",
        "-f", "avi",
        "pipe:1",
    ]

    # start the ffmpeg process
    capture = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    output, error = capture.communicate()

    print("output:", output)
    print("error:", error.decode())


if __name__ == "__main__":
    devices = get_decklink_devices()
    print("devices:", devices)

    formats = get_decklink_formats(device=devices[0])
    print("formats:", formats)

    # capture_decklink_3_seconds(device=devices[0], format_code="Hp60", output_file="output.avi")
