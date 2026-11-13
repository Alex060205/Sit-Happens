import time
import cv2
from camera import Camera
from slouching_detector_ import SlouchingDetector
from distanceDetector import DistanceDetector, play_alarm, stop_alarm


ALARM_DELAY = 5.0
WINDOW_NAME = "Sit Happens"


def main():
    camera = Camera()
    posture_detector = None
    distance_detector = None

    posture_start = None
    distance_start = None
    alarm_playing = False

    try:
        if not camera.open():
            print("Could not open the camera.")
            return

        posture_detector = SlouchingDetector()
        distance_detector = DistanceDetector(
            proximity_threshold=0.80
        )

        print("C: calibrate posture and distance")
        print("Q: quit")
        print("Click the video window to use the keyboard controls.")

        while True:
            frame = camera.read_frame()

            if frame is None:
                print("Could not capture a frame.")
                break

            frame = cv2.flip(frame, 1)
            display = frame.copy()

            # both detectors receive the same unmodified frame
            posture = posture_detector.analyze(frame)
            distance = distance_detector.analyze(frame)

            now = time.monotonic()

            # posture status and continuous warning timer
            if not posture["tracking"]:
                posture_label = "Posture: not detected"
                posture_start = None

            elif not posture["calibrated"]:
                posture_label = "Posture: press C to calibrate"
                posture_start = None

            elif posture["changed"] is True:
                if posture_start is None:
                    posture_start = now

                elapsed = now - posture_start
                remaining = max(0.0, ALARM_DELAY - elapsed)

                if elapsed >= ALARM_DELAY:
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
                distance_label = "Distance: press C to calibrate"
                distance_start = None

            elif distance["too_close"]:
                if distance_start is None:
                    distance_start = now

                elapsed = now - distance_start
                remaining = max(0.0, ALARM_DELAY - elapsed)
                percent = int(distance["relative_distance"] * 100)

                if elapsed >= ALARM_DELAY:
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
                and now - posture_start >= ALARM_DELAY
            )

            distance_alarm = (
                distance_start is not None
                and now - distance_start >= ALARM_DELAY
            )

            should_play = posture_alarm or distance_alarm

            # start and stop only when the alarm state changes
            if should_play and not alarm_playing:
                play_alarm()
                alarm_playing = True

            elif not should_play and alarm_playing:
                stop_alarm()
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

            # draw posture landmarks on the display copy
            for x, y in posture_detector.last_points.values():
                cv2.circle(
                    display,
                    (int(x), int(y)),
                    5,
                    posture_color,
                    -1,
                )

            # draw distance landmarks on the same display copy
            if distance["eye_points"] is not None:
                p1, p2 = distance["eye_points"]
                cv2.line(display, p1, p2, distance_color, 2)

            cv2.putText(
                display, posture_label, (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, posture_color, 2,
            )

            cv2.putText(
                display, distance_label, (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, distance_color, 2,
            )

            cv2.putText(
                display, "C: calibrate | Q: quit", (15, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2,
            )

            cv2.imshow(WINDOW_NAME, display)
            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), ord("Q")):
                break

            if key in (ord("c"), ord("C")):
                posture_ok = posture_detector.calibrate(frame)
                distance_ok = distance_detector.calibrate(frame)

                print(f"Posture calibration: {posture_ok}")
                print(f"Distance calibration: {distance_ok}")

                posture_start = None
                distance_start = None
                stop_alarm()
                alarm_playing = False

            if cv2.getWindowProperty(
                WINDOW_NAME, cv2.WND_PROP_VISIBLE
            ) < 1:
                break

    finally:
        stop_alarm()
        camera.close()

        if posture_detector is not None:
            posture_detector.close()

        if distance_detector is not None:
            distance_detector.close()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()