import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel

from service.settings_service import SettingsService
from service.sounds_service import SoundsService
from views.overview_grid import GridWidget
from views.menu_bar import setup_menu_bar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Widget Example")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Services
        self.sound_service = SoundsService()
        self.settings_service = SettingsService()

        #Grid Widget
        self.grid_widget = GridWidget(self.sound_service, self)
        main_layout.addWidget(self.grid_widget)

        setup_menu_bar(self, self.sound_service, self.settings_service)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())