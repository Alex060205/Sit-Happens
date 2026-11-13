from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QCheckBox
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

        self.overlay_button = QPushButton()
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
        
        self.setLayout(self._layout)
        
        self.setGeometry(1000, 0, 500, 500)
        
    def _sync_overlay_button(self, enabled: bool) -> None:
        self.overlay_button.setChecked(enabled)
        self.overlay_button.setText("Overlay: On" if enabled else "Overlay: Off")
        
        