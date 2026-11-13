from PySide6.QtCore import QObject, Signal

class AppSettings(QObject):
    overlay_changed = Signal(bool)
    calibration_requested = Signal()
    alarm_delay_changed = Signal(float)
    volume_changed = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._overlay_enabled = False
        self._alarm_delay = 5.0
        self._volume = 1.0
        
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
        
    def volume(self) -> float:
        return self._alarm_delay

    def set_volume(self, volume: float) -> None:
        volume = float(volume)
        if volume == self._volume:
            return
        self._volume = volume
        self.volume_changed.emit(volume)
        
        
