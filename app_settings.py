from PySide6.QtCore import QObject, Signal

class AppSettings(QObject):
    overlay_changed = Signal(bool)
    calibration_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._overlay_enabled = False
        
    def overlay_enabled(self) -> bool:
        return self._overlay_enabled
    
    def set_overlay_enabled(self, enabled: bool) -> None:
        if enabled == self._overlay_enabled:
            return
        self._overlay_enabled = enabled
        self.overlay_changed.emit(enabled)
        
    def request_calibration(self) -> None:
        print("settings: calibration requested")
        self.calibration_requested.emit()
        
        
