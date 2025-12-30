from pathlib import Path


class SoundEffect:
    def __init__(self, mp3_path: Path, name:str = None, volume=1.0):
        self.mp3_path = mp3_path
        #if no name is set generates the name from the mp3 path
        if name is None: name = self.make_name_from_dir()
        self.name = name
        self.volume = volume

    def make_name_from_dir(self, path: str = None) -> str:
        if path is None: path = str(self.mp3_path)
        return path.split("/")[-1].split(".")[0]