from pathlib import Path


def generate_config_path() -> Path:
    home = Path.home()
    config_dir = home / ".config" / "linux-soundboard"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def generate_default_sound_path() -> Path:
    home = Path.home()
    sound_dir = home / ".local/share" / "linux-soundboard"
    sound_dir.mkdir(parents=True, exist_ok=True)
    return sound_dir


class SettingsService:
    def __init__(self):
        self.settings_path = generate_config_path()
        self.settings = generate_default_settings()

def generate_default_settings():
    return {
        "sound_path": generate_default_sound_path(),
    }

