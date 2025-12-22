#!/usr/bin/env python3
import subprocess
import sys
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
from pynput import keyboard


class SoundboardHijacker:
    def __init__(self):
        self.original_mic = None
        self.def_sink = None
        self.sounds_dir = Path("sounds")
        self.sounds_dir.mkdir(exist_ok=True)
        self.sound_files = sorted([f.name for f in self.sounds_dir.glob('*.*') if f.suffix in ['.mp3', '.wav', '.ogg']])
        self.target_idx = None

    def setup(self):
        print("🧹 Cleaning audio modules...")
        subprocess.run(['pactl', 'unload-module', 'module-loopback'], capture_output=True)
        subprocess.run(['pactl', 'unload-module', 'module-null-sink'], capture_output=True)
        subprocess.run(['pactl', 'unload-module', 'module-remap-source'], capture_output=True)

        try:
            self.original_mic = subprocess.check_output(['pactl', 'get-default-source'], text=True).strip()
            self.def_sink = subprocess.check_output(['pactl', 'get-default-sink'], text=True).strip()
        except subprocess.CalledProcessError:
            print("❌ Error: Audio system not responding.")
            sys.exit(1)

        # 1. Create the Soundboard Sink (This is JUST for the files)
        subprocess.run(['pactl', 'load-module', 'module-null-sink', 'sink_name=sb_only',
                        'sink_properties=device.description="SB_Files_Only"'])

        # 2. Create the Final Mixer (Where Mic and SB meet)
        subprocess.run(['pactl', 'load-module', 'module-null-sink', 'sink_name=final_mix',
                        'sink_properties=device.description="Final_Mixer"'])

        # 3. Create the Virtual Mic for Discord
        subprocess.run(['pactl', 'load-module', 'module-remap-source',
                        'master=final_mix.monitor',
                        'source_name=hijacked_mic',
                        'source_properties=device.description="Hijacked_Mic"'])

        # --- ROUTING (THE ECHO FIX) ---

        # Route 1: Physical Mic -> Final Mixer (Discord hears you, but you don't hear yourself)
        subprocess.run(['pactl', 'load-module', 'module-loopback', f'source={self.original_mic}',
                        'sink=final_mix', 'latency_msec=20'])

        # Route 2: Soundboard Sink -> Final Mixer (Discord hears the soundboard)
        subprocess.run(['pactl', 'load-module', 'module-loopback', 'source=sb_only.monitor',
                        'sink=final_mix', 'latency_msec=20'])

        # Route 3: Soundboard Sink -> Your Speakers (You hear the soundboard)
        subprocess.run(['pactl', 'load-module', 'module-loopback', 'source=sb_only.monitor',
                        f'sink={self.def_sink}', 'latency_msec=20'])

        subprocess.run(['pactl', 'set-default-source', 'hijacked_mic'])

        # Target the 'sb_only' sink for playback
        sd._terminate()
        sd._initialize()
        for i, d in enumerate(sd.query_devices()):
            if "SB_Files_Only" in d['name'] and d['max_output_channels'] > 0:
                self.target_idx = i
                break

        print(f"✅ Setup complete. Echo-free routing active.")

    def play_by_index(self, index):
        if index < 0 or index >= len(self.sound_files) or self.target_idx is None:
            return

        filename = self.sound_files[index]
        path = self.sounds_dir / filename

        try:
            data, fs = sf.read(path)
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            data = data / (np.max(np.abs(data)) + 1e-9) * 0.7

            print(f"🔊 Playing: {filename}")
            sd.play(data, fs, device=self.target_idx)
        except Exception as e:
            print(f"❌ Playback error: {e}")

    def cleanup(self):
        print("\n🧹 Restoring original audio state...")
        subprocess.run(['pactl', 'unload-module', 'module-loopback'], capture_output=True)
        subprocess.run(['pactl', 'unload-module', 'module-null-sink'], capture_output=True)
        subprocess.run(['pactl', 'unload-module', 'module-remap-source'], capture_output=True)
        if self.original_mic:
            subprocess.run(['pactl', 'set-default-source', self.original_mic], capture_output=True)


if __name__ == "__main__":
    sb = SoundboardHijacker()
    sb.setup()

    hotkey_map = {}
    for i in range(min(len(sb.sound_files), 12)):
        key = f'<f{i + 1}>'
        hotkey_map[key] = (lambda idx=i: sb.play_by_index(idx))

    with keyboard.GlobalHotKeys(hotkey_map) as h:
        try:
            print(f"\n🔥 READY. F1-F12 to play. CTRL+C to quit.")
            h.join()
        except KeyboardInterrupt:
            sb.cleanup()