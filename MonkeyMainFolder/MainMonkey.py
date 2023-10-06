import sys
from PyQt6.QtWidgets import QApplication

from MonkeyMainFolder.MonkeyApplication import MyWindow
from MonkeyMainFolder.Settings import ROOT_PATH


def loadStyleSheet(filename: str):
    with open(filename, "r") as f:
        return f.read()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    tyle = loadStyleSheet(
        ROOT_PATH.parent.joinpath("Themes/IntellijThemeGrey.qss").as_posix()
    )
    # app.setStyleSheet(tyle)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
