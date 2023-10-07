from random import randint

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QSpinBox, QSpacerItem, QSizePolicy, QProgressBar, QScrollArea)


def createBudgetInputLine():
    # Container for budget and its progress ba
    containerLayout = QHBoxLayout()

    # Budget input line
    budgetLayout = QHBoxLayout()
    budgetLayout.addWidget(QLabel("For the next"))
    timeFrameDropDown = QComboBox()
    timeFrameDropDown.addItems(["Week", "Month", "6 Months", "Year"])
    budgetLayout.addWidget(timeFrameDropDown)

    budgetLayout.addWidget(QLabel("I want to set a budget of"))
    amountInput = QLineEdit()
    amountInput.setMaximumWidth(100)  # Restricting its width
    budgetLayout.addWidget(amountInput)

    budgetLayout.addWidget(QLabel("for the category"))
    categoryDropDown = QComboBox()
    budgetLayout.addWidget(categoryDropDown)

    budgetLayout.addWidget(QLabel("I want to stay within"))
    percentageInput = QSpinBox()
    percentageInput.setRange(0, 100)
    percentageInput.setSuffix('%')
    budgetLayout.addWidget(percentageInput)

    # Spacer to push the progress bar to the right
    spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    budgetLayout.addItem(spacer)

    # Add budget layout to container
    containerLayout.addLayout(budgetLayout)

    # Progress Bar to the right of the budget input fields
    progressbar = QProgressBar()
    progressbar.setValue(50)  # Setting it to 50 for visualization
    progressbar.setContentsMargins(0, 0, 0, 0)
    progressbar.setMaximumWidth(500)  # Restricting the width of the progress bar
    randomcolor = f"rgb({randint(0, 255)}, {randint(0, 255)}, {randint(0, 255)})"
    progressbar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {randomcolor}; }}")

    containerLayout.addWidget(progressbar)

    return containerLayout


class ConditionalStatements(QWidget):
    def __init__(self, categories=None):
        super().__init__()

        # Create a scroll area for the widget
        self.scrollArea = QScrollArea(self)

        # Allows the scroll area to resize with its content
        self.scrollArea.setWidgetResizable(True)

        # Create a new widget to place inside the scroll area
        # This widget will contain the main content
        self.scrollWidget = QWidget()

        # Set the widget to be the central content of the scroll area
        self.scrollArea.setWidget(self.scrollWidget)

        # Main layout for the content inside the scroll widget
        mainLayout = QVBoxLayout(self.scrollWidget)
        mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Budget setup layout
        self.budgetSetUpLayout = QVBoxLayout()  # This layout will contain all budget lines

        # Initial budget setup layout
        budgetLayout = createBudgetInputLine()
        self.budgetSetUpLayout.addLayout(budgetLayout)

        # Button Panel
        buttonLayout = QHBoxLayout()
        self.submitButton = QPushButton("Set Budget")
        buttonLayout.addWidget(self.submitButton)

        # Organize layouts
        mainLayout.addLayout(self.budgetSetUpLayout)
        mainLayout.addLayout(buttonLayout)

        # Use a layout for the main BudgetPanel to add the scroll area
        scrollLayout = QVBoxLayout(self)
        scrollLayout.addWidget(self.scrollArea)
        self.setLayout(scrollLayout)

        # Connect the button's click event

    def addBudgetLine(self):
        newBudgetLine = createBudgetInputLine()
        self.budgetSetUpLayout.insertLayout(0, newBudgetLine)  # Inserts at the top
        self.update()

    def adjustForScreenSize(self):
        # Get screen size
        screen = QGuiApplication.screens()[0]  # [0] gives the primary screen
        screensize = screen.size()

        if screensize.width() > 1920:  # For larger screens
            self.squishButtonsToCenter()
        else:  # For smaller screens
            self.setDefaultButtonSpacing()

    def squishButtonsToCenter(self):
        # Adjust button layout to center buttons for large screens

        # Create and add spacers to push contents to the center for each budget line layout
        for index in range(self.budgetSetUpLayout.count()):
            layout = self.budgetSetUpLayout.itemAt(index).layout()

            # Add spacers if they don't already exist
            if not isinstance(layout.itemAt(0), QSpacerItem):
                leftspacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                layout.insertItem(0, leftspacer)
            if not isinstance(layout.itemAt(layout.count() - 1), QSpacerItem):
                rightspacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                layout.addItem(rightspacer)

    def setDefaultButtonSpacing(self):
        # Reset button layout to default spacing

        # Remove the added spacers to revert to the default layout for each budget line
        for index in range(self.budgetSetUpLayout.count()):
            layout = self.budgetSetUpLayout.itemAt(index).layout()

            # Remove left spacer if it exists
            if isinstance(layout.itemAt(0), QSpacerItem):
                layout.takeAt(0).widget().deleteLater() if layout.itemAt(0).widget() else layout.takeAt(0)

            # Remove right spacer if it exists
            if isinstance(layout.itemAt(layout.count() - 1), QSpacerItem):
                layout.takeAt(layout.count() - 1).widget().deleteLater() if layout.itemAt(
                    layout.count() - 1).widget() else layout.takeAt(layout.count() - 1)


'''
FIle Structure
Root Program-Folder
    images-Foder
    MonkeyMainFolder-Python Folder
        Budget-Python Folder
            BudgetPanel.py - Creates the 2 charts and connects BudgettingGoals.py to our Budget Goals
                button and ConditionalStatements.py likewise.
            BudgettingGoals.py All the code inside BudgetPanel.py refactor to this one.
            ConditionalStatements.py
            DebtManagment.py
        Expenses-Python Folder
            ExpensePanel.py
        Income-Python Folder
            IncomePanel.py
        Settings-Python Folder
            MainMonkeyMenuFunctions.py
            ProgramSettings.py
            Shortcuts.py
    Receipts-Folder
    Themes-Folder

'''

