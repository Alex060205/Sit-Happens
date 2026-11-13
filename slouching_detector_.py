from pathlib import Path
import math
import cv2
import mediapipe as mp


class SlouchingDetector:
    def __init__(self):
        model_path = (
            Path(__file__).resolve().parent
            / "models"
            / "pose_landmarker_lite.task"
        )

        if not model_path.is_file():
            raise FileNotFoundError(
                f"No se encontro el modelo: {model_path}"
            )

        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(model_path)
            ),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
        )

        self.detector = (
            mp.tasks.vision.PoseLandmarker.create_from_options(options)
        )

        self.baseline = None
        self.last_points = {}

        # inital vlaues to adjust during the testing
        # they are just prototypes, not medical criteria
        self.head_angle_limit = 12.0
        self.shoulder_angle_limit = 10.0
        self.head_position_limit = 0.15

    def _get_measurements(self, frame):
        self.last_points = {}

        if frame is None:
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        result = self.detector.detect(image)

        if not result.pose_landmarks:
            return None

        landmarks = result.pose_landmarks[0]
        height, width = frame.shape[:2]

        landmark_ids = {
            "nose": 0,
            "left_eye": 2,
            "right_eye": 5,
            "left_shoulder": 11,
            "right_shoulder": 12,
        }

        points = {}

        for name, landmark_id in landmark_ids.items():
            landmark = landmarks[landmark_id]

            # no evaluamos puntos poco visibles o fuera de la imagen
            if landmark.visibility < 0.6 or landmark.presence < 0.6:
                return None

            if not (0 <= landmark.x <= 1 and 0 <= landmark.y <= 1):
                return None

            points[name] = (
                landmark.x * width,
                landmark.y * height,
            )

        left_shoulder = points["left_shoulder"]
        right_shoulder = points["right_shoulder"]
        nose = points["nose"]

        shoulder_width = math.dist(left_shoulder, right_shoulder)

        if shoulder_width < 20:
            return None

        shoulder_center_x = (
            left_shoulder[0] + right_shoulder[0]
        ) / 2

        shoulder_center_y = (
            left_shoulder[1] + right_shoulder[1]
        ) / 2

        self.last_points = points

        return {
            "head_angle": self._line_angle(
                points["left_eye"],
                points["right_eye"],
            ),
            "shoulder_angle": self._line_angle(
                left_shoulder,
                right_shoulder,
            ),
            # normalizamos para reducir el efecto de la distancia
            "head_x": (
                nose[0] - shoulder_center_x
            ) / shoulder_width,
            "head_y": (
                shoulder_center_y - nose[1]
            ) / shoulder_width,
        }

    def _line_angle(self, point_a, point_b):
        # ordena de izquierda a derecha dentro de la imagen
        if point_a[0] > point_b[0]:
            point_a, point_b = point_b, point_a

        return math.degrees(
            math.atan2(
                point_b[1] - point_a[1],
                point_b[0] - point_a[0],
            )
        )

    def calibrate(self, frame):
        measurements = self._get_measurements(frame)

        if measurements is None:
            return False

        self.baseline = measurements
        return True

    def analyze(self, frame):
        measurements = self._get_measurements(frame)

        result = {
            "tracking": measurements is not None,
            "calibrated": self.baseline is not None,
            "changed": None,
        }

        if measurements is None or self.baseline is None:
            return result

        head_angle_change = abs(
            measurements["head_angle"] - self.baseline["head_angle"]
        )

        shoulder_angle_change = abs(
            measurements["shoulder_angle"]
            - self.baseline["shoulder_angle"]
        )

        head_position_change = math.hypot(
            measurements["head_x"] - self.baseline["head_x"],
            measurements["head_y"] - self.baseline["head_y"],
        )

        result["changed"] = (
            head_angle_change > self.head_angle_limit
            or shoulder_angle_change > self.shoulder_angle_limit
            or head_position_change > self.head_position_limit
        )

        return result

    def close(self):
        if self.detector is not None:
            self.detector.close()
            self.detector = None