import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
from alarmManager import AlarmManager


class DistanceDetector:
    LEFT_EYE = 33
    RIGHT_EYE = 263

    def __init__(self, model_path: str = None, proximity_threshold: float = 0.80):
        """
        Args:
            model_path: Path to face_landmarker.task. Defaults to the same folder as this script.
            proximity_threshold: Relative distance below which the user is flagged as too close
                                 (e.g., 0.80 means 20% closer than calibrated baseline).
        """
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "face_landmarker.task"
            )

        self.proximity_threshold = proximity_threshold
        self.baseline_eye_dist = None

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.6,
            min_face_presence_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)


    def _get_eye_distance(self, frame: np.ndarray):
        """Detects facial landmarks and returns pixel distance between outer eye corners."""
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        results = self.detector.detect(mp_image)
        if not results.face_landmarks:
            return None, None

        landmarks = results.face_landmarks[0]
        left_eye = landmarks[self.LEFT_EYE]
        right_eye = landmarks[self.RIGHT_EYE]

        p1 = np.array([left_eye.x * w, left_eye.y * h])
        p2 = np.array([right_eye.x * w, right_eye.y * h])
        eye_dist = float(np.linalg.norm(p1 - p2))

        return eye_dist, (tuple(p1.astype(int)), tuple(p2.astype(int)))


    def calibrate(self, frame: np.ndarray) -> bool:
        """
        Sets the user's normal sitting distance baseline from the current frame.
        Returns True if a face was detected and calibrated, False otherwise.
        """
        eye_dist, _ = self._get_eye_distance(frame)
        if eye_dist is not None and eye_dist > 0:
            self.baseline_eye_dist = eye_dist
            return True
        return False


    def analyze(self, frame: np.ndarray) -> dict:
        """
        Analyzes a BGR frame and returns proximity tracking metrics for Person 3's UI.
        """
        eye_dist, eye_points = self._get_eye_distance(frame)

        if eye_dist is None or eye_dist <= 0:
            return {
                "tracking_succeeded": False,
                "calibrated": self.baseline_eye_dist is not None,
                "too_close": False,
                "relative_distance": None,
                "eye_points": None,
            }

        if self.baseline_eye_dist is None:
            return {
                "tracking_succeeded": True,
                "calibrated": False,
                "too_close": False,
                "relative_distance": 1.0,
                "eye_points": eye_points,
            }

        # Smaller value = closer to screen (e.g., 0.75 means 75% of normal distance)
        relative_distance = round(self.baseline_eye_dist / eye_dist, 2)
        too_close = bool(relative_distance < self.proximity_threshold)

        return {
            "tracking_succeeded": True,
            "calibrated": True,
            "too_close": too_close,
            "relative_distance": relative_distance,
            "eye_points": eye_points,
        }


    def close(self):
        self.detector.close()


# OLD CODE
'''
SOUND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alarm-blare.wav")

def play_alarm():
    pass
    #if os.path.exists(SOUND_PATH):
        # SND_FILENAME loads from disk; SND_ASYNC prevents freezing the webcam loop
        # want to loop every time the the audio ends
        #winsound.PlaySound(SOUND_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)

def stop_alarm():
    pass
    #winsound.PlaySound(None, winsound.SND_PURGE)


# --- Standalone test runner for Person 2 (ignored when imported by Person 3) ---
if __name__ == "__main__":
    ALARM_DELAY = 5.0

    cap = cv2.VideoCapture(0)
    distance_detector = DistanceDetector(proximity_threshold=0.80)
    sound_manager = AlarmManager(default_sound="sound-files/alarm-blare.wav", loop=True)

    too_close_start = None

    print("=== Screen Proximity Module Test ===")
    print("Press 'C' to calibrate | 'S' to select custom sound | 'Q' to quit")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        result = distance_detector.analyze(frame)

        if not result["tracking_succeeded"]:
            sound_manager.stop()
            too_close_start = None
            label = "Face not detected"
            color = (0, 165, 255)

        elif not result["calibrated"]:
            sound_manager.stop()
            too_close_start = None
            label = "Press 'C' to calibrate distance"
            color = (0, 220, 255)

        elif result["too_close"]:
            if too_close_start is None:
                too_close_start = time.time()

            elapsed = time.time() - too_close_start
            pct = int(result["relative_distance"] * 100)

            if elapsed >= ALARM_DELAY:
                label = f"TOO CLOSE! ({pct}%) - ALARM TRIGGERED"
                color = (0, 0, 255)
                sound_manager.play()  # Safe to call every frame; SoundManager handles state
            else:
                remaining = ALARM_DELAY - elapsed
                label = f"Too close ({pct}%) - Alarm in {remaining:.1f}s"
                color = (0, 140, 255)

        else:
            sound_manager.stop()
            too_close_start = None
            pct = int(result["relative_distance"] * 100)
            label = f"GOOD DISTANCE ({pct}%)"
            color = (0, 220, 0)

        # Draw eye line & status text
        if result["eye_points"]:
            p1, p2 = result["eye_points"]
            cv2.line(frame, p1, p2, color, 2)
            cv2.circle(frame, p1, 4, color, -1)
            cv2.circle(frame, p2, 4, color, -1)

        cv2.putText(frame, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2)
        """
        cv2.putText(
            frame,
            f"Sound: {sound_manager.get_current_sound_name()} (Press 'S' to change)",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 220, 220),
            1,
        )
        """
        cv2.imshow("Person 2 - Screen Proximity Test", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q")):
            break
        elif key in (ord("c"), ord("C")):
            if distance_detector.calibrate(frame):
                sound_manager.stop()
                too_close_start = None
                print("[CALIBRATED] Baseline eye distance saved.")
        elif key in (ord("s"), ord("S")):
            chosen = sound_manager.select_custom_sound()
            if chosen:
                print(f"[SOUND CHANGED] Now using: {chosen}")

    sound_manager.stop()
    distance_detector.close()
    cap.release()
    cv2.destroyAllWindows()
'''