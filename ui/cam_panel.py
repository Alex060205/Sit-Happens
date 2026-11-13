from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from ui.base import BasePanel
from ui.cam_capture import CamCaptureWorker
from alarmManager import AlarmManager

class CamPanel(BasePanel):
    def __init__(self, parent, settings, alarm_manager):
        super().__init__(parent)
        self._settings = settings
        self._alarm_manager = alarm_manager
        
        self._worker = None
        #self._alarm = Alarm(self)

        self.title_label = QLabel("CAMERA")
        self.image_label = QLabel()
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        
    def showEvent(self, event) -> None:
            super().showEvent(event)
            if self._worker is None:
                self._worker = CamCaptureWorker(self._settings)
                self._worker.frame_ready.connect(self._on_frame)
                self._worker.error.connect(self._on_error)
                self._worker.resolution_ready.connect(self._on_resolution)
                self._worker.alarm_changed.connect(self._alarm.set_active)
                self._worker.start()
                
    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        if self._worker is not None:
            self._worker.stop()
            self._worker.wait()
            self._worker = None
            
    def _on_frame(self, image) -> None:
        pixmap = QPixmap.fromImage(image).scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(pixmap)
        
    DISPLAY_SCALE = 1.25

    def _on_resolution(self, width: int, height: int) -> None:
        self.image_label.setFixedSize(int(width * self.DISPLAY_SCALE), int(height * self.DISPLAY_SCALE))
        self.setFixedSize(self.sizeHint())

    def _on_error(self, message: str) -> None:
        self.title_label.setText(f"ERROR: {message}")
