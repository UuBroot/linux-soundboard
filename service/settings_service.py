from pathlib import Path
from platformdirs import user_music_dir
from service.signal_service import signals
import json

class SettingsService:
    #formats need to be in lower case for consistency
    supported_formates = ["mp3","wav"]#more need to be tested

    def __init__(self):
        self.settings_path = self.generate_config_path()

        self.settings = self.load_settings()
        if self.settings is None:
            self.settings = self.generate_default_settings()
            self.save_settings()  # Save the defaults immediately

        print(self.settings)
        print(self.settings_path)
        signals.settings_changed.connect(self.save_settings)

        signals.settings_changed.emit()


    def generate_default_settings(self) -> dict:
        return {
            "sound_path": str(self.generate_default_sound_path()),
            "global_volume": 1.0,
            "allow_distortion": False,#volumn over 100%
            "wakeup_noise": False,
            "output_device": "" #default is "". it will look for default output device in hijack service
        }

    def save_settings(self) -> None:
        settings = self.settings
        print(settings)

        # Ensure path-like objects are strings before saving to JSON
        serializable_settings = settings.copy()
        if isinstance(serializable_settings.get("sound_path"), Path):
            serializable_settings["sound_path"] = str(serializable_settings["sound_path"])

        with open(self.settings_path / "settings.json", "w") as f:
            json.dump(serializable_settings, f, indent=4)

    def load_settings(self) -> dict | None:
        try:
            with open(self.settings_path / "settings.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

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