import os
from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QSoundEffect

SOUND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound-files/alarm-blare.wav")

class Alarm(QObject):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self._effect = QSoundEffect(self)
        self._effect.setLoopCount(QSoundEffect.Loop.Infinite.value)
        self._effect.setVolume(settings.volume())
        settings.volume_changed.connect(self._effect.setVolume)
        settings.preview_requested.connect(self.preview)
        self._set_source(settings.sound_path())
        settings.sound_changed.connect(self._set_source)
        
    def set_active(self, active: bool) -> None:
        if active:
            self._effect.setLoopCount(QSoundEffect.Loop.Infinite.value)
            self._effect.play()
        else:
            self._effect.stop()
            
    def preview(self) -> None:
        self._effect.setLoopCount(1)
        self._effect.play()
        
    def _set_source(self, path: str) -> None:
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
        self._effect.setSource(QUrl.fromLocalFile(path))