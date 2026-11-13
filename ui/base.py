from PySide6.QtCore import Qt, Signal, Slot, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtWidgets import QWidget, QLabel, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor, QPainter, QPen

MIN_PANEL_WIDTH = 100
MIN_PANEL_HEIGHT = 80
RESIZE_HANDLE_SIZE = 16

ANIMATION_DURATION_MS = 300

class BasePanel(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("dashboard_panel")
        
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#00e5ff"), 2))
        
        w, h = self.width(), self.height()
        bracket_len = 16
        margin = 2
        
        painter.drawLine(margin, margin, margin + bracket_len, margin)
        painter.drawLine(margin, margin, margin, margin + bracket_len)
        painter.drawLine(w - margin, margin, w - margin - bracket_len, margin)
        painter.drawLine(w - margin, margin, w - margin, margin + bracket_len)
        painter.drawLine(margin, h - margin, margin + bracket_len, h - margin)
        painter.drawLine(margin, h - margin, margin, h - margin - bracket_len)
        painter.drawLine(w - margin, h - margin, w - margin - bracket_len, h - margin)
        painter.drawLine(w - margin, h - margin, w - margin, h - margin - bracket_len)