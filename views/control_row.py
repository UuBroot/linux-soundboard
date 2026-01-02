from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QFrame, QPushButton, QStyle, QSlider, QHBoxLayout, QLabel, QCheckBox, QComboBox
from service.sounds_service import sound_service
from service.settings_service import settings_service
from service.pipewire_hijack_service import sb

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

        self.volume_label = QLabel("Volume: 100%")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(100)

        self.slider.valueChanged.connect(self.update_volume)

        volume_frame_layout.addWidget(self.volume_label)
        volume_frame_layout.addWidget(self.slider)
        layout.addWidget(volume_frame)

        #allow distortion button
        allow_distortion_button = QCheckBox("Allow Distortion")
        allow_distortion_button.setChecked(settings_service.settings["allow_distortion"]) #sets default from settings service
        allow_distortion_button.stateChanged.connect(self._update_allow_distortion)
        layout.addWidget(allow_distortion_button)

        #mic selection
        mic_selection_box = QFrame(self)
        mic_selection_box.setMaximumWidth(200)
        mic_selection_layout = QHBoxLayout(mic_selection_box)

        mic_selection_layout.addWidget(QLabel("Microphone:"))

        self.mic_selection = QComboBox()
        self.mic_selection.addItem("Default")
        self.mic_selection.addItems(sb.get_all_available_microphone_devices())
        self.mic_selection.currentIndexChanged.connect(self._changed_mic_selection)

        mic_selection_layout.addWidget(self.mic_selection)

        layout.addWidget(mic_selection_box)

    def update_volume(self, value):
        # Convert percentage to float
        float_value = value / 100.0
        print(f"Volume set to {float_value}")
        self.volume_label.setText(f"Volume: {value}%")
        settings_service.settings["global_volume"] = float_value

    def _changed_mic_selection(self, index):
        print(f"Selected mic: {self.mic_selection.currentText()}")
        if self.mic_selection.currentText() == "Default":
            settings_service.settings["output_device"] = ""
        else:
            settings_service.settings["output_device"] = self.mic_selection.currentText()
        sb.setup()

    def _update_allow_distortion(self, value):
        if value == 0:
            settings_service.settings["allow_distortion"] = False
            self.slider.setMaximum(100)
        else:
            settings_service.settings["allow_distortion"] = True
            self.slider.setMaximum(1000)


        print(f"Allow Distortion set to {settings_service.settings['allow_distortion']}")

    @staticmethod
    def on_stop_clicked():
        print("Stop clicked!")
        sound_service.stop_current_sound()
