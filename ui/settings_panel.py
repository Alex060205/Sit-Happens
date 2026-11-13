from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QCheckBox, QSlider
from PySide6.QtCore import Qt

from ui.base import BasePanel

class SettingsPanel(BasePanel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self._settings = settings
        
        self.title_label = QLabel("SETTINGS")
        self.title_label.setObjectName("panel_title")
         
        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.addWidget(self.title_label)

        self.overlay_button = QPushButton("Click to enable tracking")
        self.overlay_button.setCheckable(True)
        self.overlay_button.setChecked(self._settings.overlay_enabled())
        self.overlay_button.toggled.connect(self._settings.set_overlay_enabled)
        self._settings.overlay_changed.connect(self._sync_overlay_button)
        self._layout.addWidget(self.overlay_button)
        
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(lambda: self.window().close())
        self._layout.addWidget(self.exit_button)
        
        self.calibrate_button = QPushButton("Calibrate")
        self.calibrate_button.clicked.connect(self._settings.request_calibration)
        self._layout.addWidget(self.calibrate_button)
        
        self.alarm_delay_label = QLabel()
        self.alarm_delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.alarm_delay_slider.setRange(1, 30)  # seconds
        self._sync_alarm_delay(self._settings.alarm_delay())
        self.alarm_delay_slider.valueChanged.connect(self._settings.set_alarm_delay)
        self._settings.alarm_delay_changed.connect(self._sync_alarm_delay)
        self._layout.addWidget(self.alarm_delay_label)
        self._layout.addWidget(self.alarm_delay_slider)
        
        self.setLayout(self._layout)
        
    def _sync_overlay_button(self, enabled: bool) -> None:
        self.overlay_button.setChecked(enabled)
        self.overlay_button.setText("Overlay: On" if enabled else "Overlay: Off")
        
    def _sync_alarm_delay(self, seconds: float) -> None:
        self.alarm_delay_slider.setValue(int(seconds))
        self.alarm_delay_label.setText(f"Alarm delay: {int(seconds)}s")
        
        