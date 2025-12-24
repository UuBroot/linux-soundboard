import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QGridLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QMessageBox)

from model.sound_effect import SoundEffect

class NewSoundPopup(QDialog):
    def __init__(self, sound_service,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Sound")
        self.resize(500, 200)  # Larger starting size

        self.sound_service = sound_service

        # Main Layout
        self.main_layout = QVBoxLayout(self)

        # 1. Input Section (Grid)
        self.grid = QGridLayout()

        # Name Input
        self.grid.addWidget(QLabel("Sound Name:"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Airhorn")
        self.grid.addWidget(self.name_input, 0, 1, 1, 2)  # Span 2 columns

        # Path Input
        self.grid.addWidget(QLabel("File Path:"), 1, 0)
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select an .mp3 file...")
        self.grid.addWidget(self.path_input, 1, 1)

        # Browse Button
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.open_file_dialog)
        self.grid.addWidget(self.browse_btn, 1, 2)

        self.main_layout.addLayout(self.grid)
        self.main_layout.addStretch()  # Space between inputs and bottom buttons

        # 2. Bottom Button Section (Horizontal)
        self.button_layout = QHBoxLayout()

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)  # Built-in QDialog close

        self.add_btn = QPushButton("Add Sound")
        self.add_btn.setEnabled(False)  # Start disabled!
        self.add_btn.clicked.connect(self.add_sound)
        self.add_btn.setStyleSheet("""
                    QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }
                    QPushButton:enabled { background-color: #2ecc71; color: white; font-weight: bold; }
                """)

        self.button_layout.addWidget(self.close_btn)
        self.button_layout.addWidget(self.add_btn)

        self.main_layout.addLayout(self.button_layout)

        # --- VALIDATION LOGIC ---
        # Run this function every time the text changes in either box
        self.name_input.textChanged.connect(self.validate_inputs)
        self.path_input.textChanged.connect(self.validate_inputs)

    def validate_inputs(self):
        """Checks if both fields have content and enables/disables the button."""
        name_text = self.name_input.text().strip()
        path_text = self.path_input.text().strip()

        # Only enable if both strings are not empty
        is_valid = len(name_text) > 0 and len(path_text) > 0
        self.add_btn.setEnabled(is_valid)

    def open_file_dialog(self):
        # Opens the system file picker
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Sound File",
            "",
            "Audio Files (*.mp3 *.wav *.ogg)"
        )
        if file_path:
            self.path_input.setText(file_path)
            self.name_input.setText(file_path.split("/")[-1].split(".")[0])
        else:
            print("Invalid file selected")

    def is_file_valid(self, path):
        """
        Dedicated validation function.
        Returns True only if the file exists and is a supported audio type.
        """
        path = path.strip()
        if not os.path.isfile(path):
            return False

        valid_extensions = ('.mp3', '.wav', '.ogg', '.flac')
        return path.lower().endswith(valid_extensions)

    def get_data(self) -> SoundEffect:
        """Makes the data of the input fields available as a sound effect object."""
        return SoundEffect(
            self.path_input.text(),
            self.name_input.text()
        )

    def add_sound(self):
        if self.is_file_valid(self.path_input.text()):
            print(self.get_data())
            self.sound_service.add_sound(self.get_data())
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Could not load the sound file.")