from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap, QBrush, QPalette
from PyQt6.QtWidgets import QMenuBar, QMenu, QSplitter, QTabWidget, QLabel, QVBoxLayout, QWidget, \
    QMessageBox
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
        '''
        
        
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
'''
        icon_label = QLabel(self)
        icon_pixmap = QPixmap("images/moke.png")
        scaled_pixmap = icon_pixmap.scaled(20, 20,
                                           Qt.AspectRatioMode.KeepAspectRatio)

        icon_label.setPixmap(scaled_pixmap)

        # Add the icon label to the title bar's layout
        self.layout().insertWidget(0, icon_label)  # This will add the icon before the menu bar
        self.layout().setContentsMargins(0, 0, 0, 0)

        # Create Menus
        fileMenu = QMenu("File", self.menu_bar)
        editMenu = QMenu("Edit", self)
        client = QMenu("Client", self)


        # File Menu Actions
        openAction = QAction("Open", self)
        newAction = QAction("New", self)
        saveAction = QAction("Save", self)
        saveAsAction = QAction("Save As", self)
        exportToPDF = QAction("PDF Export", self)
        settings = QAction("Settings", self)
        exitAction = QAction("Exit", self)
        self.menuFunctions = MainMonkeyMenuFunctions(self)

        # Set shortcuts
        openAction.setShortcut(Shortcuts.OPEN)
        newAction.setShortcut(Shortcuts.NEW)
        saveAction.setShortcut(Shortcuts.SAVE)
        saveAsAction.setShortcut(Shortcuts.SAVE_AS)
        exportToPDF.setShortcut(Shortcuts.EXPORT_TO_PDF)
        settings.setShortcut(Shortcuts.SETTINGS)

        # Set Actions
        exitAction.triggered.connect(self.menuFunctions.onExitTriggered)
        openAction.triggered.connect(self.menuFunctions.openFile)
        saveAction.triggered.connect(self.menuFunctions.saveFile)
        saveAsAction.triggered.connect(self.menuFunctions.saveFileAs)
        newAction.triggered.connect(self.menuFunctions.newFile)
        settings.triggered.connect(self.openSettings)

        # Add To Menu

        fileMenu.addAction(newAction)
        fileMenu.addSeparator()
        fileMenu.addAction(openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exportToPDF)
        fileMenu.addSeparator()
        fileMenu.addAction(settings)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)
        self.menu_bar.addMenu(fileMenu)


        # Edit menu actions
        undoEdit = QAction("Undo", self)
        redoEdit = QAction("Redo", self)
        cutEdit = QAction("Cut", self)
        copyEdit = QAction("Copy", self)
        pasteEdit = QAction("Paste", self)
        selectAllEdit = QAction("Select All", self)
        findExpense = QAction("Find/Replace", self)

        undoEdit.setShortcut(Shortcuts.UNDO)
        redoEdit.setShortcut(Shortcuts.REDO)
        cutEdit.setShortcut(Shortcuts.CUT)
        copyEdit.setShortcut(Shortcuts.COPY)
        pasteEdit.setShortcut(Shortcuts.PASTE)
        selectAllEdit.setShortcut(Shortcuts.SELECT_ALL)
        # Must create a findExpense.setShortcut.

        editMenu.addAction(undoEdit)
        editMenu.addAction(redoEdit)
        editMenu.addSeparator()
        editMenu.addAction(cutEdit)
        editMenu.addAction(copyEdit)
        editMenu.addAction(pasteEdit)
        editMenu.addSeparator()
        editMenu.addAction(selectAllEdit)
        editMenu.addSeparator()
        editMenu.addAction(findExpense)
        self.menu_bar.addMenu(editMenu)

        #What Will happen next lookin ahh
        clickMeButton = QAction('Click me', self)
        aboutMenu = QMenu('About', self)
        clickMeButton.triggered.connect(self.dialogAbout)
        aboutMenu.addAction(clickMeButton)
        self.menu_bar.addMenu(aboutMenu)

        self.layout().insertWidget(1, self.menu_bar)

        self.setWindowIcon(QIcon("images/moke.png"))
        self.setWindowTitle("TheMonkeyTracker")

    def dialogAbout(self):

        dlg = QMessageBox(self)
        dlg.setWindowTitle("About!")
        dlg.setText("Chhese")
        dlg.exec()

    # We go to fix this shit bros it doesn't work.
    def closeEvent(self, event):
        should_close = self.menuFunctions.onExitTriggered()

        if not should_close:
            event.ignore()
        else:
            event.accept()

    def openSettings(self):
        print("Opening Settings...")  # Just for debugging
        self.settings_window = ProgramSettings()
        self.settings_window.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.menu_bar.setMaximumWidth(self.width())


class MyWindow(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        self.setObjectName("MyMainWindow")

        # Ignore this
        # self.setStyleSheet("#MyMainWindow { background-color: salmon; }")
        # self.setStyleSheet("#MyMainWindow { background-color: grey; }")

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
