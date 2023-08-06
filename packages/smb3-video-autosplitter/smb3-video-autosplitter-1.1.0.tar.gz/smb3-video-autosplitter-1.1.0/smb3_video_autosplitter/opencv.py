from pygrabber.dshow_graph import FilterGraph, FilterType
import cv2


class OpenCV:
    def __init__(
        self, video_capture_source, show_capture_video=False, write_capture_video=False
    ):
        self.show_capture_video = show_capture_video
        self.write_capture_video = write_capture_video
        self.graph = FilterGraph()
        self.graph.add_video_input_device(video_capture_source)
        self.graph.add_sample_grabber(self.on_frame_received)
        self.graph.add_null_render()
        self.graph.prepare_preview_graph()
        self.graph.run()
        self.frame = None
        if write_capture_video:
            video_input = self.graph.filters[FilterType.video_input]
            width, height = video_input.get_current_format()
            self.output_video = cv2.VideoWriter(
                "capture.avi", cv2.VideoWriter_fourcc(*"MPEG"), 60, (width, height)
            )

    def tick(self):
        self.graph.grab_frame()
        if self.show_capture_video and self.frame is not None:
            cv2.imshow("capture", self.frame)
            _ = cv2.waitKey(1)
        if self.write_capture_video and self.frame is not None:
            self.output_video.write(self.frame)

    def on_frame_received(self, frame):
        self.frame = frame
