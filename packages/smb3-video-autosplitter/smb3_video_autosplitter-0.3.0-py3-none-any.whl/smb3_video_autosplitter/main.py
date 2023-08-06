"""
video based autosplitter for smb3
"""
import logging

from pygrabber.dshow_graph import FilterGraph

from smb3_video_autosplitter.autosplitter import Autosplitter
from smb3_video_autosplitter.livesplit import LivesplitConnectFailedException
from smb3_video_autosplitter.opencv import OpenCV
from smb3_video_autosplitter.settings import Settings

from smb3_video_autosplitter.logging import initialize_logging

LOGGER = logging.getLogger(__name__)
SETTINGS = Settings.load()


def print_camera_info():
    graph = FilterGraph()
    input_devices = graph.get_input_devices()
    video_capture_source = SETTINGS.video_capture_source
    if (
        video_capture_source == None
        or video_capture_source == -1
        or video_capture_source >= len(input_devices)
    ):
        LOGGER.warning(
            "No camera selected or invalid, please update to one of the below:"
        )
        LOGGER.warning(input_devices)
        exit()
    LOGGER.info(f"Selected video source: {input_devices[video_capture_source]}")


def main():
    initialize_logging(
        file_log_level=SETTINGS.file_log_level,
        console_log_level=SETTINGS.console_log_level,
    )
    print_camera_info()
    opencv = OpenCV(
        SETTINGS.video_capture_source,
        SETTINGS.show_capture_video,
        SETTINGS.write_capture_video,
    )
    try:
        autosplitter = Autosplitter(SETTINGS)
    except LivesplitConnectFailedException:
        LOGGER.warning("Failed to connect to livesplit, is it running?")
        exit()
    while True:
        opencv.tick()
        autosplitter.tick(opencv.frame)


if __name__ == "__main__":
    main()
