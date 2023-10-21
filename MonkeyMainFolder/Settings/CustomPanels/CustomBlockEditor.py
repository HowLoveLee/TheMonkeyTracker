import random
import json
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
                             QGridLayout, QStyledItemDelegate, QSizePolicy)
import os
from PyQt6.QtCore import Qt, pyqtSignal, QObject


class CategoryManager(QObject):
    cats_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.filepath = None
        self.categories = {}
        self.original_categories = {}

    def initialize(self, filepath):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            return
        try:
            self.loadCats()
            self.backupCategories()
        except Exception as e:
            print(" ")

    def saveCats(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.categories, f)
            self.cats_saved.emit()
        except Exception as e:
            print("An error occurred while saving: ", e)

    def loadCats(self):
        try:
            with open(self.filepath, 'r') as f:
                self.categories = json.load(f)
        except Exception as e:
            print(" ")

    def backupCategories(self):
        self.original_categories = self.categories.copy()

    def addCategory(self, name, sub_categories=[]):
        self.categories[name] = sub_categories

    def addCategories(self, categories):
        if isinstance(categories, list):
            new_categories = {category: [] for category in categories}
            self.categories.update(new_categories)
        elif isinstance(categories, dict):
            self.categories.update(categories)
        self.saveCats()

    def getCategories(self):
        return self.categories



class CustomItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(size.height() + 10)  # add 30px to the height
        return size


