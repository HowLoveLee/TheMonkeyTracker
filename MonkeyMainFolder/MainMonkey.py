import sys
from PyQt6.QtWidgets import QApplication

from MonkeyMainFolder.MonkeyApplication import MyWindow

def loadStyleSheet(filename):
    with open(filename, "r") as f:
        return f.read()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    tyle = loadStyleSheet("C:\Dev\PythonProjects\TheMonkeyTracker\Themes\IntellijThemeGrey.qss")
    #app.setStyleSheet(tyle)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
