import json
import os
import random
import shutil

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QDoubleValidator, QPalette, QColor, QIcon
from PyQt6.QtWidgets import (QWidget, QTableWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QPushButton, QSizePolicy, QLabel, QItemDelegate, QLineEdit, QStyledItemDelegate, QDateEdit,
                             QFileDialog, QTableWidgetItem, QHeaderView)


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


class ExpensePanel(QWidget):

    def __init__(self, parent=None):
        super(ExpensePanel, self).__init__(parent)

        self.expenseTable = CustomTableWidget(1, 8)
        self.totalExpensesLabel = QLabel("Total: $0.00")
        self.committedTotalExpensesLabel = QLabel("Committed Total: $0.00")

        self.setupUi()

    def setupExpenseTable(self, table):
        table.setHorizontalHeaderLabels(
            ['Type', 'Name', 'Summary', 'Due Date', 'Audit Date', 'Receipt', 'Total', 'Commit']
        )

        # Set Money Delegate for the 'Total' column
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

        # Setup individual cell items/widgets based on each row
        for i in range(3):  # Assuming 3 rows for the sake of demonstration
            for j in range(8):
                if j == 0:  # If it's the 'Type' column
                    table.setCellWidget(i, j, self.createTypeDropdown())

                elif j == 3:  # If it's the 'Due Date' column
                    date_editor = QDateEdit()
                    date_editor.setDate(QDate.currentDate())
                    date_editor.setDisplayFormat("dd/MM/yyyy")
                    table.setCellWidget(i, j, date_editor)

                elif j == 4:  # If it's the 'Audit Date' column
                    date_editor = QDateEdit()
                    date_editor.setDate(QDate.currentDate())
                    date_editor.setDisplayFormat("dd/MM/yyyy")
                    table.setCellWidget(i, j, date_editor)


                elif j == 5:
                    receiptButton = QPushButton("No")
                    receiptButton.clicked.connect(lambda _, b=receiptButton: self.receiptButtonClicked(b))
                    table.setCellWidget(i, j, receiptButton)

                elif j == 6:  # If it's the 'Total' column
                    item = QTableWidgetItem()
                    item.setText("0.00")  # default value
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                    table.setItem(i, j, item)

                elif j == 7:  # If it's the 'Commit' column
                    commitButton = QPushButton("Commit")
                    commitButton.clicked.connect(lambda _, b=commitButton: self.commitButtonClicked(b))
                    table.setCellWidget(i, j, commitButton)

                else:
                    table.setItem(i, j, QTableWidgetItem(" "))
        date_delegate = DateDelegate(table)
        table.setItemDelegateForColumn(3, date_delegate)  # For 'Due Date' column
        table.setItemDelegateForColumn(4, date_delegate)  # For 'Audit Date' column
        self.expenseTable.model().dataChanged.connect(self.updateTotalLabels)

    def setupUi(self):
        layout = QVBoxLayout()

        self.setupExpenseTable(self.expenseTable)

        # Setup Bottom Panel with buttons
        buttonPanel = QWidget()
        buttonLayout = QHBoxLayout()

        addButton = QPushButton("Add Expense")
        deleteButton = QPushButton("Delete Expense")
        statisticsButton = QPushButton("Run Statistics")
        commitAllButton = QPushButton("Commit All Expenses")

        # Connect buttons to their respective slots
        addButton.clicked.connect(self.addExpenseRow)
        deleteButton.clicked.connect(self.deleteExpenseRow)
        statisticsButton.clicked.connect(self.StatButtonClicked)
        commitAllButton.clicked.connect(self.commitAllButtonClicked)


        buttonLayout.addWidget(addButton)
        buttonLayout.addWidget(deleteButton)
        buttonLayout.addWidget(commitAllButton)
        buttonLayout.addWidget(statisticsButton)
        buttonLayout.addWidget(self.totalExpensesLabel)
        buttonLayout.addWidget(self.committedTotalExpensesLabel)

        buttonPanel.setLayout(buttonLayout)

        layout.addWidget(self.expenseTable)
        layout.addWidget(buttonPanel)

        self.setLayout(layout)

    def commitAllButtonClicked(self):
        # Iterate through all rows
        for row in range(self.expenseTable.rowCount()):
            commitButton = self.expenseTable.cellWidget(row, 7)  # Assuming Commit button is in column 7

            # If the row is already committed (based on the commit button status), skip it
            if not commitButton.isEnabled():
                continue

            # Retrieve the name item to check if it's filled (same as in the single commit method)
            name_item = self.expenseTable.item(row, 1)  # Assuming the 2nd column is the name

            # If the name field is empty, skip this row
            if not name_item or not name_item.text().strip():
                continue

            # Commit the row
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

            # Update the commit button status for the row
            commitButton.setEnabled(False)
            commitButton.setStyleSheet("background-color: green;")

        # Update totals after committing all eligible rows
        self.updateTotalLabels()

    def updateTotalLabels(self):
        total, committed_total = self.computeTotals()
        self.totalExpensesLabel.setText(f"Total: ${total:.2f}")
        self.committedTotalExpensesLabel.setText(f"Committed Total: ${committed_total:.2f}")

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
    def addExpenseRow(self):
        rowPosition = self.expenseTable.rowCount()
        self.expenseTable.insertRow(rowPosition)

        # Set default items/widgets for the new row
        self.expenseTable.setCellWidget(rowPosition, 0, self.createTypeDropdown())

        for col in [1, 2]:
            self.expenseTable.setItem(rowPosition, col, QTableWidgetItem(" "))

        # For 'Due Date' and 'Audit Date' columns
        for col in [3, 4]:
            date_editor = QDateEdit()
            date_editor.setDate(QDate.currentDate())
            date_editor.setDisplayFormat("dd/MM/yyyy")
            self.expenseTable.setCellWidget(rowPosition, col, date_editor)

        receiptButton = QPushButton("no")
        receiptButton.clicked.connect(lambda _, b=receiptButton: self.receiptButtonClicked(b))
        self.expenseTable.setCellWidget(rowPosition, 5, receiptButton)

        # Set the default value for the 'Total' column
        item = QTableWidgetItem("0.00")
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.expenseTable.setItem(rowPosition, 6, item)

        commitButton = QPushButton("Commit")
        commitButton.clicked.connect(lambda _, b=commitButton: self.commitButtonClicked(b))
        self.expenseTable.setCellWidget(rowPosition, 7, commitButton)

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
            destinationFolder = "C:\Dev\PythonProjects\TheMonkeyTracker\Receipts"
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
        button.setText("Committed")

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
        # viewStats(self)

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
        print("Steve")
        # launch_view(data, self.getDetailedExpensesForType)

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
