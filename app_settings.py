from PySide6.QtCore import QObject, Signal

class AppSettings(QObject):
    overlay_changed = Signal(bool)
    calibration_requested = Signal()
    alarm_delay_changed = Signal(float)
    sound_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._overlay_enabled = False
        self._alarm_delay = 5.0
        self._sound_path = "sound-files/alarm-blare"
    
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
        
    def alarm_delay(self) -> float:
        return self._alarm_delay

    def set_alarm_delay(self, seconds: float) -> None:
        if seconds == self._alarm_delay:
            return
        self._alarm_delay = seconds
        self.alarm_delay_changed.emit(seconds)

    def sound_path(self) -> str:
        return self._sound_path

    def set_sound_path(self, path: str) -> None:
        if not path or path == self._sound_path:
            return
        self._sound_path = path
        self.sound_changed.emit(path)
