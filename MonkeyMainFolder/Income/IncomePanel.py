import json
import os
import random
import shutil

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QDoubleValidator, QPalette, QColor, QIcon
from PyQt6.QtWidgets import (QWidget, QTableWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QPushButton, QSizePolicy, QLabel, QItemDelegate, QLineEdit, QStyledItemDelegate, QDateEdit,
                             QFileDialog, QTableWidgetItem, QHeaderView)
# Constants for Column Indices
METHOD_COLUMN = 0
SOURCE_NAME_COLUMN = 1
DATE_RECEIVED_COLUMN = 2
AMOUNT_COLUMN = 3
COMMIT_COLUMN = 4


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


class IncomePanel(QWidget):
    def __init__(self, parent=None):
        super(IncomePanel, self).__init__(parent)
        self.incomeTable = CustomTableWidget(1, 5)  # Five columns now
        self.totalIncomesLabel = QLabel("Total: $0.00")
        self.committedTotalIncomesLabel = QLabel("Committed Total: $0.00")

        self.setupUi()

    def setupIncomeTable(self, table):
        table.setHorizontalHeaderLabels(
            ['Method', 'Source Name', 'Date Received', 'Amount', 'Commit']
        )

        # Set Money Delegate for the 'Amount' column
        delegate = MoneyItemDelegate(table)
        table.setItemDelegateForColumn(AMOUNT_COLUMN, delegate)

        # Set column widths
        table.setColumnWidth(DATE_RECEIVED_COLUMN, 120)  # Date Received column
        table.setColumnWidth(AMOUNT_COLUMN, 100)  # Amount column
        table.setColumnWidth(COMMIT_COLUMN, 100)  # Commit column

        # Set other columns to stretch
        for index in [METHOD_COLUMN, SOURCE_NAME_COLUMN]:
            table.horizontalHeader().setSectionResizeMode(index, QHeaderView.ResizeMode.Stretch)

        # Setup individual cell items/widgets based on each row
        for i in range(3):  # Assuming 3 rows for the sake of demonstration
            for j in range(5):
                if j == METHOD_COLUMN:  # If it's the 'Method' column
                    table.setCellWidget(i, j, self.createTypeDropdown())
                elif j == DATE_RECEIVED_COLUMN:  # If it's the 'Date Received' column
                    date_editor = QDateEdit()
                    date_editor.setDate(QDate.currentDate())
                    date_editor.setDisplayFormat("dd/MM/yyyy")
                    table.setCellWidget(i, j, date_editor)
                elif j == AMOUNT_COLUMN:  # If it's the 'Amount' column
                    item = QTableWidgetItem()
                    item.setText("0.00")  # default value
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                    table.setItem(i, j, item)
                elif j == COMMIT_COLUMN:  # If it's the 'Commit' column
                    commitButton = QPushButton("Commit")
                    commitButton.clicked.connect(lambda _, b=commitButton: self.commitButtonClicked(b))
                    table.setCellWidget(i, j, commitButton)
                else:
                    table.setItem(i, j, QTableWidgetItem(" "))

        date_delegate = DateDelegate(table)
        table.setItemDelegateForColumn(DATE_RECEIVED_COLUMN, date_delegate)  # For 'Date Received' column
        self.incomeTable.model().dataChanged.connect(self.updateTotalLabels)

    def setupUi(self):
        layout = QVBoxLayout()
        self.setupIncomeTable(self.incomeTable)

        # Setup Bottom Panel with buttons
        buttonPanel = QWidget()
        buttonLayout = QHBoxLayout()

        addButton = QPushButton("Add income")
        deleteButton = QPushButton("Delete income")
        statisticsButton = QPushButton("Run Statistics")
        commitAllButton = QPushButton("Commit All incomes")

        # Connect buttons to their respective slots
        addButton.clicked.connect(self.addIncomeRow)
        deleteButton.clicked.connect(self.deleteIncomeRow)
        statisticsButton.clicked.connect(self.StatButtonClicked)
        commitAllButton.clicked.connect(self.commitAllButtonClicked)


        buttonLayout.addWidget(addButton)
        buttonLayout.addWidget(deleteButton)
        buttonLayout.addWidget(commitAllButton)
        buttonLayout.addWidget(statisticsButton)
        buttonLayout.addWidget(self.totalIncomesLabel)  # Fixed the attribute name here
        buttonLayout.addWidget(self.committedTotalIncomesLabel)

        buttonPanel.setLayout(buttonLayout)

        layout.addWidget(self.incomeTable)
        layout.addWidget(buttonPanel)

        self.setLayout(layout)

    def commitAllButtonClicked(self):
        # Iterate through all rows
        for row in range(self.incomeTable.rowCount()):
            commitButton = self.incomeTable.cellWidget(row, 4)  # 'Commit' button is in column 4

            # If the row is already committed (based on the commit button status), skip it
            if not commitButton.isEnabled():
                continue

            # Retrieve the name item to check if it's filled
            name_item = self.incomeTable.item(row, 1)  # 'Source Name' is in column 1

            # If the name field is empty, skip this row
            if not name_item or not name_item.text().strip():
                continue

            # Commit the row
            for col in range(self.incomeTable.columnCount()):
                item = self.incomeTable.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                widget = self.incomeTable.cellWidget(row, col)
                if widget:
                    widget.setEnabled(False)

            # Update the commit button status for the row
            commitButton.setEnabled(False)
            commitButton.setStyleSheet("background-color: green;")

        # Update totals after committing all eligible rows
        self.updateTotalLabels()

    def updateTotalLabels(self):
        total, committed_total = self.computeTotals()
        self.totalIncomesLabel.setText(f"Total: ${total:.2f}")
        self.committedTotalIncomesLabel.setText(f"Committed Total: ${committed_total:.2f}")

    def computeTotals(self):
        total = 0.0
        committed_total = 0.0
        for row in range(self.incomeTable.rowCount()):
            # Check if the income is committed
            commitButton = self.incomeTable.cellWidget(row, COMMIT_COLUMN)
            if not commitButton:
                continue

            # Get the amount
            amount_item = self.incomeTable.item(row, AMOUNT_COLUMN)
            if not amount_item:
                continue

            amount = float(amount_item.text().replace("$", "").strip())

            total += amount

            if not commitButton.isEnabled():  # If the income is committed
                committed_total += amount

        return total, committed_total

    def addIncomeRow(self):
        rowPosition = self.incomeTable.rowCount()
        self.incomeTable.insertRow(rowPosition)

        # Set dropdown for 'Method'
        self.incomeTable.setCellWidget(rowPosition, METHOD_COLUMN, self.createTypeDropdown())

        # Set empty fields for 'Source Name' and 'Date Received'
        self.incomeTable.setItem(rowPosition, SOURCE_NAME_COLUMN, QTableWidgetItem(""))

        date_editor = QDateEdit()
        date_editor.setDate(QDate.currentDate())
        date_editor.setDisplayFormat("dd/MM/yyyy")
        self.incomeTable.setCellWidget(rowPosition, DATE_RECEIVED_COLUMN, date_editor)

        # Set the default value for the 'Amount' column
        item = QTableWidgetItem("0.00")
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.incomeTable.setItem(rowPosition, AMOUNT_COLUMN, item)

        # Insert the 'Commit' button
        commitButton = QPushButton("Commit")
        commitButton.clicked.connect(lambda _, b=commitButton: self.commitButtonClicked(b))
        self.incomeTable.setCellWidget(rowPosition, COMMIT_COLUMN, commitButton)

    def deleteIncomeRow(self):
        selectedRows = self.incomeTable.selectionModel().selectedRows()
        for index in selectedRows:
            self.incomeTable.removeRow(index.row())
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
        row = self.incomeTable.indexAt(button.pos()).row()
        name_item = self.incomeTable.item(row, 1)  # Assuming the 'Source Name' is in column 1

        if not name_item or not name_item.text().strip():
            # highlight the name cell with a red background if the name is empty
            self.incomeTable.setCurrentCell(row, 1)
            return

        # If name is provided, proceed with committing
        for col in range(self.incomeTable.columnCount()):
            item = self.incomeTable.item(row, col)
            if item:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            widget = self.incomeTable.cellWidget(row, col)
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
            "Banking": ["debit", "credit1", "credit 2"],
            "Paper": ["Cash", "Check"],
            "Assets":["Gifts", "Donations", "Object"]

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
        types = self.getTypes()

        for _ in range(num_rows):
            rowPosition = self.incomeTable.rowCount()
            self.incomeTable.insertRow(rowPosition)

            # Select random type and set it
            selected_type = random.choice(types)
            type_dropdown = self.createTypeDropdown()
            type_dropdown.setCurrentText(selected_type)
            self.incomeTable.setCellWidget(rowPosition, 0, type_dropdown)

            # Set source name to the type selected
            name_item = QTableWidgetItem(selected_type)
            self.incomeTable.setItem(rowPosition, 1, name_item)

            # Assign a random total value between $0 and $1000 for example
            total_value = f"${random.uniform(0, 1000):.2f}"
            total_item = QTableWidgetItem(total_value)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.incomeTable.setItem(rowPosition, 3, total_item)  # Adjusted index

            # Add the 'Commit' button
            commitButton = QPushButton("Commit")
            commitButton.clicked.connect(lambda _, b=commitButton: self.commitButtonClicked(b))
            self.incomeTable.setCellWidget(rowPosition, 4, commitButton)  # Adjusted index

    def StatButtonClicked(self):
        print("Working")
        data = self.getCommittedincomeData()
        # viewStats(self)

    def headerDoubleClicked(self, logicalIndex):
        if logicalIndex == 0:  # If the 'Method' header is double-clicked
            # 1. Convert QComboBox to QTableWidgetItem
            numRows = self.incomeTable.rowCount()
            for row in range(numRows):
                widget = self.incomeTable.cellWidget(row, logicalIndex)
                if isinstance(widget, QComboBox):
                    itemText = widget.currentText()
                    self.incomeTable.setItem(row, logicalIndex, QTableWidgetItem(itemText))

            # 2. Sort the column
            self.incomeTable.sortItems(logicalIndex, Qt.SortOrder.AscendingOrder)

            # 3. Convert QTableWidgetItem back to QComboBox
            for row in range(numRows):
                item = self.incomeTable.item(row, logicalIndex)
                if item:
                    comboBox = self.createTypeDropdown()
                    comboBox.setCurrentText(item.text())
                    self.incomeTable.setCellWidget(row, logicalIndex, comboBox)

        elif logicalIndex == 3:  # If the 'Date Received' header is double-clicked
            self.incomeTable.sortItems(logicalIndex, Qt.SortOrder.AscendingOrder)


    def launchStatsView(self, data):
        print("Steve")
        # launch_view(data, self.getDetailedIncomesForType)

    def getCommittedincomeData(self):
        data = {}
        for row in range(self.incomeTable.rowCount()):
            commitButton = self.incomeTable.cellWidget(row, 4)  # Assuming Commit button is in column 4
            if not commitButton.isEnabled():  # Check if the income is committed
                type_widget = self.incomeTable.cellWidget(row, 0)  # Assuming Method dropdown is in column 0
                income_type = type_widget.currentText()
                amount_item = self.incomeTable.item(row, 3)  # Assuming Amount is in column 3
                amount = float(amount_item.text().replace("$", "").strip())
                if income_type in data:
                    data[income_type] += amount
                else:
                    data[income_type] = amount
        return data

    def getIncomesForType(self, income_type):
        incomes = []
        for row in range(self.incomeTable.rowCount()):
            commitButton = self.incomeTable.cellWidget(row, 7)  # Assuming Commit button is in column 7
            if not commitButton.isEnabled():  # Check if the income is committed
                type_widget = self.incomeTable.cellWidget(row, 0)  # Assuming Type dropdown is in column 0
                if type_widget.currentText() == income_type:
                    income_name = self.incomeTable.item(row, 1).text()  # Assuming Name is in column 1
                    income_date = self.incomeTable.item(row, 3).text()  # Assuming Due Date is in column 3
                    amount_item = self.incomeTable.item(row, 6).text()  # Assuming Total is in column 6
                    incomes.append({
                        "Name": income_name,
                        "Date": income_date,
                        "Amount": float(amount_item.replace("$", "").strip())
                    })

        # Write incomes to a file
        with open('income_data.txt', 'w') as f:
            json.dump(incomes, f)

    def getDetailedIncomesForType(self, income_type):
        detailed_incomes = []
        for row in range(self.incomeTable.rowCount()):
            type_widget = self.incomeTable.cellWidget(row, 0)  # Assuming Method dropdown is in column 0
            if type_widget.currentText() == income_type:
                name_item = self.incomeTable.item(row, 1)  # Assuming 'Source Name' is in column 1
                date_item = self.incomeTable.item(row, 2)  # Assuming 'Date Received' is in column 2
                amount_item = self.incomeTable.item(row, 3)  # Assuming 'Amount' is in column 3

                detailed_incomes.append({
                    "Name": name_item.text(),
                    "Date": date_item.text(),
                    "Amount": float(amount_item.text().replace("$", "").strip())
                })
        return detailed_incomes
