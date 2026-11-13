# Sit Happens

A desktop companion for coders that monitors posture changes and screen proximity using a webcam. When a warning persists, the app plays an audio reminder.

## Features

- **Posture monitoring:** detects changes in head tilt, shoulder tilt, and head position compared with a calibrated baseline.
- **Screen proximity monitoring:** estimates whether the user has moved too close to the camera.
- **Audio reminders:** plays an alarm when either warning persists for the selected delay.
- **Adjustable alarm delay:** choose between 1 and 30 seconds. The default is 5 seconds.
- **Calibration:** set posture and distance baselines using the Calibrate button.
- **Background monitoring:** continues monitoring when the window is minimized.

## Technologies

| Technology | Purpose |
| --- | --- |
| Python | Application logic |
| OpenCV | Webcam capture and image processing |
| MediaPipe | Face and body landmark detection |
| NumPy | Numerical calculations |
| PySide6 | Desktop interface and audio playback |

## Requirements

- A webcam
- Speakers or headphones
- Camera access enabled

## How to Use

1. Position the webcam so your face and both shoulders are visible.
2. Sit comfortably and face the camera.
3. Click **Calibrate** to save your posture and distance baselines.
4. Choose the alarm delay using the slider.
5. Enable the overlay if you want to see landmarks and status messages.
6. Continue working. Monitoring remains active when the window is minimized.
7. Click **Exit** or close the main window to stop the application.

The overlay button only changes what appears on the preview. Turning the overlay off does not pause detection.

Recalibrate after moving the camera or changing your desk setup.