class CustomBlockEditor(QWidget):
    def __init__(self, filepath, signal_broker=None):
        super().__init__()
        self.signal_broker = signal_broker

        self.blockList = None
        self.filepath = filepath
        self.categoryManager = CategoryManager()  # Initialize CategoryManager
        self.categoryManager.initialize(filepath)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.initUI()

    def random_light_color(self):
        return QColor(random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))

    def initUI(self):
        gridLayout = QGridLayout()

        # Block list
        self.blockList = QTreeWidget(self)
        self.blockList.setMinimumHeight(400)
        self.blockList.setItemDelegate(CustomItemDelegate(self.blockList))  # install the custom delegate

        self.blockList.itemChanged.connect(self.itemChanged)

        self.blockList.setHeaderHidden(True)
        self.blockList.setDragEnabled(True)
        self.blockList.setAcceptDrops(True)
        self.blockList.setDropIndicatorShown(True)
        self.blockList.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        gridLayout.addWidget(self.blockList, 0, 0, 2, 1)  # Spans two rows, one column
        # Adding items and sub-items

        items = self.categoryManager.categories

        for parent, children in items.items():
            parentItem = QTreeWidgetItem(self.blockList, [parent])
            parentItem.setBackground(0, self.random_light_color())
            for child in children:
                child_item = QTreeWidgetItem(parentItem, [child])
                child_item.setBackground(0, self.random_light_color())
        self.blockList.setCurrentItem(self.blockList.topLevelItem(0))
        self.expand_all_items(self.blockList)

        for i in range(self.blockList.topLevelItemCount()):
            top_item = self.blockList.topLevelItem(i)
            self.syncColors(top_item)
        # Button Layout
        buttonLayout = QHBoxLayout()

        # Add button layout to grid
        gridLayout.addLayout(buttonLayout, 2, 0)

        # Up and Down buttons on the right with QVBoxLayout
        verticalButtonLayout = QVBoxLayout()
        verticalButtonLayout.setSpacing(0)  # No spacing between buttons
        verticalButtonLayout.addStretch(1)  # Add stretch to push the following buttons to the bottom
        # Add Buttons

        self.saveButton = QPushButton('Save', self)
        self.cancelButton = QPushButton('Cancel', self)
        self.editButton = QPushButton('Edit Categories', self)

        self.addButton = QPushButton('Add Block', self)
        self.addButton.setStyleSheet('background-color: lightgreen;')

        self.deleteButton = QPushButton('Delete Block', self)
        self.deleteButton.setStyleSheet('background-color: red; color: white;')

        self.indentButton = QPushButton('Indent', self)
        self.outdentButton = QPushButton('Outdent', self)
        self.upButton = QPushButton('Up', self)
        self.downButton = QPushButton('Down', self)
        self.breakApartButton = QPushButton('Break Away Children', self)

        # Connect button signals to slots
        self.addButton.clicked.connect(self.addBlock)
        self.deleteButton.clicked.connect(self.deleteBlock)
        self.indentButton.clicked.connect(self.indentBlock)
        self.outdentButton.clicked.connect(self.outdentBlock)
        self.breakApartButton.clicked.connect(self.breakCats)
        self.editButton.clicked.connect(self.toggleEditMode)
        self.saveButton.clicked.connect(self.saveCats)
        self.cancelButton.clicked.connect(self.cancelCats)

        buttonLayout.addWidget(self.editButton)
        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addWidget(self.cancelButton)

        verticalButtonLayout.addWidget(self.breakApartButton)
        verticalButtonLayout.addWidget(self.addButton)
        verticalButtonLayout.addWidget(self.deleteButton)
        verticalButtonLayout.addWidget(self.indentButton)
        verticalButtonLayout.addWidget(self.outdentButton)

        # Connect Up and Down button signals to slots
        self.upButton.clicked.connect(self.moveUp)
        self.downButton.clicked.connect(self.moveDown)

        # Add to vertical layout
        verticalButtonLayout.addWidget(self.upButton)
        verticalButtonLayout.addWidget(self.downButton)

        # Add vertical layout to grid layout
        gridLayout.addLayout(verticalButtonLayout, 0, 1, 2, 1)  # Span two rows

        self.setLayout(gridLayout)
        # Initially disable all buttons and the tree widget
        self.setEditMode(False)

    def expand_all_items(self, tree_widget, item=None):
        if item is None:
            for i in range(tree_widget.topLevelItemCount()):
                top_item = tree_widget.topLevelItem(i)
                self.expand_all_items(tree_widget, top_item)
        else:
            item.setExpanded(True)
            for i in range(item.childCount()):
                child_item = item.child(i)
                self.expand_all_items(tree_widget, child_item)

    def toggleEditMode(self):
        # Toggle the editing mode
        self.setEditMode(not self.blockList.isEnabled())

    def updateCategoryManager(self):
        self.categoryManager.categories = {}  # Clearing old categories
        for i in range(self.blockList.topLevelItemCount()):
            top_item = self.blockList.topLevelItem(i)
            category_name = top_item.text(0)
            sub_categories = []
            for j in range(top_item.childCount()):
                sub_item = top_item.child(j)
                sub_categories.append(sub_item.text(0))
            self.categoryManager.addCategory(category_name, sub_categories)

    def saveCats(self):
        self.updateCategoryManager()
        self.categoryManager.saveCats()
        if self.signal_broker:
            self.signal_broker.global_cats_saved.emit()
        self.categoryManager.backupCategories()  # Backup the current state
        self.toggleEditMode()


    def setEditMode(self, enabled):
        # Enable/Disable the tree widget
        self.blockList.setEnabled(enabled)

        # Enable/Disable buttons
        self.saveButton.setEnabled(enabled)
        self.cancelButton.setEnabled(enabled)
        self.addButton.setEnabled(enabled)
        self.deleteButton.setEnabled(enabled)
        self.indentButton.setEnabled(enabled)
        self.outdentButton.setEnabled(enabled)
        self.upButton.setEnabled(enabled)
        self.downButton.setEnabled(enabled)
        self.breakApartButton.setEnabled(enabled)

        # Enable the Edit Categories button if other buttons are disabled
        self.editButton.setEnabled(not enabled)

    def restoreUIFromCategoryManager(self):
        self.blockList.clear()  # Clear the current list
        categories = self.categoryManager.getSavedCategories()
        for parent, children in categories.items():
            parentItem = QTreeWidgetItem(self.blockList, [parent])
            parentItem.setBackground(0, self.random_light_color())
            for child in children:
                child_item = QTreeWidgetItem(parentItem, [child])
                child_item.setBackground(0, self.random_light_color())

    def cancelCats(self):
        # print("Cancel Revert Changes")
        # Restore original categories
        self.categoryManager.restoreCategories()
        self.toggleEditMode()
        self.restoreUIFromCategoryManager()  # Restores the UI to the original state

    def addBlock(self):
        currentItem = self.blockList.currentItem()
        new_item = QTreeWidgetItem(["New Block"])

        if currentItem:
            parentItem = currentItem.parent()
            if parentItem:
                # If the current item has a parent, it's a subcategory.
                # Add the new block as a subcategory.
                parentItem.addChild(new_item)
                new_item.setBackground(0, parentItem.background(0))  # Sync color
            else:
                # If the current item is a top-level item, it's a category.
                # Add the new block as a category.
                index = self.blockList.indexOfTopLevelItem(currentItem)
                self.blockList.insertTopLevelItem(index + 1, new_item)
                new_item.setBackground(0, self.random_light_color())
        else:
            # If no item is selected, add the new block as a category.
            self.blockList.addTopLevelItem(new_item)
            new_item.setBackground(0, self.random_light_color())

        # Select and start editing the newly created item
        self.blockList.setCurrentItem(new_item)
        new_item.setFlags(new_item.flags() | Qt.ItemFlag.ItemIsEditable)  # Enable editing
        self.blockList.editItem(new_item)

    def syncColors(self, parentItem):
        parent_color = parentItem.background(0)
        for i in range(parentItem.childCount()):
            child_item = parentItem.child(i)
            child_item.setBackground(0, parent_color)
            self.syncColors(child_item)  # For nested subcategories, if any

    def itemChanged(self, item, column):
        if item.text(0) != "New Block":
            self.blockList.itemChanged.disconnect(self.itemChanged)  # Disconnect the signal temporarily
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Update the flags
            self.blockList.itemChanged.connect(self.itemChanged)  # Reconnect the signal

    def deleteBlock(self):
        selected_item = self.blockList.currentItem()
        if selected_item:
            parentItem = selected_item.parent()

            if parentItem:
                # Remove the child from its parent
                parentItem.removeChild(selected_item)
            else:
                # Promote all children to categories before removing the parent
                index = self.blockList.indexOfTopLevelItem(selected_item)
                for i in range(selected_item.childCount()):
                    child_item = selected_item.takeChild(0)
                    self.blockList.insertTopLevelItem(index + i, child_item)

                # Remove the selected item
                self.blockList.takeTopLevelItem(index)

    def indentBlock(self):
        currentItem = self.blockList.currentItem()
        if currentItem:
            # Check if the current item has children
            if currentItem.childCount() > 0:
                return

            # Check the depth of the current item
            depth = 0
            parent = currentItem.parent()
            while parent:
                depth += 1
                parent = parent.parent()

            # Limit indentation to 1 level; do nothing if trying to exceed
            if depth >= 1:
                return

            previous_sibling = self.getPreviousSibling(currentItem)
            if previous_sibling:
                # Remove the current item from its parent or top-level
                if currentItem.parent():
                    currentItem.parent().removeChild(currentItem)
                else:
                    self.blockList.takeTopLevelItem(self.blockList.indexOfTopLevelItem(currentItem))

                # Make it a child of the previous sibling
                previous_sibling.addChild(currentItem)

                # Update color to match parent
                currentItem.setBackground(0, previous_sibling.background(0))

                self.blockList.setCurrentItem(currentItem)

    def indentBlock(self):
        currentItem = self.blockList.currentItem()
        if currentItem:
            # Check if the current item has children
            if currentItem.childCount() > 0:
                return

            # Check the depth of the current item
            depth = 0
            parent = currentItem.parent()
            while parent:
                depth += 1
                parent = parent.parent()

            # Limit indentation to 1 level; do nothing if trying to exceed
            if depth >= 1:
                return

            previous_sibling = self.getPreviousSibling(currentItem)
            if previous_sibling:
                # Remove the current item from its parent or top-level
                if currentItem.parent():
                    currentItem.parent().removeChild(currentItem)
                else:
                    self.blockList.takeTopLevelItem(self.blockList.indexOfTopLevelItem(currentItem))

                # Make it a child of the previous sibling
                previous_sibling.addChild(currentItem)

                # Update color to match parent
                currentItem.setBackground(0, previous_sibling.background(0))

                self.blockList.setCurrentItem(currentItem)

    def outdentBlock(self):
        currentItem = self.blockList.currentItem()
        if currentItem and currentItem.parent():
            parentItem = currentItem.parent()

            # Remove from parent
            parentItem.removeChild(currentItem)

            # Find the index of the parent to insert the item after it
            if parentItem.parent():
                index = parentItem.parent().indexOfChild(parentItem)
                parentItem.parent().insertChild(index + 1, currentItem)
                currentItem.setBackground(0, parentItem.parent().background(0))
            else:
                index = self.blockList.indexOfTopLevelItem(parentItem)
                self.blockList.insertTopLevelItem(index + 1, currentItem)
                currentItem.setBackground(0, parentItem.background(0))

            self.blockList.setCurrentItem(currentItem)

    def moveUp(self):
        currentItem = self.blockList.currentItem()
        if currentItem:
            previous_item = self.getPreviousSibling(currentItem)
            if previous_item:
                child_count = previous_item.childCount()
                if child_count > 0:
                    # If the previous item has children, select the last child
                    self.blockList.setCurrentItem(previous_item.child(child_count - 1))
                else:
                    # Select the previous sibling item
                    self.blockList.setCurrentItem(previous_item)
            else:
                parentItem = currentItem.parent()
                if parentItem:
                    # If there is a parent, select it
                    self.blockList.setCurrentItem(parentItem)

    def moveDown(self):
        currentItem = self.blockList.currentItem()
        if currentItem:
            child_count = currentItem.childCount()

            if child_count > 0:
                # If the current item has children, select the first child
                self.blockList.setCurrentItem(currentItem.child(0))
            else:
                # If the current item doesn't have children, find its next sibling or parent's next sibling
                parentItem = currentItem.parent()
                nextItem = self.getNextSibling(currentItem)

                if nextItem:
                    self.blockList.setCurrentItem(nextItem)
                elif parentItem:
                    next_parentItem = self.getNextSibling(parentItem)
                    if next_parentItem:
                        self.blockList.setCurrentItem(next_parentItem)

    def getPreviousSibling(self, item):
        parentItem = item.parent()
        if parentItem:
            index = parentItem.indexOfChild(item)
            if index > 0:
                return parentItem.child(index - 1)
        else:
            index = self.blockList.indexOfTopLevelItem(item)
            if index > 0:
                return self.blockList.topLevelItem(index - 1)
        return None

    def getNextSibling(self, item):
        parentItem = item.parent()
        if parentItem:
            index = parentItem.indexOfChild(item)
            if index < parentItem.childCount() - 1:
                return parentItem.child(index + 1)
        else:
            index = self.blockList.indexOfTopLevelItem(item)
            if index < self.blockList.topLevelItemCount() - 1:
                return self.blockList.topLevelItem(index + 1)
        return None

    def breakCats(self):
        currentItem = self.blockList.currentItem()
        if currentItem:
            parentItem = currentItem.parent()
            if not parentItem:
                # This is a top-level item, so it's a category. Remove all its children.
                while currentItem.childCount() > 0:
                    currentItem.removeChild(currentItem.child(0))
