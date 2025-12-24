from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                               QVBoxLayout, QListWidget, QStackedWidget, QLabel, QFrame)
from PySide6.QtCore import Qt


class SidebarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sidebar Navigation Example")
        self.resize(800, 500)

        # 1. Main Layout (Horizontal)
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 2. Setup the Sidebar (QListWidget)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150)
        self.sidebar.addItems(["Dashboard", "Soundboard", "Settings", "About"])

        # Style the sidebar slightly
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                color: white;
                border: none;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 15px;
            }
            QListWidget::item:selected {
                background-color: #34495e;
                border-left: 5px solid #3498db;
            }
        """)

        # 3. Setup the Right-Side Content (QStackedWidget)
        self.content_stack = QStackedWidget()

        # Create different pages
        self.content_stack.addWidget(self.create_page("Welcome to the Dashboard", "#ecf0f1"))
        self.content_stack.addWidget(self.create_page("Your Sounds go here", "#bdc3c7"))
        self.content_stack.addWidget(self.create_page("System Settings", "#95a5a6"))
        self.content_stack.addWidget(self.create_page("About Linux Soundboard", "#7f8c8d"))

        # 4. Connect Sidebar to the Stack
        # currentRowChanged sends the index of the clicked item
        self.sidebar.currentRowChanged.connect(self.content_stack.setCurrentIndex)

        # 5. Assemble everything
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_stack)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def create_page(self, text, bg_color):
        """Helper to create a simple widget for each view"""
        page = QFrame()
        page.setStyleSheet(f"background-color: {bg_color};")
        layout = QVBoxLayout(page)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 20px; color: #2c3e50; font-weight: bold;")
        layout.addWidget(label)
        return page