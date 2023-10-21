from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QLineEdit, QLabel, QStackedWidget, QPushButton,
                             QTreeWidget, QTreeWidgetItem, QFrame)

from MonkeyMainFolder.Settings.CustomPanels.CustomBlockEditor import CustomBlockEditor
from MonkeyMainFolder.Settings.CustomPanels.Customlabel import ClickableLabel
from MonkeyMainFolder.Settings.CustomPanels.CustomShortCutEditor import CustomShortCutEditor


class ProgramSettings(QWidget):
    def __init__(self, broker, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.broker = broker
        self.setGeometry(100, 100, 800, 600)  # Set default position and size
        self.setMinimumSize(1,500)

        self.expensesEditor = CustomBlockEditor("C:/Dev/PythonProjects/TheMonkeyTracker/MonkeyMainFolder/Settings"
                                                "/JSONS/expensesEditor.json", self.broker)
        self.incomeEditor = CustomBlockEditor("C:/Dev/PythonProjects/TheMonkeyTracker/MonkeyMainFolder/Settings/JSONS"
                                              "/incomeEditor.json",None)
        self.budgetEditor = CustomBlockEditor("C:/Dev/PythonProjects/TheMonkeyTracker/MonkeyMainFolder/Settings/JSONS"
                                              "/budgetEditor.json")
        self.shortcutEditor = CustomShortCutEditor("C:/Dev/PythonProjects/TheMonkeyTracker/MonkeyMainFolder/Settings"
                                                   "/JSONS/shorts.json")
        # Main Layout
        layout = QVBoxLayout(self)

        # Splitter to separate the categories (left) from the settings details (right)
        self.splitter = QSplitter(self)

        # LEFT SIDE: Tree for settings categories
        self.leftPanel = QFrame(self)
        leftLayout = QVBoxLayout(self.leftPanel)
        leftLayout.setContentsMargins(0, 0, 0, 0)

        # Search Bar at the top
        self.searchBar = QLineEdit(self)
        self.searchBar.setPlaceholderText("Search Settings...")
        self.searchBar.setClearButtonEnabled(True)

        self.searchBar.textChanged.connect(self.searchSettingsTree)

        leftLayout.addWidget(self.searchBar)

        # Tree setup
        self.settingsTree = QTreeWidget(self)
        self.setupSettingsTree()
        leftLayout.addWidget(self.settingsTree)

        # RIGHT SIDE: Stacked Widget for details
        self.settingsDetails = QStackedWidget(self)

        # I do not know what I want to show when settings are opened on start.
        self.test = QLabel("Click any of the Settings headers.")
        self.settingsDetails.addWidget(self.test)

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
        # self.settingsTree.expandAll()

        # Set the main layout
        self.setLayout(layout)
        self.splitter.widget(0).setMinimumWidth(200)
        self.splitter.setSizes([100, 600])
        self.splitter.setCollapsible(0, False)

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

        # Categories
        categoriesItem = QTreeWidgetItem(["Categories"])
        categoriesItem.addChild(QTreeWidgetItem(["Expenses Editor"]))
        categoriesItem.addChild(QTreeWidgetItem(["Income Editor"]))
        categoriesItem.addChild(QTreeWidgetItem(["Budget Editor"]))
        # Budgeting
        budgetItem = QTreeWidgetItem(["Budgeting"])
        budgetItem.addChild(QTreeWidgetItem(["Budget Setup"]))
        budgetItem.addChild(QTreeWidgetItem(["Alerts"]))

        # Shortcuts
        shortcutsItem = QTreeWidgetItem(["Shortcuts"])
        shortcutsItem.addChild(QTreeWidgetItem(["Overview"]))
        shortcutsItem.addChild(QTreeWidgetItem(["Editor"]))
        # Integrations
        integrationsItem = QTreeWidgetItem(["Integrations"])
        integrationsItem.addChild(QTreeWidgetItem(["Financial"]))
        integrationsItem.addChild(QTreeWidgetItem(["File Management"]))

        # Add top-level items to the tree
        self.settingsTree.addTopLevelItem(generalItem)
        self.settingsTree.addTopLevelItem(appearanceItem)
        self.settingsTree.addTopLevelItem(categoriesItem)
        self.settingsTree.addTopLevelItem(budgetItem)
        self.settingsTree.addTopLevelItem(shortcutsItem)
        self.settingsTree.addTopLevelItem(integrationsItem)

    def handleLabelClick(self, subcategory_name):
        matching_items = self.settingsTree.findItems(subcategory_name,
                                                     Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchRecursive)
        if matching_items:
            self.settingsTree.setCurrentItem(matching_items[0])
            self.changeSettingsPage(matching_items[0],
                                    None)  # Call this to switch to the panel related to the clicked subcategory

    def changeSettingsPage(self, current, previous):
        currentText = current.text(0)
        container = QWidget(self)
        layout = QVBoxLayout(container)

        # Reduce the spacing between each element
        layout.setSpacing(5)
        runLabels = True

        # Create Title and Description Labels
        titleLabel = QLabel(currentText, self)
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titleLabel.setStyleSheet("font: bold 18px")

        # Map categories to their descriptions
        descriptions = {
            "General Settings": " RatChange your basic application settings.",
            "Appearance": "Customize the look and feel of the application.",
            "Tables": "Manage how tables are displayed and interacted with.",
            "Budgeting": "Control your budget and alert settings.",
            "Shortcuts": "Customize your shortcuts and their behaviors.",
            "Integrations": "Integrate with financial services and manage your files.",
        }

        descriptionLabel = QLabel(
            descriptions.get(currentText, f"This is a description for {currentText} settings."),
            self)
        # Add them to layout
        layout.addWidget(titleLabel)
        layout.addWidget(descriptionLabel)
        # Set the description label based on the category

        if currentText == "General Settings":
            labels = [
                ClickableLabel("Display", self),
                ClickableLabel("Language", self),
                ClickableLabel("About", self)
            ]
        elif currentText == "Appearance":
            labels = [
                ClickableLabel("Category Color Scheme", self),
                ClickableLabel("StyleSheets & Themes", self)
            ]
        elif currentText == "Categories":
            labels = [
                ClickableLabel("Expenses Editor", self),
                ClickableLabel("Income Editor", self),
                ClickableLabel("Budget Editor", self)

            ]
        elif currentText == "Expenses Editor":
            layout.addWidget(titleLabel)
            layout.addWidget(self.expensesEditor)
            layout.setStretchFactor(self.expensesEditor, 1)
            runLabels = False
        elif currentText == "Income Editor":
            layout.addWidget(titleLabel)
            layout.addWidget(self.incomeEditor)
            layout.setStretchFactor(self.incomeEditor, 1)
            runLabels = False
        elif currentText == "Budget Editor":
            layout.addWidget(titleLabel)
            layout.addWidget(self.budgetEditor)
            layout.setStretchFactor(self.budgetEditor, 1)
            runLabels = False
        elif currentText == "Budgeting":
            labels = [
                ClickableLabel("Budget Setup", self),
                ClickableLabel("Alerts", self)
            ]
        elif currentText == "Shortcuts":
            labels = [
                ClickableLabel("Overview", self),
                ClickableLabel("Editor", self)
            ]
            
        elif currentText == "Editor":
            layout.addWidget(titleLabel)
            layout.addWidget(self.shortcutEditor)
            layout.setStretchFactor(self.shortcutEditor, 1)
            runLabels = False

        elif currentText == "Integrations":
            labels = [
                ClickableLabel("Financial Services", self),
                ClickableLabel("File Management", self),
            ]
        else:
            if currentText != "Expenses Editor":
                labels = [QLabel("Select a setting from the left panel to view details.", self)]
            else:
                labels = [QLabel("edit", self)]

        if runLabels:
            def make_lambda(label_text):
                return lambda *args: self.handleLabelClick(label_text)

            for label in labels:
                print(type(label))
                existing_style = label.styleSheet()
                label.setStyleSheet(f"{existing_style}; padding-left: 20px;")
                layout.addWidget(label)
                if isinstance(label, ClickableLabel):
                    label.clicked.connect(make_lambda(label.text()))

        layout.addStretch(1)
        idx = self.settingsDetails.addWidget(container)
        self.settingsDetails.setCurrentIndex(idx)

    def acceptSettings(self):
        # Apply the settings changes if needed
        # For now, just close the window
        self.close()

    def searchSettingsTree(self):
        query = self.searchBar.text().strip().lower()  # Case-insensitive search
        all_items = self.settingsTree.findItems('*', Qt.MatchFlag.MatchWildcard | Qt.MatchFlag.MatchRecursive)

        closest_item = None
        closest_distance = float('inf')  # Initialize with a large value

        for item in all_items:
            item_text = item.text(0).lower()

            # Calculate the 'distance' between the query and the item text
            distance = len(item_text) - len(query)

            # If the query is in the item text and the distance is less than the closest found so far
            if query in item_text and distance < closest_distance:
                closest_item = item
                closest_distance = distance

        # Automatically select the closest matching item
        if closest_item:
            self.settingsTree.setCurrentItem(closest_item)


'''
If i say between (Finished) add a  green checkmark emoji in front of the name of the action.
Menubar
    -File
        -New (Finished)
        -Load(Finished)
        -Save(Finished)
            !Add a small panel that is green and say Saved!
        -Save As(Finished)
            !Add a small panel that is green and say Saved! To path:
        -Settings
        -Export To PDF  !Exported to:
        -Exit
            #Exit, Windows Exit button, New, Load, any form of exit will have a dialog to prevent accidental loss of 
            current sheet.
    -Edit(This is a big task I cannot be certain when I will implement it)
        -Undo
        -Redo
        -Copy
        -Paste
        -Cut
        -Select All
        -Delete
        -Find
    -Server
        -Download Sheet
        -Upload Sheet

Table Panel
    -Columns
        -Type of Expense
        -Name of Expense
        -Summary
        -Date Due
        -Audit date
        -Proof of Receipt
        -Total Amount
        -Commit Action
        
        !Might add, I'd like a 'From' column that you can select what was the payment method, this way we can add a way 
            to increase debt amount that way the user can input a starting amount and just keep adding expenses and the
            total can we added to its debt department.
    
    -Features:
        -Add Row
        -Delete Row
        -Commit All rows
        -Total Pre
        -Total Committed
    
    Filters:
        - Date Filter
            -Dropdown with 2 date selectors(From & To)
        - Expense Category Filter
            -Dropdown with Tick Buttons next to categories.
        - Reset Filter
            -Label to remove all filters and show the complete table.
    
    -Settings: Will add, reformat tables to use our new category edtors, 
        #Function: Create a Tree add and delete, push and back create building blocks style of editor.
                    Tables filters will use the categories by reading them from a file they were written to, that way
                    we can live edit them and immediately use them.
                    
        -Tables
            -Category Editor (Add, Delete, Edit categories)
                -Expenses
                -Income
                -Budget
        -Shortcuts
            -Overview
                -Non editable field with list of shortcuts.
            -Edit
                -List of shortcuts, Label of shortcut next to a button when clicked listen for any keyboard input edit.
                Save, Cancel Buttons.
                -Write to file, edit our code so it reads from files.
    
    -Integrations
        -File Management:
            -Choosing where the files are stored.

Credit Payments
Zelle
Xoom
Rent
Utilities
Fuel
Auto Insurance
Maintenance & repairs
Groceries
Dinning Out
Coffe Shops
Movie Theaters
Video Games
Streaming Services.

                
                
                
'''
