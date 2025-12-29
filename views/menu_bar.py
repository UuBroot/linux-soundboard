from PySide6.QtGui import QAction, QKeySequence

from views.configure_sound_popup import ConfigureSoundPopup
from views.new_sound_popup import NewSoundPopup
from service.pipewire_hijack_service import sb

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
        add_sound_action.triggered.connect(lambda _: add_sound(window))

        sounds_menu.addAction(add_sound_action)

        add_sound_action = QAction("&Stop Sound", window)
        add_sound_action.setShortcut(QKeySequence.Delete)
        add_sound_action.triggered.connect(lambda _: stop_playback())

        sounds_menu.addAction(add_sound_action)

        add_sound_action = QAction("&Configure Sounds", window)
        add_sound_action.setShortcut(QKeySequence.Preferences)
        add_sound_action.triggered.connect(lambda _: configure_sounds(window))

        sounds_menu.addAction(add_sound_action)

def add_sound(window):
        print("Add sound!")
        popup = NewSoundPopup(window)
        popup.exec()

def configure_sounds(window):
    print("Configure sounds!")
    popup = ConfigureSoundPopup(window)
    popup.exec()

def stop_playback():
        sb.stop()
