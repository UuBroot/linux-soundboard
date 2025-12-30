from pathlib import Path
from platformdirs import user_music_dir

class SettingsService:
    #formats need to be in lower case for consistency
    supported_formates = ["mp3","wav"]#more need to be tested

    def __init__(self):
        self.settings_path = self.generate_config_path()
        self.settings = self.generate_default_settings()

    def generate_default_settings(self) -> dict:
        return {
            "sound_path": self.generate_default_sound_path(),
        }

    @staticmethod
    def generate_config_path() -> Path:
        home = Path.home()
        config_dir = home / ".config" / "linux-soundboard"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @staticmethod
    def generate_default_sound_path() -> Path:
        music_path: Path = Path(user_music_dir())
        sound_dir = music_path / "Sounds"
        sound_dir.mkdir(parents=True, exist_ok=True)
        return sound_dir

settings_service = SettingsService()