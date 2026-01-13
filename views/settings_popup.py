from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QListWidget, QStackedWidget, QLabel, QFrame, QDialog,
                               QLineEdit, QComboBox, QCheckBox)
from PySide6.QtCore import Qt

from service.settings_service import settings_service
from service.sounds_service import sound_service
from service.signal_service import signals

class SettingsPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(800, 500)

        # Main Layout (Horizontal)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Setup the Sidebar (QListWidget)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150)

        self.sidebar.addItems(["Folders", "Pipewire", "About"])

        # Setup the Right-Side Content (QStackedWidget)
        self.content_stack = QStackedWidget()

        # Folder Conf
        folder_conf_page = QFrame()
        folder_conf_layout = QVBoxLayout(folder_conf_page)
        folder_conf_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        folder_conf_layout.addWidget(QLabel("Music Folder:"))
        sound_path = settings_service.settings.get("sound_path")
        self.sound_path_input = QLineEdit(str(sound_path))
        self.sound_path_input.textChanged.connect(self._path_changed)
        folder_conf_layout.addWidget(self.sound_path_input)
        self.content_stack.addWidget(folder_conf_page)

        # Pipewire Conf
        pipewire_conf_page = QFrame()
        pipewire_conf_layout = QVBoxLayout(pipewire_conf_page)
        pipewire_conf_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pipewire_conf_layout.addWidget(QLabel("Pipewire Configuration:"))
        do_wakeup_noise = QCheckBox("Make a Wakeup noise")
        do_wakeup_noise.setChecked(settings_service.settings.get("wakeup_noise"))
        do_wakeup_noise.clicked.connect(self._do_wakeup_noise_changed)

        pipewire_conf_layout.addWidget(do_wakeup_noise)

        self.content_stack.addWidget(pipewire_conf_page)

        # About
        about_page = QFrame()
        about_conf_layout = QVBoxLayout(about_page)
        about_conf_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        about_conf_layout.addWidget(QLabel("About"))
        about_conf_layout.addWidget(QLabel("Version 0.0.1"))

        self.content_stack.addWidget(about_page)

        # 4. Connect Sidebar to the Stack
        # currentRowChanged sends the index of the clicked item
        self.sidebar.currentRowChanged.connect(self.content_stack.setCurrentIndex)

        # 5. Assemble everything
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_stack)

    @staticmethod
    def _path_changed(value):
        print("Path changed!", value)
        settings_service.settings["sound_path"] = value
        sound_service.update_sounds_from_folder()

        signals.settings_changed.emit()

    @staticmethod
    def _do_wakeup_noise_changed(value):
        settings_service.settings["wakeup_noise"] = value
        signals.settings_changed.emit()