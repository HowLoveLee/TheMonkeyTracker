from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap, QBrush, QPalette
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu, QSplitter, QTabWidget, QLabel, QMessageBox

from MonkeyMainFolder.Expenses.ExpensePanel import ExpensePanel
from MonkeyMainFolder.Income.IncomePanel import IncomePanel
from Settings.MainMonkeyMenuFunctions import MainMonkeyMenuFunctions
from Settings.Shortcuts import Shortcuts


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MonkeyTracker")
        self.setWindowIcon(QIcon('images/icons8-monkey-96.png'))

        # Create the menu bar
        menubar = QMenuBar(self)

        # Create menus
        fileMenu = QMenu('File', self)
        editMenu = QMenu('Edit', self)
        clientServerMenu = QMenu('idkYetGang', self)

        # Add actions to the File menu
        openAction = QAction('Open', self)
        newAction = QAction('New', self)
        saveAction = QAction('Save', self)
        saveAsAction = QAction('Save As', self)

        exportToPDF = QAction('PDF Export', self)
        settings = QAction('Settings', self)
        exitAction = QAction('Exit', self)

        self.menuFunctions = MainMonkeyMenuFunctions(self)

        openAction.setShortcut(Shortcuts.OPEN)
        newAction.setShortcut(Shortcuts.NEW)
        saveAction.setShortcut(Shortcuts.SAVE)
        saveAsAction.setShortcut(Shortcuts.SAVE_AS)
        exportToPDF.setShortcut(Shortcuts.EXPORT_TO_PDF)
        settings.setShortcut(Shortcuts.SETTINGS)

        exitAction.triggered.connect(self.menuFunctions.onExitTriggered)
        openAction.triggered.connect(self.menuFunctions.openFile)
        saveAction.triggered.connect(self.menuFunctions.saveFile)
        saveAsAction.triggered.connect(self.menuFunctions.saveFileAs)
        newAction.triggered.connect(self.menuFunctions.newFile)

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

        # Edit menu actions
        undoEdit = QAction('Undo', self)
        redoEdit = QAction('Redo', self)
        cutEdit = QAction('Cut', self)
        copyEdit = QAction('Copy', self)
        pasteEdit = QAction('Paste', self)
        selectAllEdit = QAction('Select All', self)

        undoEdit.setShortcut(Shortcuts.UNDO)
        redoEdit.setShortcut(Shortcuts.REDO)
        cutEdit.setShortcut(Shortcuts.CUT)
        copyEdit.setShortcut(Shortcuts.COPY)
        pasteEdit.setShortcut(Shortcuts.PASTE)
        selectAllEdit.setShortcut(Shortcuts.SELECT_ALL)

        editMenu.addAction(undoEdit)
        editMenu.addAction(redoEdit)
        editMenu.addSeparator()
        editMenu.addAction(cutEdit)
        editMenu.addAction(copyEdit)
        editMenu.addAction(pasteEdit)
        editMenu.addSeparator()
        editMenu.addAction(selectAllEdit)

        # Add the menus to the menu bar
        menubar.addMenu(fileMenu)
        menubar.addMenu(editMenu)
        menubar.addMenu(clientServerMenu)

        # Set the menu bar for the window
        self.setMenuBar(menubar)

        # Create a QTabWidget instance
        tabWidget = QTabWidget(self)

        # Create panels for expenses and income
        self.expensePanel = ExpensePanel()
        self.incomePanel = IncomePanel()

        # Set up the QSplitter to divide the panels vertically
        splitter = CustomSplitter(Qt.Orientation.Vertical, self)
        splitter.addWidget(self.expensePanel)
        splitter.addWidget(self.incomePanel)
        splitter.setSizes([100, 1000])
        pixmap = QPixmap('C:\\Dev\\PythonProjects\\TheMonkeyTracker\\images\\Splitter.png')
        desired_width = self.width()
        scaled_pixmap = pixmap.scaled(desired_width, 360, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)

        # Use the scaled pixmap for the brush
        brush = QBrush(scaled_pixmap)
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, brush)
        splitter.setPalette(palette)

        # Add the splitter as the first tab
        tabWidget.addTab(splitter, "Expenses & Income")

        # Placeholder widget for the Budget part
        budgetPlaceholder = QLabel("Budget panel placeholder.", self)

        # Add the budget placeholder as the second tab
        tabWidget.addTab(budgetPlaceholder, "Budget")

        # Set the QTabWidget as the central widget of the main window
        self.setCentralWidget(tabWidget)

        self.setGeometry(100, 100, 990, 700)

    def closeEvent(self, event):
        # You might call your onExitTriggered and let it return True/False based on whether to proceed closing
        should_close = self.menuFunctions.onExitTriggered()

        if not should_close:
            event.ignore()
        else:
            event.accept()


class CustomSplitter(QSplitter):
    def __init__(self, orientation, parent=None):
        super(CustomSplitter, self).__init__(orientation, parent)
        self.setHandleWidth(20)  # Set the desired width here
