import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QMenuBar, QMenu, QLabel
from qframelesswindow import FramelessWindow, StandardTitleBar


class CustomTitleBar(StandardTitleBar):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a menu bar and add it to the built-in title bar
        self.menu_bar = QMenuBar(self)

        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: transparent;
            }
            QMenuBar::item {
                        background-color: transparent;
                        padding: 6px 6px;  /* Adjusted padding for width */
                        font-size: 30px;    /* Font size */
                        color: black;         /* Text color */
                        margin: 1px 0;      /* Spacing between items */
            }
            QMenuBar::item:selected {
                background-color: rgba(173, 216, 230, 1.0);  # Light blue for selected item
            }
            QMenu {
                background-color: white;
                border: 1px solid rgba(0, 0, 0, 0.5);  # Semi-transparent black border
            }
            QMenu::item {
                background-color: white;
                padding: 5px 10px;  # Adjust as needed
                color: black;  # Text color
            }
            QMenu::item:selected {
                background-color: rgba(220, 220, 220, 1.0);  # Slightly gray for selected item
            }
            QMenu::item:active {
                background-color: rgba(200, 200, 200, 1.0);  # A bit darker gray for an active item
            }
        """)
        icon_label = QLabel(self)
        icon_pixmap = QPixmap("images/moke.png")
        scaled_pixmap = icon_pixmap.scaled(20, 20,
                                           Qt.AspectRatioMode.KeepAspectRatio)

        icon_label.setPixmap(scaled_pixmap)

        # Add the icon label to the title bar's layout
        self.layout().insertWidget(0, icon_label)  # This will add the icon before the menu bar
        self.layout().setContentsMargins(10, 0, 0, 0)
        # File menu and its actions
        file_menu = QMenu("File", self.menu_bar)
        file_menu.addAction("Open")
        file_menu.addAction("New")
        file_menu.addAction("Save")
        self.menu_bar.addMenu(file_menu)

        # Edit menu and its actions
        edit_menu = QMenu("Edit", self.menu_bar)
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addAction("Settings")
        self.menu_bar.addMenu(edit_menu)

        # View menu and its actions
        view_menu = QMenu("View", self.menu_bar)
        view_menu.addAction("Find")
        self.menu_bar.addMenu(view_menu)

        # Add the menu bar to the title bar's layout
        self.layout().insertWidget(2, self.menu_bar)

        # Optionally set an icon and title
        self.setWindowIcon(QIcon("images/moke.png"))
        self.setWindowTitle("TheMonkeyTracker")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.menu_bar.setMaximumWidth(self.width())


class MainWindow(FramelessWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # change the default title bar
        self.setTitleBar(CustomTitleBar(self))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
