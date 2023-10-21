from PyQt6.QtCore import QObject, pyqtSignal


class SignalBroker(QObject):
    global_cats_saved = pyqtSignal()


broker = SignalBroker()
