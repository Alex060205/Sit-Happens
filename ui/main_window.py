from PySide6.QtWidgets import QMainWindow, QWidget

from ui.dashboard_canvas import DashboardCanvas
from ui.cam_panel import CamPanel
from ui.settings_panel import SettingsPanel
from app_settings import AppSettings

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
        
        