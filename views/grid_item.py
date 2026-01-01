from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from model.sound_effect import SoundEffect
from service.pipewire_hijack_service import sb
from service.settings_service import settings_service

class GridItem(QWidget):
    def __init__(self, sound_effect_obj: SoundEffect, item_size, parent=None):
        super().__init__(parent)
        self.sound_effect_obj = sound_effect_obj
        self.item_size = item_size

        # Set fixed size to maintain 1:1 aspect ratio
        self.setFixedSize(self.item_size, self.item_size)

        # Create layout and button
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.button = QPushButton()
        self.button_layout = QVBoxLayout(self.button)

        self.button_label = QLabel(self.sound_effect_obj.name)
        self.button_label.setWordWrap(True)
        self.button_label.setAlignment(Qt.AlignCenter)
        self.button_layout.addWidget(self.button_label)

        self.button.setLayout(self.button_layout)
        self.button.setMinimumSize(self.item_size, self.item_size)
        self.button.setMaximumSize(self.item_size, self.item_size)
        self.button.clicked.connect(self._clicked)

        layout.addWidget(self.button)

    def _clicked(self):
        print(f"Item {self.sound_effect_obj.name} clicked!")
        print(f"Volume: {settings_service.settings['global_volume']}")
        self.sound_effect_obj.volume = settings_service.settings["global_volume"]
        sb.play(self.sound_effect_obj)
