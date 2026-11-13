from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import QWidget

GRID_COLOR = QColor(26, 58, 66, 60)
GRID_SPACING = 40

class DashboardCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(GRID_COLOR, 1))
        
        for x in range(0, self.width(), GRID_SPACING):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), GRID_SPACING):
            painter.drawLine(0, y, self.width(), y)
        
        return super().paintEvent(event)