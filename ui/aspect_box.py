from PySide6.QtWidgets import QWidget

class AspectRatioBox(QWidget):
    """Keeps a single child at a fixed width/height ratio, centered and as large as fits."""

    def __init__(self, child: QWidget, ratio: float, parent=None):
        super().__init__(parent)
        self._child = child
        self._ratio = ratio
        child.setParent(self)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        w, h = self.width(), self.height()
        if h == 0:
            return
        if w / h > self._ratio:
            cw, ch = int(h * self._ratio), h
        else:
            cw, ch = w, int(w / self._ratio)
        self._child.setGeometry((w - cw) // 2, (h - ch) // 2, cw, ch)