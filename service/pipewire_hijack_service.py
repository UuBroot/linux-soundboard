#!/usr/bin/env python3
import subprocess
import sys
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
from pynput import keyboard

from model.sound_effect import SoundEffect

class SoundboardHijacker:
    def __init__(self):
        self.original_mic = None
        self.def_sink = None
        self.sounds_dir = Path("../sounds")
        self.sounds_dir.mkdir(exist_ok=True)
        self.target_idx = None
        # Cache for loaded audio to prevent disk lag during F-key presses
        self.audio_cache = {}

    def setup(self):
        print("🧹 Cleaning audio modules...")
        self._unload_modules()

        try:
            self.original_mic = subprocess.check_output(['pactl', 'get-default-source'], text=True).strip()
            self.def_sink = subprocess.check_output(['pactl', 'get-default-sink'], text=True).strip()
        except subprocess.CalledProcessError:
            print("❌ Error: Audio system not responding. Is PipeWire/PulseAudio running?")
            sys.exit(1)

        # 1. Create Routing Topology
        subprocess.run(['pactl', 'load-module', 'module-null-sink', 'sink_name=sb_only',
                        'sink_properties=device.description="SB_Files_Only"'])
        subprocess.run(['pactl', 'load-module', 'module-null-sink', 'sink_name=final_mix',
                        'sink_properties=device.description="Final_Mixer"'])
        subprocess.run(
            ['pactl', 'load-module', 'module-remap-source', 'master=final_mix.monitor', 'source_name=hijacked_mic',
             'source_properties=device.description="Hijacked_Mic"'])

        # 2. Patch Cables
        subprocess.run(['pactl', 'load-module', 'module-loopback', f'source={self.original_mic}', 'sink=final_mix',
                        'latency_msec=20'])
        subprocess.run(
            ['pactl', 'load-module', 'module-loopback', 'source=sb_only.monitor', 'sink=final_mix', 'latency_msec=20'])
        subprocess.run(['pactl', 'load-module', 'module-loopback', 'source=sb_only.monitor', f'sink={self.def_sink}',
                        'latency_msec=20'])

        subprocess.run(['pactl', 'set-default-source', 'hijacked_mic'])

        # 3. Target the SoundDevice Index
        sd._terminate()
        sd._initialize()
        for i, d in enumerate(sd.query_devices()):
            if "SB_Files_Only" in d['name'] and d['max_output_channels'] > 0:
                self.target_idx = i
                break

        print(f"✅ Setup complete. Virtual Mic Active.")

    def play(self, effect):
        """Plays a SoundEffect object using its specific volume setting."""
        path = self.sounds_dir / effect.mp3_path

        try:
            # 1. Check Cache first
            if str(path) not in self.audio_cache:
                data, fs = sf.read(str(path))

                # Convert to mono
                if len(data.shape) > 1:
                    data = np.mean(data, axis=1)

                # Normalize to peak
                max_val = np.max(np.abs(data))
                if max_val > 0:
                    data = (data / max_val)

                # Prepend the 'wake up' noise for Krisp
                noise_floor = np.random.normal(0, 0.005, int(fs * 0.1))
                processed_data = np.concatenate([noise_floor, data])

                self.audio_cache[str(path)] = (processed_data, fs)

            audio_data, sample_rate = self.audio_cache[str(path)]

            final_volume = 0.9 * effect.volume
            output_data = audio_data * final_volume

            print(f"🔊 Playing: {effect.name} (Vol: {effect.volume:.2f})")
            sd.play(output_data, sample_rate, device=self.target_idx)

        except Exception as e:
            print(f"❌ Playback error for {effect.name}: {e}")

    def stop(self):
        """Immediately stops all playing sounds."""
        sd.stop()
        print("🛑 Playback stopped.")

    def _unload_modules(self):
        subprocess.run(['pactl', 'unload-module', 'module-loopback'], capture_output=True)
        subprocess.run(['pactl', 'unload-module', 'module-null-sink'], capture_output=True)
        subprocess.run(['pactl', 'unload-module', 'module-remap-source'], capture_output=True)

    def cleanup(self):
        print("\n🧹 Restoring original audio state...")
        self._unload_modules()
        if self.original_mic:
            subprocess.run(['pactl', 'set-default-source', self.original_mic], capture_output=True)


# --- EXECUTION EXAMPLE FOR TESTING ---
if __name__ == "__main__":
    sb = SoundboardHijacker()
    sb.setup()

    # Define your effects list
    effects = [
        SoundEffect("gunshot.mp3", "Gunshot", 0.40),
        SoundEffect("gunshot.mp3", "Gunshot", 0.80),
        SoundEffect("auf der spitze der welt-02.mp3", "Geilo", 0.70)
    ]

    # Map hotkeys to the model objects
    hotkey_map = {}
    for i, effect in enumerate(effects[:12]):
        key = f'<f{i + 1}>'
        # We use a default argument (eff=effect) to capture the current effect in the loop
        hotkey_map[key] = (lambda eff=effect: sb.play(eff))

    # Add a stop key
    hotkey_map['<esc>'] = sb.stop

    with keyboard.GlobalHotKeys(hotkey_map) as h:
        try:
            print(f"🔥 READY. F1-{f'F{len(effects)}'} to play. ESC to stop. CTRL+C to quit.")
            h.join()
        except KeyboardInterrupt:
            sb.cleanup()