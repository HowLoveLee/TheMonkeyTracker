import json
import os
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QScrollArea


class ShortcutManager:
    def __init__(self):
        self.filepath = None
        self.shortcuts = {}
        self.original_shortcuts = {}

    def initialize(self, filepath):
        self.filepath = filepath

        if not os.path.exists(self.filepath):
            # print(f"No previous shortcuts found for {self.filepath}, starting fresh.")
            return

        try:
            self.loadShortcuts()
            self.backupShortcuts()
        except Exception as e:
            print(" ")
            # print(f"An error occurred: {e}")

    def saveShortcuts(self):
        # print("Saving shortcuts...")
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.shortcuts, f)
        except Exception as e:
            print(" ")
            # print(f"An error occurred while saving: {e}")

    def loadShortcuts(self):
        # print(f"Loading shortcuts from {self.filepath}")
        try:
            with open(self.filepath, 'r') as f:
                self.shortcuts = json.load(f)
            # print(f"Loaded shortcuts: {self.shortcuts}")
        except Exception as e:
            print(" ")
            # print(f"An error occurred while loading: {e}")

    def backupShortcuts(self):
        self.original_shortcuts = self.shortcuts.copy()
        # print(f"Backed up shortcuts: {self.original_shortcuts}")

    def addShortcut(self, name, keys=[]):
        self.shortcuts[name] = keys
        # print(f"Added shortcut: {name}, Keys: {keys}")


class CustomShortCutEditor(QWidget):
    def __init__(self, filepath):
        super().__init__()

        self.filepath = filepath
        self.layoutChanged = False  # Initialize the boolean flag

        self.shortcutManager = ShortcutManager()
        self.shortcutManager.initialize(self.filepath)
        self.shortcuts = self.shortcutManager.shortcuts

        self.mainLayout = QVBoxLayout()

        # Create a QWidget for the main content and set the layout
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)

        # Create a QScrollArea to hold the main content widget
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.mainWidget)
        self.scroll.setWidgetResizable(True)

        # Set the layout of the CustomShortCutEditor to hold the scroll area
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll)

        # Set size policy to stretch to the entire main panel
        self.scroll.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.setMinimumSize(1, 500)
        self.setBaseSize(300, 500)
        self.createLayout()

    def createLayout(self):
        # print(f"Creating layout with shortcuts: {self.shortcuts}")

        for shortcut, keybinds in self.shortcuts.items():
            label = QLabel(shortcut)

            hLayout = QHBoxLayout()
            hLayout.addWidget(label)

            if len(keybinds) == 1:
                currentBtn = QPushButton(keybinds[0])
                editBtn = QPushButton("Edit")
                hLayout.addWidget(currentBtn)
                hLayout.addWidget(editBtn)
            elif len(keybinds) > 1:
                for keybind in keybinds:
                    currentBtn = QPushButton(keybind)
                    hLayout.addWidget(currentBtn)
            else:
                editBtn = QPushButton("-")
                hLayout.addWidget(editBtn)

            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)

            self.mainLayout.addLayout(hLayout)
            self.mainLayout.addWidget(separator)
