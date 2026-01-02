import os
from pathlib import Path

from PySide6.QtCore import QObject
import shutil
from model.sound_effect import SoundEffect
from service.signal_service import signals
from service.settings_service import settings_service
from service.pipewire_hijack_service import sb

class SoundsService(QObject):
    def __init__(self):
        super().__init__()
        self.sounds_list: list[SoundEffect] = []

    def delete_sound_by_id(self, num):
        path = self.sounds_list[num].mp3_path
        if path.is_file():
            os.remove(path)
        self.update_sounds_from_folder()

    def add_sound(self, path: Path):
        """Doesn't add the sound to the list, but adds it to the Sounds folder copying it."""
        sounds_path: Path = Path(settings_service.settings.get("sound_path"))
        if path.is_file():
            try:
                shutil.copy(path, sounds_path)
                self.update_sounds_from_folder()
            except Exception as e:
                print(e)
        else:
            print("INTERNAL ERROR: Invalid file selected")

    def update_sounds_from_folder(self):
        #resettings current sounds
        self.sounds_list = []

        #update sounds from a folder
        sounds_path: Path = Path(settings_service.settings.get("sound_path"))
        print("Refreshing sounds from: ", sounds_path)

        for file_path in sounds_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower()[1:] in settings_service.supported_formates:
                print(type(file_path),file_path)
                new_sound_effect = SoundEffect(file_path)
                self.sounds_list.append(new_sound_effect)

        #sending update signal
        print(self.sounds_list)
        signals.sounds_list_changed.emit(self.sounds_list)

    @staticmethod
    def stop_current_sound():
        sb.stop()

sound_service = SoundsService()
