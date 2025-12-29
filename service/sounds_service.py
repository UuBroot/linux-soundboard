from PySide6.QtCore import QObject

from model.sound_effect import SoundEffect
from service.signal_service import signals

class SoundsService(QObject):
    def __init__(self):
        super().__init__()
        self.sounds_list: list[SoundEffect] = []

    def delete_sound_by_id(self,num):
        self.sounds_list.pop(num)
        signals.sounds_list_changed.emit(self.sounds_list)

    def add_sound(self,sound: SoundEffect):
        self.sounds_list.append(sound)
        signals.sounds_list_changed.emit(self.sounds_list)

sound_service = SoundsService()
