import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle

from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    style_path = Path(__file__).resolve().parent / "style.qss"
    app.setStyleSheet(style_path.read_text())
 
    window = MainWindow()
    window.resize(window.screen().availableGeometry().size() * 0.8)
    window.show()
    
    icon = app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
    tray = QSystemTrayIcon(icon)
    tray.setToolTip("Sit Happens")
    
    menu = QMenu()
    menu.addAction("Show").triggered.connect(window.show)
    menu.addAction("Quit").triggered.connect(app.quit)
    tray.setContextMenu(menu)
    tray.show()
    
    sys.exit(app.exec())

    
if __name__ == "__main__":
    main()