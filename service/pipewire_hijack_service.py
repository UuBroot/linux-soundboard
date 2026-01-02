#!/usr/bin/env python3
import subprocess
import sys
import threading
import soundfile as sf
import numpy as np

from model.sound_effect import SoundEffect

class SoundboardHijacker:
    def __init__(self):
        self.original_mic = None
        self.def_sink = None
        self.playback_process = None
        self._playback_lock = threading.Lock()
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

        print(f"✅ Setup complete. Virtual Mic Active.")

    def _play_thread(self, output_data, sample_rate):
        with self._playback_lock:
            try:
                # Try pw-play first (PipeWire native)
                self.playback_process = subprocess.Popen([
                    'pw-play',
                    '--target=sb_only',
                    '--format=f32',
                    f'--rate={sample_rate}',
                    '--channels=1',
                    '--raw',
                    '-'
                ], stdin=subprocess.PIPE)
            except FileNotFoundError:
                # Fallback to paplay (PulseAudio)
                self.playback_process = subprocess.Popen([
                    'paplay',
                    '--device=sb_only',
                    '--format=float32ne',
                    '--channels=1',
                    f'--rate={sample_rate}',
                    '--raw'
                ], stdin=subprocess.PIPE)

        process = self.playback_process
        try:
            if process and process.stdin:
                process.stdin.write(output_data.astype(np.float32).tobytes())
                process.stdin.close()
                process.wait()
        except BrokenPipeError:
            # Check if process was intentionally terminated
            with self._playback_lock:
                if self.playback_process is process:
                    print("⚠️ Playback process ended prematurely (Broken Pipe).")
        except Exception as e:
            print(f"❌ Error during playback streaming: {e}")
        finally:
            with self._playback_lock:
                if self.playback_process is process:
                    self.playback_process = None

    def play(self, effect: SoundEffect):
        """Plays a SoundEffect object using its specific volume setting."""
        path = effect.mp3_path

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

            self.stop() # Stop any current playback

            print(f"🔊 Playing: {effect.name} (Vol: {effect.volume:.2f})")

            thread = threading.Thread(target=self._play_thread, args=(output_data, sample_rate))
            thread.daemon = True
            thread.start()

        except Exception as e:
            print(f"❌ Playback error for {effect.name}: {e}")

    def stop(self):
        """Immediately stops all playing sounds."""
        with self._playback_lock:
            if self.playback_process:
                self.playback_process.terminate()
                self.playback_process = None
                print("🛑 Playback stopped.")

    def _unload_modules(self):
        subprocess.run(['pactl', 'unload-module', 'module-loopback'], capture_output=True)
        subprocess.run(['pactl', 'unload-module', 'module-null-sink'], capture_output=True)
        subprocess.run(['pactl', 'unload-module', 'module-remap-source'], capture_output=True)

    def cleanup(self):
        print("\n🧹 Restoring original audio state...")
        self.stop()
        self._unload_modules()
        if self.original_mic:
            subprocess.run(['pactl', 'set-default-source', self.original_mic], capture_output=True)

# Soundboard Hijacker Object generation.(maybe there is a better way to do this?)
sb = SoundboardHijacker()
sb.setup()