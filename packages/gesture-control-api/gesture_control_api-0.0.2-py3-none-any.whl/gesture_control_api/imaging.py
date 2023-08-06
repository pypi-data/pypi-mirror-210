from typing import Tuple, Union

import numpy as np
import cv2


class FrameReader:
    def __init__(self, frame_source) -> None:
        pass

    def get_frame(self) -> Tuple[bool, np.ndarray]:
        pass


class OpenCvFrameReader(FrameReader):
    def __init__(self, frame_source: Union[int, str] = 0, size_of_frame_to_process: Tuple[int, int] = (640, 480)) -> None:
        self.cap = cv2.VideoCapture(frame_source)

        if self.cap is None or not self.cap.isOpened():
            raise IOError(f"Unable to access frame source: {frame_source}")
        
        self.size_of_frame_to_process = size_of_frame_to_process

    def get_frame(self) -> Tuple[bool, np.ndarray]:
        if not self.cap.isOpened():
            return (False, np.array([]))

        success, image = self.cap.read()

        if not success:
            return (False, np.array([]))

        # Resize for performance
        image = cv2.resize(image, self.size_of_frame_to_process, interpolation=cv2.INTER_AREA)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # To improve performance, optionally mark the image as not writeable to pass by reference.
        image.flags.writeable = False

        return (True, image)

    def __del__(self):
        self.cap.release()
