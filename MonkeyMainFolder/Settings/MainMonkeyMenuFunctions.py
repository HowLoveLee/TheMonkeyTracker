import os

import pandas as pd
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QComboBox, QDateEdit, QPushButton, QTableWidgetItem

from MonkeyMainFolder.Settings.CustomPanels.CustomBlockEditor import CategoryManager


class MainMonkeyMenuFunctions:
    # we will need to pass our flags and signals to this one so it automatically updates when categories that
    # dont exist in the json file are added to the json file we can refresh on that instance. We need to use the
    # Save Category Manager, add    def __init__(broker, self, window): now that we have the broker we can immit to th
    # To the Refresh Cats inside the Expensepanel and rerresh and add the line.
    def __init__(self, window):
        self.main_window = window
        self.current_file_path = None
        self.is_dirty = False

    def markDirty(self):
        self.is_dirty = True

    def newFile(self):
        row_count = self.main_window.expensePanel.expenseTable.rowCount()

        if row_count > 0 and self.current_file_path and self.current_file_path != "New File":
            file_name_with_extension = os.path.basename(self.current_file_path)
            buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel

            reply = QMessageBox().question(None, 'Save Changes?',
                                           f"Do you wish to save changes to {file_name_with_extension} before proceeding?",
                                           buttons)

            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.saveFile()

        elif row_count > 0:
            buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel

            reply = QMessageBox().question(None, 'Save New File?',
                                           "This new file has information. Do you wish to save it?",
                                           buttons)

            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.saveFileAs()

        self.main_window.expensePanel.expenseTable.setRowCount(0)
        self.current_file_path = None

    def openFile(self):
        if self.current_file_path == "New File":
            # Handle the case when the current file is a new unsaved file
            reply = QMessageBox().question(None, 'Save Changes?',
                                           "This new File has information. Do you wish to save it?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.saveFile()

        elif self.current_file_path:
            # Handle the case when the current file is an existing saved file
            file_name_with_extension = os.path.basename(self.current_file_path)
            reply = QMessageBox().question(None, 'Save Changes?',
                                           f"Do you wish to save changes to {file_name_with_extension} before proceeding?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.saveFile()

        options = QFileDialog.Option.ReadOnly
        filePath, _ = QFileDialog.getOpenFileName(self.main_window, "Open Excel File", "",
                                                  "Excel Files (*.xlsx);;All Files (*)", options=options)
        if filePath:
            try:
                df = pd.read_excel(filePath, engine='openpyxl')
                # Populate the data into your UI components
                self._populate_table_from_df(df)
                self.current_file_path = filePath
            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", str(e))

    def _populate_table_from_df(self, df):
        # Instantiate CategoryManager
        categoryManager = CategoryManager()
        categoryManager.initialize(
            "C:/Dev/PythonProjects/TheMonkeyTracker/MonkeyMainFolder/Settings/JSONS/expensesEditor.json")

        # Create an empty list to hold non-matching expenses
        non_matching_expenses = []

        table = self.main_window.expensePanel.expenseTable
        table.setRowCount(0)

        categories = categoryManager.getCategories()  # fetch categories from the JSON file
        table = self.main_window.expensePanel.expenseTable
        table.setRowCount(0)

        for index, row in df.iterrows():
            table.insertRow(index)
            for col, value in enumerate(row):
                # Category comparison logic

                if col == 0:
                    store_value = value

                    # Create a QComboBox and populate it with hierarchical categories
                    combo = QComboBox()
                    model = QStandardItemModel()

                    # Used to find the index of the matching item later
                    index_to_select = -1
                    current_index = 0

                    for category, subcategories in categories.items():
                        category_item = QStandardItem(category)
                        if subcategories:  # If there are subcategories
                            category_item.setSelectable(False)
                            category_item.setEnabled(False)
                        else:  # If there are no subcategories
                            category_item.setSelectable(True)
                            category_item.setEnabled(True)
                        model.appendRow(category_item)
                        current_index += 1

                        for subcategory in subcategories:
                            subcategory_item = QStandardItem(f"  {subcategory}")
                            model.appendRow(subcategory_item)

                            # Check if the store_value matches this subcategory
                            if store_value.strip() == subcategory.strip():
                                index_to_select = current_index

                            current_index += 1
                    combo.setMaxVisibleItems(30)
                    combo.setModel(model)

                    if index_to_select >= 0:
                        combo.setCurrentIndex(index_to_select)
                    else:
                        non_matching_expenses.append(store_value)

                    table.setCellWidget(index, col, combo)

                elif col in [3, 4]:  # Assuming these are the Due Date and Audit Date columns
                    date_edit = QDateEdit()
                    date = QDate.fromString(value, "yyyy-MM-dd")
                    date_edit.setDate(date)
                    table.setCellWidget(index, col, date_edit)
                elif col == 5:  # Assuming this is the Receipt column
                    button = QPushButton("Yes" if value != " " else "No", table)
                    if value != " ":
                        button.receipt_path = value
                        button.setStyleSheet("background-color: green;")
                        button.clicked.connect(
                            lambda _, b=button: self.main_window.expensePanel.receiptButtonClicked(b))
                    else:
                        button.clicked.connect(lambda _, b=button: self.main_window.expensePanel.receiptButtonClicked(
                            b))  # This connects the button to the same function when there's no receipt, but you can
                        # adjust as needed
                    table.setCellWidget(index, col, button)
                elif col == 6:  # Assuming this is the "Total" column
                    item = QTableWidgetItem()
                    item.setText(f"{value:.2f}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                    table.setItem(index, col, item)
                elif col == 7:  # Assuming this is the Commit column
                    button = QPushButton(value, table)
                    if value == "Committed":
                        button.setStyleSheet("background-color: green;")
                        button.setEnabled(False)
                    else:  # If not committed, connect the button to the commit function
                        button.clicked.connect(lambda _, b=button: self.main_window.expensePanel.commitButtonClicked(b))
                    table.setCellWidget(index, col, button)
                else:
                    table.setItem(index, col, QTableWidgetItem(str(value)))

            commit_button = table.cellWidget(index, 7)
            if commit_button and commit_button.text() == "Committed":
                self._disable_row_editing(table, index)

        # Check if there are any non-matching expenses
        if non_matching_expenses:
            # Create a dialog to show non-matching expenses
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("The following expenses did not match any category:")
            msg.setInformativeText('\n'.join(non_matching_expenses))
            msg.setWindowTitle("Non-Matching Expenses")
            msg.setStandardButtons(QMessageBox.StandardButton.Apply | QMessageBox.StandardButton.Abort)

            retval = msg.exec()

            if retval == QMessageBox.StandardButton.Apply:
                # Add non-matching expenses to JSON
                categoryManager.addCategories(non_matching_expenses)

    def _disable_row_editing(self, table, row):
        """Disable editing for all cells in a specific row, except the Receipt column."""
        for col in range(table.columnCount()):
            if col == 5:  # Skip the Receipt column
                continue

            item = table.item(row, col)
            if item:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            widget = table.cellWidget(row, col)
            if widget:
                widget.setEnabled(False)

    def saveFile(self):
        # If the current file path exists, save directly to it.
        if self.current_file_path:
            self._saveToFile(self.current_file_path)
        else:
            # If the current file path doesn't exist, open a Save As dialog.
            self.saveFileAs()
        self.is_dirty = False

    def saveFileAs(self):
        filePath, _ = QFileDialog.getSaveFileName(self.main_window, "Save Excel File", "",
                                                  "Excel Files (*.xlsx);;All Files (*)")
        if filePath:
            self._saveToFile(filePath)
            self.current_file_path = filePath  # Update the current file path

    def _saveToFile(self, filePath):
        if not filePath:
            filePath, _ = QFileDialog.getSaveFileName(self.main_window, "Save Excel File", "",
                                                      "Excel Files (*.xlsx);;All Files (*)")
        if filePath:
            try:
                expense_table = self.main_window.expensePanel.expenseTable

                rows = expense_table.rowCount()
                columns = expense_table.columnCount()

                data = []

                for row in range(rows):
                    row_data = []
                    for column in range(columns):

                        # Transaction Type
                        if column == 0:
                            widget = expense_table.cellWidget(row, column)
                            if isinstance(widget, QComboBox):
                                row_data.append(widget.currentText())
                            else:
                                row_data.append(" ")

                        # Name, Summary
                        elif column in [1, 2]:
                            item = expense_table.item(row, column)
                            row_data.append(item.text() if item else " ")

                        # Due Date, Audit Date
                        elif column in [3, 4]:
                            date_widget = expense_table.cellWidget(row, column)
                            if isinstance(date_widget, QDateEdit):
                                row_data.append(date_widget.date().toString("yyyy-MM-dd"))
                            else:
                                row_data.append(" ")

                        # Receipts
                        elif column == 5:
                            button = expense_table.cellWidget(row, column)
                            if button and button.text() == "Yes" and hasattr(button, 'receipt_path'):
                                receipt_path = button.receipt_path
                                print(receipt_path)  # Printing the path for verification
                                row_data.append(receipt_path)
                            else:
                                row_data.append(" ")
                        elif column == 7:
                            button = expense_table.cellWidget(row, column)
                            if button:
                                row_data.append(button.text())
                            else:
                                row_data.append(" ")
                        # Total, Commit
                        else:
                            item = expense_table.item(row, column)
                            row_data.append(item.text() if item else " ")

                    data.append(row_data)

                df = pd.DataFrame(data,
                                  columns=["Transaction Type", "Name", "Summary", "Due Date", "Audit Date", "Receipt",
                                           "Total", "Commit"])
                df.to_excel(filePath, engine='openpyxl', index=False)

            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", str(e))

    def _create_df_from_table(self):
        # Extract data from ExpensePanel table to create a pandas DataFrame
        table = self.main_window.expensePanel.expenseTable
        column_labels = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        data = []
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = self._get_data_from_cell(table, row, col)
                row_data.append(item)
            data.append(row_data)
        return pd.DataFrame(data, columns=column_labels)

    def _get_data_from_cell(self, table, row, col):
        """Retrieve data from a cell in a QTableWidget."""
        item = table.item(row, col)

        # If the cell contains a QComboBox (Transaction Type)
        if type(table.cellWidget(row, col)) == QComboBox:
            return table.cellWidget(row, col).currentText()

        # If the cell contains a QDateEdit (Date)
        elif type(table.cellWidget(row, col)) == QDateEdit:
            date = table.cellWidget(row, col).date()
            return date.toString("yyyy-MM-dd")

        # If the cell is for the Receipts column (based on your column index)
        elif col == 6:  # Change the index if it's different
            button = table.cellWidget(row, col)
            if button and button.text() == "Yes" and hasattr(button, 'receipt_path'):
                return button.receipt_path
            else:
                return ""

        # Any other cell
        elif item:
            return item.text()
        else:
            return ""

    def openSettings(self):
        print("Open Settings")

    def onExitTriggered(self):
        print("Exit Trigger Event")
