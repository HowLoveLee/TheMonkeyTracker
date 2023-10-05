# Make letters black whe highlighting a field, they look white and contrast wrong.
import json
import os
import random
import shutil
import sys

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction, QStandardItemModel, QStandardItem, QDoubleValidator, QPalette, QColor, QIcon
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QMenu, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QHBoxLayout, QWidget, QSplitter, QPushButton, QSizePolicy, QComboBox,
                             QDateEdit, QItemDelegate, QHeaderView, QStyledItemDelegate, QLineEdit, QLabel, QFileDialog)

from Stats import launch_view, viewStats


class MoneyItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.validator = QDoubleValidator(0, 9999999999, 2, self)

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(self.validator)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        if value:
            editor.setText(str(value))

    def setModelData(self, editor, model, index):
        value = editor.text().replace('$', '').strip()
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        painter.save()
        rect = option.rect
        painter.drawText(rect.left() + 5, rect.top(), rect.width(), rect.height(),
                         Qt.AlignmentFlag.AlignVCenter, "$")
        painter.restore()


class CustomTableWidget(QTableWidget):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)
        self.non_editable_rows = set()

    def flags(self, index):
        if index.row() in self.non_editable_rows:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def disableRowEditing(self, row):
        self.non_editable_rows.add(row)


class DateDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDisplayFormat("dd/MM/yyyy")

        editor.setDate(QDate.currentDate())
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setDate(QDate.fromString(value, "dd/MM/yyyy"))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.date().toString("dd/MM/yyyy"), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('images/icons8-monkey-96.png'))
        # Create the menu bar
        menubar = QMenuBar(self)

        # Create menus
        fileMenu = QMenu('File', self)
        editMenu = QMenu('Edit', self)
        clientServerMenu = QMenu('ClientServer', self)

        # Add actions to the File menu
        openAction = QAction('Open', self)
        saveAction = QAction('Save', self)
        saveAsAction = QAction('Save As', self)
        exportToExcel = QAction('Excel Export', self)
        exportToPDF = QAction('PDF Export', self)
        settings = QAction('Settings', self)
        exitAction = QAction('Exit', self)
        exitAction.triggered.connect(self.close)  # Connect the exit action to the window's close method

        fileMenu.addAction(openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exportToExcel)
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
        preferencesEdit = QAction('Preferences', self)

        editMenu.addAction(undoEdit)
        editMenu.addAction(redoEdit)
        editMenu.addSeparator()
        editMenu.addAction(cutEdit)
        editMenu.addAction(copyEdit)
        editMenu.addAction(pasteEdit)
        editMenu.addSeparator()
        editMenu.addAction(selectAllEdit)
        editMenu.addSeparator()
        editMenu.addAction(preferencesEdit)

        # Add the menus to the menu bar
        menubar.addMenu(fileMenu)
        menubar.addMenu(editMenu)
        menubar.addMenu(clientServerMenu)

        # Set the menu bar for the window
        self.setMenuBar(menubar)

        # Create panels for expenses and income
        self.expensePanel, self.expenseTable = self.createPanelWithTable(isExpense=True)
        self.incomePanel, self.incomeTable = self.createPanelWithTable(isExpense=False)

        # Set DateDelegate for Expense and Income tables
        expense_date_delegate = DateDelegate()
        self.expenseTable.setItemDelegateForColumn(3, expense_date_delegate)
        self.expenseTable.setItemDelegateForColumn(4, expense_date_delegate)

        income_date_delegate = DateDelegate()
        self.incomeTable.setItemDelegateForColumn(1, income_date_delegate)

        # Set up the QSplitter to divide the main window horizontally
        splitter = QSplitter(Qt.Orientation.Vertical, self)
        splitter.addWidget(self.expensePanel)
        splitter.addWidget(self.incomePanel)

        initial_sizes = [100, -100]  # for demonstration purposes
        splitter.setSizes(initial_sizes)
        # Set the QSplitter as the central widget of the main window
        self.setCentralWidget(splitter)

        self.setWindowTitle("Monkey Tracker")
        self.setGeometry(100, 100, 990, 700)

    def updateTotalLabels(self):
        total, committed_total = self.computeTotals()
        self.totalExpensesLabel.setText(f"Total: ${total:.2f}")
        self.committedTotalExpensesLabel.setText(f"Committed Total: ${committed_total:.2f}")

    def createPanelWithTable(self, isExpense=True):

        panel = QWidget()
        layout = QVBoxLayout()

        table = CustomTableWidget(1, 8 if isExpense else 3)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        blue = QColor(240, 255, 255)
        palette = table.palette()
        palette.setColor(QPalette.ColorRole.Highlight, blue)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))  # Setting text color to black
        table.setPalette(palette)

        if isExpense:
            table.setHorizontalHeaderLabels(
                ['Type', 'Name', 'Summary', 'Due Date', 'Audit Date', 'Receipt', 'Total', 'Commit'])

            delegate = MoneyItemDelegate(table)
            table.setItemDelegateForColumn(6, delegate)

            # Set column widths for the Expense table
            table.setColumnWidth(3, 120)
            table.setColumnWidth(4, 120)
            table.setColumnWidth(5, 100)  # Receipt column
            table.setColumnWidth(6, 100)  # Total column
            table.setColumnWidth(7, 100)  # Commit column

            # Set other columns to stretch
            for index in [0, 1, 2]:
                table.horizontalHeader().setSectionResizeMode(index, QHeaderView.ResizeMode.Stretch)

        else:
            table.setHorizontalHeaderLabels(['Entity', 'Received Date', 'Amount'])

            # Set column width for the Income table
            table.setColumnWidth(2, 100)  # Amount column
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)

            # Set other columns to stretch
            for index in [0, 1]:
                table.horizontalHeader().setSectionResizeMode(index, QHeaderView.ResizeMode.Stretch)

        for i in range(3):  # Assuming 3 rows for the sake of demonstration
            for j in range(8 if isExpense else 3):
                if isExpense:
                    if j == 0:  # If it's the 'Type' column
                        table.setCellWidget(i, j, self.createTypeDropdown())

                    elif j == 5:
                        receiptButton = QPushButton("No")
                        receiptButton.clicked.connect(lambda _, b=receiptButton: self.receiptButtonClicked(b))
                        table.setCellWidget(i, j, receiptButton)
                    #  receiptButton.setStyleSheet("background-color: lightyellow;")

                    elif j == 6:  # If it's the 'Total' column
                        item = QTableWidgetItem()
                        item.setText("0.00")  # default value
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                        table.setItem(i, j, item)

                    elif j == 7:  # If it's the 'Commit' column
                        commitButton = QPushButton("Commit")
                        commitButton.clicked.connect(lambda _, b=commitButton: self.commitButtonClicked(b))
                        # commitButton.setStyleSheet("background-color: lightyellow;")

                        table.setCellWidget(i, j, commitButton)
                    else:
                        table.setItem(i, j, QTableWidgetItem(" "))
                else:
                    table.setItem(i, j, QTableWidgetItem(" "))

        layout.addWidget(table, 1)

        if isExpense:
            buttonPanel = QWidget()
            buttonLayout = QHBoxLayout()

            addButton = QPushButton("Add Expense")
            deleteButton = QPushButton("Delete Expense")
            statisticsButton = QPushButton("Run Statistics")
            commitAllButton = QPushButton("Commit All Expenses")

            addButton.clicked.connect(self.addExpenseRow)
            deleteButton.clicked.connect(self.deleteExpenseRow)

            statisticsButton.clicked.connect(self.StatButtonClicked)

            table.setSortingEnabled(True)
            table.horizontalHeader().sectionDoubleClicked.connect(self.headerDoubleClicked)

            buttonLayout.addWidget(addButton)
            buttonLayout.addWidget(deleteButton)
            buttonLayout.addWidget(commitAllButton)
            buttonLayout.addWidget(statisticsButton)

            # Add total labels
            self.totalExpensesLabel = QLabel("Total: $0.00")
            self.committedTotalExpensesLabel = QLabel("Committed Total: $0.00")

            buttonLayout.addWidget(self.totalExpensesLabel)
            buttonLayout.addWidget(self.committedTotalExpensesLabel)

            table.model().dataChanged.connect(self.updateTotalLabels)

            buttonPanel.setLayout(buttonLayout)
            layout.addWidget(buttonPanel)

        panel.setLayout(layout)
        return panel, table  # Returning the table as well for further reference

    def computeTotals(self):
        total = 0.0
        committed_total = 0.0
        for row in range(self.expenseTable.rowCount()):
            commitButton = self.expenseTable.cellWidget(row, 7)

            # Check if the commitButton exists
            if not commitButton:
                print(f"Missing commitButton in row {row}. Skipping this row.")
                continue

            # Check if the button is enabled
            if not commitButton.isEnabled():
                committed_value = self.expenseTable.item(row, 6).text().replace('$', '')
                committed_total += float(committed_value)

            value = self.expenseTable.item(row, 6).text().replace('$', '')
            total += float(value)

        return total, committed_total

    def deleteExpenseRow(self):
        selectedRows = self.expenseTable.selectionModel().selectedRows()
        for index in selectedRows:
            self.expenseTable.removeRow(index.row())
        # Update totals after deletion
        self.updateTotalLabels()

    def receiptButtonClicked(self, button):
        if hasattr(button, "receipt_path"):  # Check if the button has a stored path
            os.startfile(button.receipt_path)  # Open the receipt using the default viewer
            return

        options = QFileDialog.Option.ReadOnly
        filePath, _ = QFileDialog.getOpenFileName(self, "Select Receipt", "",
                                                  "Image Files (*.png *.jpeg *.jpg);;PDF Files (*.pdf);;All Files (*)",
                                                  options=options)

        if filePath:  # If a file was selected
            destinationFolder = "Receipts"
            destinationPath = os.path.join(destinationFolder, os.path.basename(filePath))
            shutil.copy2(filePath, destinationPath)

            # Change the button's appearance and store the receipt's path in the button
            button.setText("Yes")
            button.setStyleSheet("background-color: green")
            button.receipt_path = destinationPath  # Store the path as an attribute of the button

    def commitButtonClicked(self, button):
        row = self.expenseTable.indexAt(button.pos()).row()
        name_item = self.expenseTable.item(row, 1)  # Assuming the 2nd column is the name

        if not name_item or not name_item.text().strip():
            # highlight the name cell with a red background if the name is empty
            self.expenseTable.setCurrentCell(row, 1)
            return

        # If name is provided, proceed with committing
        for col in range(self.expenseTable.columnCount()):
            # Skip over the Receipt column
            if col == 5:  # Assuming that column index 5 is for Receipts
                continue

            item = self.expenseTable.item(row, col)
            if item:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            widget = self.expenseTable.cellWidget(row, col)
            if widget:
                widget.setEnabled(False)

        button.setEnabled(False)
        button.setStyleSheet("background-color: green;")

        # Update totals after committing
        self.updateTotalLabels()

    def createTypeDropdown(self):

        comboBox = QComboBox()
        model = QStandardItemModel()

        categories = {
            "Banking": ["Credit Payments", "Zelle", "Xoom"],
            "House": ["Rent", "Utilities"],
            "Transportation": ["Fuel", "Auto Insurance", "Maintenance/Repairs"],
            "Food": ["Groceries", "Dining Out", "Coffee Shops"],
            "Entertainment": ["Movie Theaters", "Video Games", "Streaming Services"],
            "Mobile Service": [],
            "Clothing": [],
            "Education": ["Tuition Fees"],
            "Investments & Savings": ["Stocks", "Savings Accounts", "Business Transactions"],
            "Travel": ["Flights", "Hotels"],
            "Miscellaneous": ["Gifts/Donations", "Home Decor"],
            "Pets": []
        }

        for category, subcategories in categories.items():
            category_item = QStandardItem(category)
            category_item.setSelectable(False)  # make the main category non-selectable
            category_item.setEnabled(False)  # make the item appear slightly grayed out
            model.appendRow(category_item)

            for subcategory in subcategories:
                subcategory_item = QStandardItem(f"  {subcategory}")
                model.appendRow(subcategory_item)
        comboBox.setMaxVisibleItems(30)
        comboBox.setModel(model)
        return comboBox

    def addExpenseRow(self):
        rowPosition = self.expenseTable.rowCount()
        self.expenseTable.insertRow(rowPosition)

        # Set default items/widgets for the new row
        self.expenseTable.setCellWidget(rowPosition, 0, self.createTypeDropdown())

        for col in [1, 2, 3, 4, 5]:
            self.expenseTable.setItem(rowPosition, col, QTableWidgetItem(" "))

        commitButton = QPushButton("Commit")
        commitButton.clicked.connect(lambda _, b=commitButton: self.commitButtonClicked(b))
        # commitButton.setStyleSheet("background-color: lightyellow;")

        self.expenseTable.setCellWidget(rowPosition, 7, commitButton)
        # Set the default value for the 'Total' column

        receiptButton = QPushButton("no")
        receiptButton.clicked.connect(lambda _, b=receiptButton: self.receiptButtonClicked(b))
        # receiptButton.setStyleSheet("background-color: lightyellow;")

        self.expenseTable.setCellWidget(rowPosition, 5, receiptButton)

        # Set the default value for the 'Total' column
        item = QTableWidgetItem("0.00")
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        item.setText("0.00")  # default value
        self.expenseTable.setItem(rowPosition, 6, item)

    def getTypes(self):
        return ['Type1', 'Type2', 'Type3', 'Type4']  # Example types

    def RowCreator(self, num_rows):
        # print("Starting RowCreator...")  # Start of function

        types = self.getTypes()

        for _ in range(num_rows):
            # print("Inserting new row...")  # Before inserting a new row
            rowPosition = self.expenseTable.rowCount()
            self.expenseTable.insertRow(rowPosition)

            # Select random type and set it
            # print("Setting type...")  # Before setting type
            selected_type = random.choice(types)
            type_dropdown = self.createTypeDropdown()
            type_dropdown.setCurrentText(selected_type)
            self.expenseTable.setCellWidget(rowPosition, 0, type_dropdown)

            # Set name to the type selected
            # print("Setting name...")  # Before setting name
            name_item = QTableWidgetItem(selected_type)
            self.expenseTable.setItem(rowPosition, 1, name_item)

            # Assign a random total value between $0 and $1000 for example
            # print("Setting total...")  # Before setting total
            total_value = f"${random.uniform(0, 1000):.2f}"
            total_item = QTableWidgetItem(total_value)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.expenseTable.setItem(rowPosition, 6, total_item)

            # Add the 'Commit' button
            # print("Adding commit button...")  # Before adding commit button
            commitButton = QPushButton("Commit")
            commitButton.clicked.connect(lambda _, b=commitButton: self.commitButtonClicked(b))
            self.expenseTable.setCellWidget(rowPosition, 7, commitButton)

        # print("Finished RowCreator")  # End of function

    def StatButtonClicked(self):
        print("Working")
        data = self.getCommittedExpenseData()
        viewStats(self)

    def headerDoubleClicked(self, logicalIndex):

        if logicalIndex == 0:  # If the 'Type' header is double-clicked

            # 1. Convert QComboBox to QTableWidgetItem
            numRows = self.expenseTable.rowCount()
            for row in range(numRows):
                widget = self.expenseTable.cellWidget(row, logicalIndex)
                if isinstance(widget, QComboBox):
                    itemText = widget.currentText()
                    self.expenseTable.setItem(row, logicalIndex, QTableWidgetItem(itemText))

            # 2. Sort the column
            self.expenseTable.sortItems(logicalIndex, Qt.SortOrder.AscendingOrder)

            # 3. Convert QTableWidgetItem back to QComboBox
            for row in range(numRows):
                item = self.expenseTable.item(row, logicalIndex)
                if item:
                    comboBox = self.createTypeDropdown()
                    comboBox.setCurrentText(item.text())
                    self.expenseTable.setCellWidget(row, logicalIndex, comboBox)

        elif logicalIndex == 3:  # If the 'Due Date' header is double-clicked
            self.expenseTable.sortItems(logicalIndex, Qt.SortOrder.AscendingOrder)

    def launchStatsView(self, data):
        launch_view(data, self.getDetailedExpensesForType)

    def getCommittedExpenseData(self):
        data = {}
        for row in range(self.expenseTable.rowCount()):
            commitButton = self.expenseTable.cellWidget(row, 7)  # Assuming Commit button is in column 7
            if not commitButton.isEnabled():  # Check if the expense is committed
                type_widget = self.expenseTable.cellWidget(row, 0)  # Assuming Type dropdown is in column 0
                expense_type = type_widget.currentText()
                amount_item = self.expenseTable.item(row, 6)  # Assuming Total is in column 6
                amount = float(amount_item.text().replace("$", "").strip())
                if expense_type in data:
                    data[expense_type] += amount
                else:
                    data[expense_type] = amount
        return data

    def getExpensesForType(self, expense_type):
        expenses = []
        for row in range(self.expenseTable.rowCount()):
            commitButton = self.expenseTable.cellWidget(row, 7)  # Assuming Commit button is in column 7
            if not commitButton.isEnabled():  # Check if the expense is committed
                type_widget = self.expenseTable.cellWidget(row, 0)  # Assuming Type dropdown is in column 0
                if type_widget.currentText() == expense_type:
                    expense_name = self.expenseTable.item(row, 1).text()  # Assuming Name is in column 1
                    expense_date = self.expenseTable.item(row, 3).text()  # Assuming Due Date is in column 3
                    amount_item = self.expenseTable.item(row, 6).text()  # Assuming Total is in column 6
                    expenses.append({
                        "Name": expense_name,
                        "Date": expense_date,
                        "Amount": float(amount_item.replace("$", "").strip())
                    })

        # Write expenses to a file
        with open('expense_data.txt', 'w') as f:
            json.dump(expenses, f)

    def getDetailedExpensesForType(self, expense_type):
        detailed_expenses = []
        for row in range(self.expenseTable.rowCount()):
            type_widget = self.expenseTable.cellWidget(row, 0)  # Assuming Type dropdown is in column 0
            if type_widget.currentText() == expense_type:
                name_item = self.expenseTable.item(row, 1)  # Assuming Name is in column 1
                date_item = self.expenseTable.item(row, 3)  # Assuming Date is in column 3
                amount_item = self.expenseTable.item(row, 6)  # Assuming Total is in column 6

                detailed_expenses.append({
                    "Name": name_item.text(),
                    "Date": date_item.text(),
                    "Amount": float(amount_item.text().replace("$", "").strip())
                })
        return detailed_expenses


