import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel

from views.control_row import ControlRow
from views.overview_grid import GridWidget
from views.menu_bar import setup_menu_bar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linux Soundboard")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Control Row
        main_layout.addWidget(ControlRow(self))

        #Grid Widget
        self.grid_widget = GridWidget(self)
        main_layout.addWidget(self.grid_widget)

        setup_menu_bar(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())