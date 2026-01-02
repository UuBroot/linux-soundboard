#!/usr/bin/env python3
import json
import subprocess
import sys
import threading
import soundfile as sf
import numpy as np

from model.sound_effect import SoundEffect
from service.settings_service import settings_service

class SoundboardHijacker:
    def __init__(self):
        self.original_mic = None
        self.def_sink = None
        self.playback_processes = []
        self._playback_lock = threading.Lock()
        self.module_ids = []
        self.audio_cache = {}

    def setup(self):
        print("Cleaning up...")
        self.cleanup()

        print("Setting up virtual mic...")
        try:
            """Tries to get the original mic and default sink. This is not only useful for restoring the original mic but is also a test to see if pipewire/pulseaudio is running"""
            output_device_setting = settings_service.settings["output_device"]
            if output_device_setting == "":
                print("No output device set. Using default.")
                self.original_mic = subprocess.check_output(['pactl', 'get-default-source'], text=True).strip()
                print("using default mic:", self.original_mic)
            else:
                print("using output device:", output_device_setting)
                self.original_mic = self.get_source_by_name(output_device_setting)

            self.def_sink = subprocess.check_output(['pactl', 'get-default-sink'], text=True).strip()
        except subprocess.CalledProcessError:
            print("❌ Error: Audio system not responding. Is PipeWire/PulseAudio running?")
            sys.exit(1)

        # 1. Create Routing Topology
        # We create one null sink that acts as our "Virtual Microphone"
        res = subprocess.run(['pactl', 'load-module', 'module-null-sink', 'sink_name=virtual_mic_sink',
                        'sink_properties=device.description="Virtual_Mic_Sink"'], capture_output=True, text=True)
        if res.returncode == 0:
            self.module_ids.append(res.stdout.strip())
        
        # Expose the monitor of the null sink as a proper Microphone source
        res = subprocess.run(
            ['pactl', 'load-module', 'module-remap-source', 'master=virtual_mic_sink.monitor', 'source_name=hijacked_mic',
             'source_properties=device.description="Hijacked_Mic"'], capture_output=True, text=True)
        if res.returncode == 0:
            self.module_ids.append(res.stdout.strip())

        # 2. Patch Cables
        # Route real mic into the virtual mic sink
        res = subprocess.run(['pactl', 'load-module', 'module-loopback', f'source={self.original_mic}', 'sink=virtual_mic_sink',
                        'latency_msec=20'], capture_output=True, text=True)
        if res.returncode == 0:
            self.module_ids.append(res.stdout.strip())

        # Set the virtual mic as default system input
        subprocess.run(['pactl', 'set-default-source', 'hijacked_mic'])

        # Explicitly set volumes to 100% and unmute to avoid "lower volume" or "no sound" issues
        subprocess.run(['pactl', 'set-sink-volume', 'virtual_mic_sink', '100%'], capture_output=True)
        subprocess.run(['pactl', 'set-sink-mute', 'virtual_mic_sink', '0'], capture_output=True)
        subprocess.run(['pactl', 'set-source-volume', 'hijacked_mic', '100%'], capture_output=True)
        subprocess.run(['pactl', 'set-source-mute', 'hijacked_mic', '0'], capture_output=True)

        print(f"✅ Setup complete. Virtual Mic Active.")

    def _play_thread(self, audio_data, sample_rate, effect_volume):
        with self._playback_lock:
            try:
                # Define targets: our virtual mic and the user's speakers
                targets = [
                    ('pw-play', '--target=virtual_mic_sink'),
                    ('pw-play', f'--target={self.def_sink}')
                ]
                
                # Check if pw-play exists by trying to run it
                subprocess.run(['pw-play', '--version'], capture_output=True, check=True)
                use_pw = True
            except (FileNotFoundError, subprocess.CalledProcessError):
                use_pw = False
                targets = [
                    ('paplay', '--device=virtual_mic_sink'),
                    ('paplay', f'--device={self.def_sink}')
                ]

            for cmd_base, target_flag in targets:
                cmd = [
                    cmd_base,
                    target_flag,
                    '--format=f32' if use_pw else '--format=float32ne',
                    f'--rate={sample_rate}',
                    '--channels=1',
                    '--raw',
                    '-'
                ]
                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                self.playback_processes.append(proc)

        processes = list(self.playback_processes)
        try:
            # We work with chunks of the float32 array directly to apply volume in real-time
            chunk_samples = 1024  # About 23ms at 44.1kHz
            for i in range(0, len(audio_data), chunk_samples):
                chunk = audio_data[i:i + chunk_samples]
                
                # Apply current volumes: 0.9 (headroom) * effect_volume * global_volume
                current_global_vol = settings_service.settings.get("global_volume", 1.0)
                final_chunk = (chunk * 0.9 * effect_volume * current_global_vol).astype(np.float32)
                chunk_bytes = final_chunk.tobytes()

                for proc in processes:
                    if proc and proc.stdin:
                        try:
                            proc.stdin.write(chunk_bytes)
                        except BrokenPipeError:
                            pass
            
            for proc in processes:
                if proc and proc.stdin:
                    try:
                        proc.stdin.close()
                    except (BrokenPipeError, OSError):
                        pass
                proc.wait()
                
        except Exception as e:
            print(f"❌ Error during playback streaming: {e}")
        finally:
            with self._playback_lock:
                # Only clear if these are the same processes we started
                if all(p in self.playback_processes for p in processes):
                    for p in processes:
                        if p in self.playback_processes:
                            self.playback_processes.remove(p)

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

                # Prepend the 'wake up' noise for Krisp (Optional)
                if settings_service.settings["wakeup_noise"]:
                    print("Adding wakeup noise...")
                    noise_floor = np.random.normal(0, 0.005, int(fs * 0.1))
                    processed_data = np.concatenate([noise_floor, data])

                    self.audio_cache[str(path)] = (processed_data, fs)
                else:
                    self.audio_cache[str(path)] = (data, fs)

            audio_data, sample_rate = self.audio_cache[str(path)]

            # Refresh default sink to handle output device changes
            try:
                self.def_sink = subprocess.check_output(['pactl', 'get-default-sink'], text=True).strip()
            except subprocess.CalledProcessError:
                pass

            self.stop() # Stop any current playback

            print(f"🔊 Playing: {effect.name} (Vol: {effect.volume:.2f})")

            thread = threading.Thread(target=self._play_thread, args=(audio_data, sample_rate, effect.volume))
            thread.daemon = True
            thread.start()

        except Exception as e:
            print(f"❌ Playback error for {effect.name}: {e}")

    def stop(self):
        """Immediately stops all playing sounds."""
        with self._playback_lock:
            if self.playback_processes:
                for proc in self.playback_processes:
                    proc.terminate()
                self.playback_processes.clear()
                print("🛑 Playback stopped.")

    def _unload_modules(self):
        if self.module_ids:
            for mid in reversed(self.module_ids):
                subprocess.run(['pactl', 'unload-module', mid], capture_output=True)
            self.module_ids.clear()
        else:
            # Fallback for when we don't have IDs (e.g. initial setup cleanup)
            # We try to unload by name to be as specific as possible
            # Note: pactl doesn't support unloading by name directly easily without grep/awk
            # so we keep the type-based unload as a last resort for initial cleanup
            print("Falling back to unloading modules by type. THERE MAY BE LINGERING MODULES.")
            subprocess.run(['pactl', 'unload-module', 'module-loopback'], capture_output=True)
            subprocess.run(['pactl', 'unload-module', 'module-null-sink'], capture_output=True)
            subprocess.run(['pactl', 'unload-module', 'module-remap-source'], capture_output=True)

    def cleanup(self):
        print("Restoring original audio state...")
        self.stop()
        
        # Ensure we set the default source back BEFORE unloading the module it belongs to
        if self.original_mic:
            print(f"Restoring original mic: {self.original_mic}")
            subprocess.run(['pactl', 'set-default-source', self.original_mic], capture_output=True)
            
        self._unload_modules()

    @staticmethod
    def get_default_microphone():
        return subprocess.check_output(['pactl', 'get-default-source'], text=True).strip()

    def get_source_by_name(self, name):
        all_microphones = self.get_all_available_microphone_devices()
        return all_microphones.get(name, "")

    @staticmethod
    def get_all_available_microphone_devices():
        """Returns a dict mapping 'Description' -> 'Technical Name'"""
        try:
            # Using JSON format here is much cleaner than manual string parsing
            result = subprocess.run(
                ['pactl', '--format=json', 'list', 'sources'],
                capture_output=True,
                text=True,
                check=True
            )
            sources = json.loads(result.stdout)

            # Map of Description -> Technical Name
            device_map = {}

            for s in sources:
                name = s.get("name", "")
                # Get the best available description
                description = s.get("description") or s.get("properties", {}).get("device.description") or name

                # Filter logic
                if ".monitor" in name or name == "hijacked_mic":
                    continue

                # PulseAudio JSON structure puts device.class inside 'properties'
                props = s.get("properties", {})
                device_class = props.get("device.class")
                media_class = props.get("media.class")

                if device_class == "sound" or media_class == "Audio/Source":
                    device_map[description] = name

            return device_map
        except Exception as e:
            print(f"Error getting microphones: {e}")
            return {}

# Soundboard Hijacker Object generation.(maybe there is a better way to do this?)
sb = SoundboardHijacker()
sb.setup()