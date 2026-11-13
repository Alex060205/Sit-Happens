from PySide6.QtWidgets import QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from ui.base import BasePanel
from ui.cam_capture import CamCaptureWorker
from alarm import Alarm

class CamPanel(BasePanel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self._settings = settings
        
        self._worker = None
        self._alarm = Alarm(self)

        self.title_label = QLabel("CAMERA")
        self.image_label = QLabel()
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.title_label)
        layout.addWidget(self.image_label, stretch=1)
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
                
    def shutdown(self) -> None:
        # stop detection only when the application closes
        if self._worker is not None:
            self._worker.alarm_changed.disconnect(
                self._alarm.set_active
            )
            self._worker.stop()
            self._worker.wait()
            self._worker.deleteLater()
            self._worker = None

        self._alarm.set_active(False)
            
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
