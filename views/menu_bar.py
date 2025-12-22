from PySide6.QtGui import QAction, QKeySequence


def setup_menu_bar(window):
        """Set up the menu bar using the window instance"""
        menu_bar = window.menuBar()

        menu_bar.setNativeMenuBar(False) #is for macOS and disables native menu bars for development


        # --- File Menu ---
        file_menu = menu_bar.addMenu("&File")
        exit_action = QAction("Quit", window)
        exit_action.setMenuRole(QAction.QuitRole)
        exit_action.triggered.connect(window.close)
        file_menu.addAction(exit_action)

        # --- Sounds Menu ---
        sounds_menu = menu_bar.addMenu("&Sounds")
        add_sound_action = QAction("&Add Sound", window)
        add_sound_action.setShortcut(QKeySequence.New)
        add_sound_action.triggered.connect(add_sound)

        sounds_menu.addAction(add_sound_action)

def add_sound():
        print("Add sound!")
        pass