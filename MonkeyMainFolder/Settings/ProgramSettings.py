from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QLineEdit, QLabel, QStackedWidget, QPushButton,
                             QTreeWidget, QTreeWidgetItem, QFrame)


class ProgramSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 800, 600)  # Set default position and size

        # Main Layout
        layout = QVBoxLayout(self)

        # Splitter to separate the categories (left) from the settings details (right)
        self.splitter = QSplitter(self)

        # LEFT SIDE: Tree for settings categories
        self.leftPanel = QFrame(self)
        leftLayout = QVBoxLayout(self.leftPanel)

        # Search Bar at the top
        self.searchBar = QLineEdit(self)
        self.searchBar.setPlaceholderText("Search Settings...")
        leftLayout.addWidget(self.searchBar)

        # Tree setup
        self.settingsTree = QTreeWidget(self)
        self.setupSettingsTree()
        leftLayout.addWidget(self.settingsTree)

        # RIGHT SIDE: Stacked Widget for details
        self.settingsDetails = QStackedWidget(self)
        self.defaultLabel = QLabel("Select a setting from the left panel to view details.", self)
        self.settingsDetails.addWidget(self.defaultLabel)

        # Connect tree selection to stacked widget
        self.settingsTree.currentItemChanged.connect(self.changeSettingsPage)

        # Add widgets to the splitter
        self.splitter.addWidget(self.leftPanel)
        self.splitter.addWidget(self.settingsDetails)

        # Add the splitter to the main layout
        layout.addWidget(self.splitter)

        # Ok and Cancel buttons at the bottom
        btnLayout = QHBoxLayout()
        saveButton = QPushButton("Save", self)
        okButton = QPushButton("OK", self)
        cancelButton = QPushButton("Cancel", self)
        btnLayout.addStretch(1)  # Pushes buttons to the right
        btnLayout.addWidget(saveButton)
        btnLayout.addWidget(okButton)
        btnLayout.addWidget(cancelButton)

        layout.addLayout(btnLayout)

        # Connect the buttons
        okButton.clicked.connect(self.acceptSettings)
        cancelButton.clicked.connect(self.close)
        self.settingsTree.expandAll()

        # Set the main layout
        self.setLayout(layout)

    def setupSettingsTree(self):
        """Initialize the settings tree."""
        self.settingsTree.setHeaderHidden(True)  # Hide the header

        # General Settings
        generalItem = QTreeWidgetItem(["General Settings"])
        generalItem.addChild(QTreeWidgetItem(["Display"]))
        generalItem.addChild(QTreeWidgetItem(["Language"]))

        # Appearance
        appearanceItem = QTreeWidgetItem(["Appearance"])
        appearanceItem.addChild(QTreeWidgetItem(["Category Color Scheme"]))
        appearanceItem.addChild(QTreeWidgetItem(["StyleSheets & Themes"]))

        # Tables
        tablesItem = QTreeWidgetItem(["Tables"])
        tablesItem.addChild(QTreeWidgetItem(["Expenses"]))
        tablesItem.addChild(QTreeWidgetItem(["Income"]))

        # Budgeting
        budgetItem = QTreeWidgetItem(["Budgeting"])
        budgetItem.addChild(QTreeWidgetItem(["Budget Setup"]))
        budgetItem.addChild(QTreeWidgetItem(["Alerts"]))

        # Shortcuts
        shortcutsItem = QTreeWidgetItem(["Shortcuts"])
        shortcutsItem.addChild(QTreeWidgetItem(["Overview"]))

        # Integrations
        integrationsItem = QTreeWidgetItem(["Integrations"])
        integrationsItem.addChild(QTreeWidgetItem(["Financial"]))
        integrationsItem.addChild(QTreeWidgetItem(["File Management"]))

        # Add top-level items to the tree
        self.settingsTree.addTopLevelItem(generalItem)
        self.settingsTree.addTopLevelItem(appearanceItem)
        self.settingsTree.addTopLevelItem(tablesItem)
        self.settingsTree.addTopLevelItem(budgetItem)
        self.settingsTree.addTopLevelItem(shortcutsItem)
        self.settingsTree.addTopLevelItem(integrationsItem)

    def changeSettingsPage(self, current, previous):
        # Update the label on the right side to reflect the selected tree item
        label = QLabel(current.text(0), self)
        idx = self.settingsDetails.addWidget(label)
        self.settingsDetails.setCurrentIndex(idx)

    def acceptSettings(self):
        # Apply the settings changes if needed
        # For now, just close the window
        self.close()


'''
General
    Language
    Currency
List Types:
    Expenses
    Income

Preferences
    Themes
    Color Coded Categories
Accesability
    Column Visibility
Budget
    Budgeting Period
    Budgeting Method
    Budget Categories 
    Alert Thresholds
Integrations
    Link to Bank Acconts
    Receipt Folder
    Integrations with other financial tools

'''
