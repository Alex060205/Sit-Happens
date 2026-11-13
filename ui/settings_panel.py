import os
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QCheckBox, QSlider, QHBoxLayout, QFileDialog
from PySide6.QtCore import Qt

from ui.base import BasePanel

class SettingsPanel(BasePanel):
    def __init__(self, parent, settings, alarm_manager):
        super().__init__(parent)
        self._settings = settings
        self._alarm_manager = alarm_manager
        
        self.title_label = QLabel("SETTINGS")
        self.title_label.setObjectName("panel_title")
         
        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.addWidget(self.title_label)

        self.overlay_button = QPushButton("Click to Enable Tracking")
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


        self.sound_label = QLabel()
        self._sync_sound_label(self._settings.sound_path())
        self._settings.sound_changed.connect(self._sync_sound_label)
        self._layout.addWidget(self.sound_label)

        # Preset Sound Buttons
        preset_layout = QHBoxLayout()
        presets = {
            "Coconut Mall": "sound-files/coconut-mall.wav",
            "Alarm": "sound-files/alarm-blare.wav",
        }
        for label_text, file_path in presets.items():
            btn = QPushButton(label_text)
            btn.clicked.connect(
                lambda checked=False, p=file_path: self._select_sound(p)
            )
            preset_layout.addWidget(btn)
        self._layout.addLayout(preset_layout)

        # Custom File Browser & Preview Buttons
        custom_layout = QHBoxLayout()
        self.browse_sound_button = QPushButton("Browse File...")
        self.browse_sound_button.clicked.connect(self._browse_sound_file)
        custom_layout.addWidget(self.browse_sound_button)

        self.preview_sound_button = QPushButton("Preview")
        self.preview_sound_button.clicked.connect(self._preview_sound)
        custom_layout.addWidget(self.preview_sound_button)
        self._layout.addLayout(custom_layout)

        
        self.setLayout(self._layout)
        self.setGeometry(1000, 0, 500, 500)
        
    def _sync_overlay_button(self, enabled: bool) -> None:
        self.overlay_button.setChecked(enabled)
        self.overlay_button.setText("Overlay: On" if enabled else "Overlay: Off")
        
    def _sync_alarm_delay(self, seconds: float) -> None:
        self.alarm_delay_slider.setValue(int(seconds))
        self.alarm_delay_label.setText(f"Alarm delay: {int(seconds)}s")

    def _sync_sound_label(self, path: str) -> None:
        filename = os.path.basename(path) if path else "None"
        self.sound_label.setText(f"Alarm sound: {filename}")

    def _select_sound(self, path: str) -> None:
        if self._alarm_manager is not None:
            if not self._alarm_manager.set_sound(path):
                print(f"[WARNING] Sound file not found: {path}")
                return
        self._settings.set_sound_path(path)

    def _browse_sound_file(self) -> None:
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Alert Sound",
            "",
            "WAV Audio Files (*.wav)",
        )
        if selected_path:
            self._select_sound(selected_path)

    def _preview_sound(self) -> None:
        if self._alarm_manager is not None:
            self._alarm_manager.preview()
        