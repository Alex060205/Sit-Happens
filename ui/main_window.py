from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from ui.aspect_box import AspectRatioBox

from ui.dashboard_canvas import DashboardCanvas
from ui.cam_panel import CamPanel
from ui.settings_panel import SettingsPanel
from app_settings import AppSettings
from alarm import Alarm

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sit Happens")
        self.resize(1920, 1080)
        
        canvas = DashboardCanvas(self)
        self.setCentralWidget(canvas)
        
        self.settings = AppSettings(self)
        
        self.cam_panel = CamPanel(canvas, self.settings)
        self.settings_panel = SettingsPanel(canvas, self.settings)
        
        def closeEvent(self, event) -> None:
            self.cam_panel.shutdown()
            super().closeEvent(event)
        
        stage = QWidget()
        stage_layout = QHBoxLayout(stage)
        stage_layout.addWidget(self.cam_panel, stretch=2.5)
        stage_layout.addWidget(self.settings_panel, stretch=1)

        box = AspectRatioBox(stage, ratio=1.5)

        canvas_layout = QHBoxLayout(canvas)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.addWidget(box)
        