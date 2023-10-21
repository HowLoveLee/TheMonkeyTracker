from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("color: blue;")
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.setStyleSheet("color: purple;")
        self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.setStyleSheet("color: blue; text-decoration: underline;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("color: blue; text-decoration: none;")
        super().leaveEvent(event)
