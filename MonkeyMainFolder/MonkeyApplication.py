from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap, QBrush, QPalette
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu, QSplitter, QTabWidget, QLabel, QVBoxLayout, QWidget
from qframelesswindow import FramelessWindow, StandardTitleBar, AcrylicWindow
from MonkeyMainFolder.Budget.ConditionalStatements import ConditionalStatements
from MonkeyMainFolder.Expenses.ExpensePanel import ExpensePanel
from MonkeyMainFolder.Income.IncomePanel import IncomePanel
from Settings.MainMonkeyMenuFunctions import MainMonkeyMenuFunctions
from Settings.Shortcuts import Shortcuts
from Settings.ProgramSettings import ProgramSettings
from Budget.BudgetPanel import BudgetPanel


class CustomTitleBar(StandardTitleBar):

    def __init__(self, parent=None):
        super().__init__(parent)

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
        self.layout().setContentsMargins(0, 0, 0, 0)

        file_menu = QMenu("File", self.menu_bar)
        file_menu.addAction("Open")
        file_menu.addAction("New")
        file_menu.addAction("Save")
        self.menu_bar.addMenu(file_menu)

        edit_menu = QMenu("Edit", self.menu_bar)
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addAction("Settings")
        self.menu_bar.addMenu(edit_menu)

        view_menu = QMenu("View", self.menu_bar)
        view_menu.addAction("Find")
        self.menu_bar.addMenu(view_menu)

        self.layout().insertWidget(1, self.menu_bar)
        self.setWindowIcon(QIcon("images/moke.png"))
        self.setWindowTitle("TheMonkeyTracker")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.menu_bar.setMaximumWidth(self.width())


class MyWindow(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        self.setObjectName("MyMainWindow")

        # self.setStyleSheet("#MyMainWindow { background-color: red; }")

        mainLayout = QVBoxLayout()  # Create a QVBoxLayout
        mainLayout.setContentsMargins(0, 32, 0, 0)  # Top margin set to 32 pixels

        tabWidget = QTabWidget(self)
        mainLayout.addWidget(tabWidget)  # Add the QTabWidget to the layout
        centralWidget = QWidget()  # Create a central widget
        centralWidget.setLayout(mainLayout)  # Set the layout to the central widget

        self.expensePanel = ExpensePanel()
        self.incomePanel = IncomePanel()
        splitter = CustomSplitter(Qt.Orientation.Vertical, self)
        splitter.addWidget(self.expensePanel)
        splitter.addWidget(self.incomePanel)
        splitter.setSizes([100, -100])
        pixmap = QPixmap("C:\\Dev\\PythonProjects\\TheMonkeyTracker\\images\\Splitter.png")
        desired_width = self.width()
        scaled_pixmap = pixmap.scaled(desired_width, 360, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        brush = QBrush(scaled_pixmap)
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, brush)
        splitter.setPalette(palette)
        tabWidget.addTab(splitter, "Expenses & Income")
        self.budget = BudgetPanel()
        self.Conditional = ConditionalStatements()
        tabWidget.addTab(self.budget, "Budget")

        layout = QVBoxLayout(self)
        layout.addWidget(centralWidget)  # Add centralWidget to the FramelessWindow layout

        self.setGeometry(100, 100, 990, 700)
        self.titleBar.raise_()

    def moveEvent(self, event):
        super().moveEvent(event)
        current_screen = self.screen()
        screen_resolution = current_screen.size()
        if hasattr(self, 'Conditional'):  # Check if 'Conditional' attribute exists
            if screen_resolution.width() > 1920:
                self.Conditional.squishButtonsToCenter()
            else:
                self.Conditional.setDefaultButtonSpacing()


class CustomSplitter(QSplitter):
    def __init__(self, orientation, parent=None):
        super(CustomSplitter, self).__init__(orientation, parent)
        self.setHandleWidth(20)  # Set the desired width here
