import cv2
from camera import Camera
from posture_detector import PostureDetector


def main():
    camera = Camera()
    detector = None

    try:
        if not camera.open():
            print("Could not open the camera.")
            print("Close other apps that are using the camera.")
            return

        detector = PostureDetector()

        print("C: calibrate posture")
        print("Q: quit")
        print("Click the video window to use the keyboard controls.")

        while True:
            frame = camera.read_frame()

            if frame is None:
                print("Could not capture a frame from the camera.")
                break

            result = detector.analyze(frame)
            display = frame.copy()

            if not result["tracking"]:
                status = "Keep your head and both shoulders in view"
                color = (0, 180, 255)

            elif not result["calibrated"]:
                status = "Sit comfortably and press C"
                color = (0, 180, 255)

            elif result["changed"]:
                status = "Posture change detected"
                color = (0, 180, 255)

            else:
                status = "Close to your baseline posture"
                color = (0, 220, 0)

            for point in detector.last_points.values():
                x, y = point

                cv2.circle(
                    display,
                    (int(x), int(y)),
                    5,
                    color,
                    -1,
                )

            cv2.putText(
                display,
                status,
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                color,
                2,
            )

            cv2.putText(
                display,
                "C: calibrate | Q: quit",
                (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
            )

            cv2.imshow("Sit Happens - Posture Test", display)

            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), ord("Q")):
                break

            if key in (ord("c"), ord("C")):
                if detector.calibrate(frame):
                    print("Posture calibrated.")
                else:
                    print(
                        "Could not calibrate. "
                        "Make sure your head and both shoulders are visible."
                    )

            if cv2.getWindowProperty(
                "Sit Happens - Posture Test",
                cv2.WND_PROP_VISIBLE,
            ) < 1:
                break

    finally:
        camera.close()

        if detector is not None:
            detector.close()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()