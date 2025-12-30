from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QVBoxLayout, QFrame, QPushButton, QStyle
from service.sounds_service import sound_service

class ControlRow(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMaximumHeight(45)
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)

        palette = self.palette()
        palette.setColor(QPalette.Window, palette.color(QPalette.Base))
        palette.setColor(QPalette.Dark, palette.color(QPalette.Mid))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setLineWidth(1)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setAlignment(Qt.AlignTop)

        #Stop Button
        stop_button = QPushButton()
        stop_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
        stop_button.setIcon(stop_icon)
        stop_button.setFixedSize(40, 40)
        layout.addWidget(stop_button)
        stop_button.clicked.connect(self.on_stop_clicked)

    @staticmethod
    def on_stop_clicked():
        print("Stop clicked!")
        sound_service.stop_current_sound()
