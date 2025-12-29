from pathlib import Path
from typing import Dict

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget, QHeaderView, QTableWidgetItem, \
    QAbstractItemView, QLineEdit
from PySide6.QtCore import Qt

from service.sounds_service import sound_service
from service.settings_service import settings_service

class ConfigureSoundPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sound_service = sound_service
        self.setWindowTitle("Configure Sounds")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.resize(600, 400)

        layout = QVBoxLayout()

        #Sound Path
        self.sound_path = QLineEdit()
        print(settings_service.settings)

        curr_settings: Dict = settings_service.settings
        soundpath = Path(curr_settings["sound_path"])
        self.sound_path.setText(soundpath.as_uri())

        layout.addWidget(self.sound_path)

        #Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Sound Name", "File Path", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        #Header Settings
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 80)

        #loads the table data
        self.load_table_data()

        layout.addWidget(self.table)

        #Close Button
        close_button = QPushButton("Close Me")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def load_table_data(self):
        self.table.setRowCount(len(self.sound_service.sounds_list))

        for row, sound in enumerate(self.sound_service.sounds_list):
            # Create table items from the object attributes
            name_item = QTableWidgetItem(sound.name)
            path_item = QTableWidgetItem(sound.mp3_path)

            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
            delete_btn.clicked.connect(lambda _, r=row: self.delete_row(r))

            # Insert items into the table
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, path_item)

            self.table.setCellWidget(row, 2, delete_btn)

    def delete_row(self, row):
        self.sound_service.delete_sound_by_id(row)
        self.load_table_data()