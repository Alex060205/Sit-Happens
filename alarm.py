import os
from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QSoundEffect

SOUND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound-files/alarm-blare.wav")

class Alarm(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._effect = QSoundEffect(self)
        self._effect.setSource(QUrl.fromLocalFile(SOUND_PATH))
        self._effect.setLoopCount(QSoundEffect.Loop.Infinite.value)
        
    def set_active(self, active: bool) -> None:
        if active:
            self._effect.play()
        else:
            self._effect.stop()