def loadStylesheet(filename):
    with open(filename, "r") as file:
        return file.read()


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)

        stylesheet = loadStylesheet("IntellijThemeGrey.qss")
        app.setStyleSheet(stylesheet)
        window = MyWindow()  # Ensure this class is defined
        window.show()

        sys.exit(app.exec())
    except Exception as e:
        print(f"An error occurred: {e}")
# Application Features and Functionalities:
# - Basic Python knowledge expanded to proficiency with multiple libraries and application creation.
# - Developed debugging skills.
#
# File Operations:
# - New Sheet: Create a new blank sheet.
# - Open Sheet: Open an existing sheet.
# - Save Sheet: Save the current sheet.
# - Save As: Save the current sheet with a different name or location.
# - Export:
#   - To PDF: Export the current sheet as a PDF.
#   - To Excel: Export the current sheet in Excel format.
#
# Settings:
# - Application Size: Adjust the size for accessibility.
# - Color Category:
#   - Customizable color assignments for categories.
#   - Automatic coloration for table population based on category for aesthetics.
#   - Add or modify categories and subcategories.
# - Font:
#   - Type: Choose font type for the application.
#   - Size: Adjust the font size for readability.
#
# Edit Menu:
# - Redo Line: Reapply the last undone action on a line.
# - Undo Line: Revert the last action on a line.
# - Cut/Copy/Paste Line: Basic line manipulation functions.
# - Select All: Select all lines in the current view.
# - Delete Line: Remove the selected line.
#
# Client Server Menu:
# - Additional unknown functions to be added.
#
# Miscellaneous:
# - Commit All Lines: Save all lines that meet commit criteria to permanent storage.
# - Income Table: No current functionality, to be developed.
#        self.setWindowIcon(QIcon('images/icons8-monkey-96.png'))
