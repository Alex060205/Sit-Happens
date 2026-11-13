import cv2


class Camera:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.capture = None

    def open(self):
        # not opening the camera twice
        if self.capture is not None and self.capture.isOpened():
            return True

        self.capture = cv2.VideoCapture(self.camera_index)

        if not self.capture.isOpened():
            self.close()
            return False

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        return True

    def read_frame(self):
        if self.capture is None:
            return None

        success, frame = self.capture.read()

        if not success:
            return None

        return frame

    def close(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None