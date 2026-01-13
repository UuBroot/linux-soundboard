from PySide6.QtCore import Signal, QObject

class SignalService(QObject):
    sounds_list_changed = Signal(list)
    settings_changed = Signal()

signals = SignalService()