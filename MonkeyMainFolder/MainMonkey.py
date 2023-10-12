import sys
from PyQt6.QtWidgets import QApplication

from MonkeyMainFolder.MonkeyApplication import MyWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())