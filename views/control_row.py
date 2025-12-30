from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QFrame, QPushButton, QStyle, QSlider, QHBoxLayout, QLabel
from service.sounds_service import sound_service
from service.settings_service import settings_service

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


        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setAlignment(Qt.AlignTop)

        #Stop Button
        stop_button = QPushButton()
        stop_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
        stop_button.setIcon(stop_icon)
        stop_button.setFixedSize(40, 40)
        layout.addWidget(stop_button)
        stop_button.clicked.connect(self.on_stop_clicked)

        #Volumn Slider
        volume_frame = QFrame(self)
        volume_frame_layout = QHBoxLayout(volume_frame)
        volume_frame.setMaximumWidth(200)

        self.volume_label = QLabel("Volume: 50%")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)

        self.slider.valueChanged.connect(self.update_volume)

        volume_frame_layout.addWidget(self.volume_label)
        volume_frame_layout.addWidget(self.slider)
        layout.addWidget(volume_frame)

    def update_volume(self, value):
        # Convert percentage to float
        float_value = value / 100.0
        print(f"Volume set to {float_value}")
        self.volume_label.setText(f"Volume: {value}%")
        settings_service.settings["global_volume"] = float_value

    @staticmethod
    def on_stop_clicked():
        print("Stop clicked!")
        sound_service.stop_current_sound()
