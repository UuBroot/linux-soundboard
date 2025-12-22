import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from views.overview_grid import GridWidget
from views.menu_bar import setup_menu_bar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Widget Example")
        self.setGeometry(100, 100, 800, 600)

        setup_menu_bar(self)

        # Create a central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create and add the grid widget
        items_list = [
            "Item 1", "Item 2", "Item 3", "Item 4",
            "Item 5", "Item 6", "Item 7", "Item 8",
            "Item 9", "Item 10", "Item 11", "Item 12",
            "Item 13", "Item 14", "Item 15", "Item 16"
        ]
        #items_list = []

        self.grid_widget = GridWidget(items_list)
        main_layout.addWidget(self.grid_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())