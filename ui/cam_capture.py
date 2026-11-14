import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from distanceDetector import DistanceDetector
from slouchingDetector import SlouchingDetector

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
        cap = cv2.VideoCapture(0)
        distance_detector = DistanceDetector(proximity_threshold=0.80)
        posture_detector = SlouchingDetector()

        distance_start = None
        posture_start = None
        alarm_playing = False
        
        try:

            while self._running:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_original = frame

                frame = cv2.flip(frame, 1)
                display = frame.copy()
                
                if frame is None:
                    print("Could not capture a frame.")
                    break
                
                if self._calibration_requested:
                    self._calibration_requested = False
                    distance_detector.calibrate(frame)
                    posture_detector.calibrate(frame)
                
                posture = posture_detector.analyze(frame)
                distance = distance_detector.analyze(frame)
                
                now = time.monotonic()
                alarm_delay = self._settings.alarm_delay()
                
                # posture status and continuous warning timer
                if not posture["tracking"]:
                    posture_label = "Posture: not detected"
                    posture_start = None

                elif not posture["calibrated"]:
                    posture_label = "Posture: press Calibrate"
                    posture_start = None

                elif posture["changed"] is True:
                    if posture_start is None:
                        posture_start = now

                    elapsed = now - posture_start
                    remaining = max(0.0, alarm_delay - elapsed)

                    if elapsed >= alarm_delay:
                        posture_label = "Posture: change detected - ALARM"
                    else:
                        posture_label = (
                            f"Posture: change detected - alarm in {remaining:.1f}s"
                        )

                else:
                    posture_label = "Posture: within baseline"
                    posture_start = None

                # distance status and continuous warning timer
                if not distance["tracking_succeeded"]:
                    distance_label = "Distance: face not detected"
                    distance_start = None

                elif not distance["calibrated"]:
                    distance_label = "Distance: press Calibrate"
                    distance_start = None

                elif distance["too_close"]:
                    if distance_start is None:
                        distance_start = now

                    elapsed = now - distance_start
                    remaining = max(0.0, alarm_delay - elapsed)
                    percent = int(distance["relative_distance"] * 100)

                    if elapsed >= alarm_delay:
                        distance_label = (
                            f"Distance: too close ({percent}%) - ALARM"
                        )
                    else:
                        distance_label = (
                            f"Distance: too close ({percent}%)"
                            f" - alarm in {remaining:.1f}s"
                        )

                else:
                    percent = int(distance["relative_distance"] * 100)
                    distance_label = f"Distance: within baseline ({percent}%)"
                    distance_start = None

                # either detector can request the shared alarm
                posture_alarm = (
                    posture_start is not None
                    and now - posture_start >= alarm_delay
                )

                distance_alarm = (
                    distance_start is not None
                    and now - distance_start >= alarm_delay
                )

                should_play = posture_alarm or distance_alarm

                # start and stop only when the alarm state changes
                if should_play and not alarm_playing:
                    self.alarm_changed.emit(True)
                    alarm_playing = True

                elif not should_play and alarm_playing:
                    self.alarm_changed.emit(False)
                    alarm_playing = False
                    
                posture_color = (
                    (0, 180, 255)
                    if posture["changed"] is not False
                    else (0, 220, 0)
                )

                distance_color = (
                    (0, 180, 255)
                    if not distance["tracking_succeeded"]
                    or not distance["calibrated"]
                    or distance["too_close"]
                    else (0, 220, 0)
                )
                    
                if (self._settings.overlay_enabled()):
                    # draw posture landmarks on the display copy
                    for x, y in posture_detector.last_points.values():
                        cv2.circle(
                            frame,
                            (int(x), int(y)),
                            5,
                            posture_color,
                            -1,
                        )
                    
                    
                    if distance["eye_points"]:
                        p1, p2 = distance["eye_points"]
                        cv2.line(frame, p1, p2, distance_color, 2)
                        cv2.circle(frame, p1, 4, distance_color, -1)
                        cv2.circle(frame, p2, 4, distance_color, -1)
                        
                    

                    cv2.putText(frame, distance_label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, distance_color, 2)
                    cv2.putText(frame, posture_label, (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.85, posture_color, 2)
                        
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                if (w, h) != (self._width, self._height):
                    self._width, self._height = w, h
                    self.resolution_ready.emit(w, h)
                image = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
                self.frame_ready.emit(image)
                self.msleep(int(1000 / TARGET_FPS))
        finally:
            if alarm_playing:
                self.alarm_changed.emit(False)
            distance_detector.close()
            posture_detector.close()  # if SlouchingDetector has close()
            cap.release()
        
    def _on_calibration_requested(self) -> None:
        print("worker: flag set")
        self._calibration_requested = True
            
    def get_dim(self):
        print(self._width, self._height)
        return self._width, self._height
            
    def stop(self) -> None:
        self._running = False