import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from distanceDetector import DistanceDetector

import os
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

TARGET_FPS = 30

class CamCaptureWorker(QThread):
    frame_ready = Signal(QImage)
    error = Signal(str)
    
    resolution_ready = Signal(int, int)
    alarm_changed = Signal(bool)
    
    def __init__(self, settings):
        super().__init__()
        self._running = True
        self._width = 0
        self._height = 0
        self._settings = settings
        self._calibration_requested = False
        self._settings.calibration_requested.connect(self._on_calibration_requested)

    def run(self) -> None:
        ALARM_DELAY = 5.0

        cap = cv2.VideoCapture(0)
        distance_detector = DistanceDetector(proximity_threshold=0.80)

        too_close_start = None
        alarm_trigger = False

        while self._running:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_original = frame

            frame = cv2.flip(frame, 1)
            
            if self._calibration_requested:
                self._calibration_requested = False
                distance_detector.calibrate(frame)
            
            result = distance_detector.analyze(frame)

            if not result["tracking_succeeded"]:
                label = "Face not detected"
                color = (0, 165, 255)

            elif not result["calibrated"]:
                label = "Please calibrate"
                color = (0, 220, 255)

            elif result["too_close"]:
                if too_close_start is None:
                    too_close_start = time.time()

                elapsed = time.time() - too_close_start
                pct = int(result["relative_distance"] * 100)

                if elapsed >= ALARM_DELAY:
                    label = f"TOO CLOSE! ({pct}%) - ALARM TRIGGERED"
                    color = (0, 0, 255)  # Red
                    if not alarm_trigger:
                        print("[ALARM] User too close for too long! Playing sound...")
                        self.alarm_changed.emit(True)
                        alarm_trigger = True
                else:
                    remaining = ALARM_DELAY - elapsed
                    label = f"Too close ({pct}%) - Alarm in {remaining:.1f}s"
                    color = (0, 140, 255)  # Orange warning during countdown

            else:
                if alarm_trigger: 
                    self.alarm_changed.emit(False)
                too_close_start = None
                alarm_trigger = False
                pct = int(result["relative_distance"] * 100)
                label = f"GOOD DISTANCE ({pct}%)"
                color = (0, 220, 0)  # Green
                
            if (self._settings.overlay_enabled()):
                if result["eye_points"]:
                    p1, p2 = result["eye_points"]
                    cv2.line(frame, p1, p2, color, 2)
                    cv2.circle(frame, p1, 4, color, -1)
                    cv2.circle(frame, p2, 4, color, -1)

                cv2.putText(frame, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2)
                    
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            if (w, h) != (self._width, self._height):
                self._width, self._height = w, h
                self.resolution_ready.emit(w, h)
            image = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
            self.frame_ready.emit(image)
            self.msleep(int(1000 / TARGET_FPS))

        distance_detector.close()
        cap.release()
        
    def _on_calibration_requested(self) -> None:
        print("worker: flag set")
        self._calibration_requested = True
            
    def get_dim(self):
        print(self._width, self._height)
        return self._width, self._height
            
    def stop(self) -> None:
        self._running = False