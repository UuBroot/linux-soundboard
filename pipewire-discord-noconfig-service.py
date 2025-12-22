#!/usr/bin/env python3
"""
Transparent PipeWire Soundboard
Sets up a virtual mic as system default - works with Discord automatically!

The virtual mic combines: Real Mic + Soundboard
Discord doesn't need any configuration changes!
"""

import subprocess
import sounddevice as sd
import soundfile as sf
from pathlib import Path
import time
import sys


class TransparentSoundboard:
    """
    Creates a virtual microphone that becomes the system default.
    Mixes real mic + soundboard audio transparently.
    """

    def __init__(self):
        self.original_default_source = None
        self.soundboard_sink = "soundboard_sink"
        self.combined_source = "virtual_mic_combined"
        self.modules_loaded = []
        self.sounds_dir = Path("sounds")
        self.sounds_dir.mkdir(exist_ok=True)

    def get_default_source(self):
        """Get the current default audio input"""
        result = subprocess.run(
            ['pactl', 'get-default-source'],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    def setup_virtual_microphone(self):
        """
        Create a virtual microphone that:
        1. Captures from real mic
        2. Captures from soundboard
        3. Mixes them together
        4. Becomes the new system default
        """

        print("\n[1/4] Saving original default microphone...")
        self.original_default_source = self.get_default_source()
        print(f"  Original: {self.original_default_source}")

        # Step 1: Create null sink for soundboard output
        print("\n[2/4] Creating soundboard audio sink...")
        cmd = [
            'pactl', 'load-module', 'module-null-sink',
            f'sink_name={self.soundboard_sink}',
            'sink_properties=device.description="Soundboard_Audio"'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self.modules_loaded.append(result.stdout.strip())
            print(f"  ✓ Created: {self.soundboard_sink}")

        # Step 2: Create combined source using module-combine-stream
        # This mixes real mic + soundboard monitor
        print("\n[3/4] Creating combined virtual microphone...")

        # Use module-loopback to mix both sources
        # Loopback 1: Real mic -> Combined sink
        cmd1 = [
            'pactl', 'load-module', 'module-null-sink',
            f'sink_name=combined_mixer',
            'sink_properties=device.description="Audio_Mixer"'
        ]
        result1 = subprocess.run(cmd1, capture_output=True, text=True)
        if result1.returncode == 0:
            self.modules_loaded.append(result1.stdout.strip())

        # Route real mic to mixer
        cmd2 = [
            'pactl', 'load-module', 'module-loopback',
            f'source={self.original_default_source}',
            'sink=combined_mixer',
            'latency_msec=1'
        ]
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        if result2.returncode == 0:
            self.modules_loaded.append(result2.stdout.strip())

        # Route soundboard to mixer
        cmd3 = [
            'pactl', 'load-module', 'module-loopback',
            f'source={self.soundboard_sink}.monitor',
            'sink=combined_mixer',
            'latency_msec=1'
        ]
        result3 = subprocess.run(cmd3, capture_output=True, text=True)
        if result3.returncode == 0:
            self.modules_loaded.append(result3.stdout.strip())

        # Create remap source from mixer monitor (this is our new virtual mic)
        cmd4 = [
            'pactl', 'load-module', 'module-remap-source',
            f'source_name={self.combined_source}',
            'master=combined_mixer.monitor',
            'source_properties=device.description="Virtual_Microphone"'
        ]
        result4 = subprocess.run(cmd4, capture_output=True, text=True)
        if result4.returncode == 0:
            self.modules_loaded.append(result4.stdout.strip())
            print(f"  ✓ Created: {self.combined_source}")

        # Step 3: Set as default source
        print("\n[4/4] Setting virtual microphone as system default...")
        subprocess.run(['pactl', 'set-default-source', self.combined_source])
        print(f"  ✓ System default microphone is now: Virtual_Microphone")

        print("\n" + "=" * 60)
        print("SUCCESS! Virtual microphone is now active!")
        print("=" * 60)
        print("\nWhat this means:")
        print("  • Discord will automatically use your virtual mic")
        print("  • Your real voice is captured")
        print("  • Soundboard sounds mix in automatically")
        print("  • NO Discord settings changes needed!")
        print("=" * 60 + "\n")

    def find_soundboard_device_id(self):
        """Find the device ID for the soundboard sink"""
        devices = sd.query_devices()
        for idx, device in enumerate(devices):
            if self.soundboard_sink in device['name']:
                return idx
        return None

    def play_sound(self, filepath):
        """Play a sound through the virtual microphone"""
        device_id = self.find_soundboard_device_id()

        if device_id is None:
            print("Error: Could not find soundboard device")
            return False

        try:
            print(f"🔊 Playing: {filepath.name}")
            data, samplerate = sf.read(filepath)
            sd.play(data, samplerate, device=device_id)
            sd.wait()
            print("  ✓ Done")
            return True
        except Exception as e:
            print(f"Error playing sound: {e}")
            return False

    def list_sounds(self):
        """List available sound files"""
        sounds = list(self.sounds_dir.glob('*.*'))

        if not sounds:
            print(f"\nNo sounds found in {self.sounds_dir}/")
            print("Add .mp3, .wav, or .ogg files to get started")
            return []

        print("\n=== Available Sounds ===")
        for i, sound in enumerate(sounds, 1):
            print(f"  {i}. {sound.name}")
        print("=" * 40)

        return sounds

    def cleanup(self):
        """Restore original audio configuration"""
        print("\n" + "=" * 60)
        print("Cleaning up...")
        print("=" * 60)

        # Restore original default source
        if self.original_default_source:
            print(f"\nRestoring original microphone: {self.original_default_source}")
            subprocess.run(['pactl', 'set-default-source', self.original_default_source])

        # Unload all modules in reverse order
        print("\nRemoving virtual devices...")
        for module_id in reversed(self.modules_loaded):
            subprocess.run(['pactl', 'unload-module', module_id],
                           capture_output=True)

        print("✓ Cleanup complete!")
        print("✓ Original audio configuration restored")


def check_dependencies():
    """Check if required tools are available"""
    import shutil

    missing = []

    if not shutil.which('pactl'):
        missing.append("pactl (pulseaudio-utils)")

    try:
        import sounddevice
        import soundfile
    except ImportError:
        missing.append("Python packages (sounddevice, soundfile)")

    if missing:
        print("Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with:")
        print("  sudo apt install pulseaudio-utils")
        print("  pip install sounddevice soundfile numpy")
        return False

    return True


def main():
    """Main application"""

    if not check_dependencies():
        sys.exit(1)

    print("=" * 60)
    print("TRANSPARENT PIPEWIRE SOUNDBOARD")
    print("No Discord configuration needed!")
    print("=" * 60)

    soundboard = TransparentSoundboard()

    try:
        # Setup virtual microphone
        soundboard.setup_virtual_microphone()

        # List sounds
        sounds = soundboard.list_sounds()

        if not sounds:
            print("\nTip: Add sound files to 'sounds/' directory")
            input("\nPress Enter to exit and restore settings...")
            return

        # Interactive mode
        print("\n" + "=" * 60)
        print("SOUNDBOARD READY")
        print("=" * 60)
        print("\nCommands:")
        print("  1-9 : Play sound by number")
        print("  l   : List sounds")
        print("  t   : Test with Discord")
        print("  q   : Quit and restore settings")
        print("=" * 60 + "\n")

        while True:
            try:
                cmd = input("Command> ").strip().lower()

                if cmd == 'q':
                    break
                elif cmd == 'l':
                    sounds = soundboard.list_sounds()
                elif cmd == 't':
                    print("\n=== Discord Test Instructions ===")
                    print("1. Open Discord (if not already open)")
                    print("2. Join a voice channel")
                    print("3. Speak - you should be heard normally")
                    print("4. Play a sound from this soundboard")
                    print("5. The sound should be heard in Discord!")
                    print("   (No settings changes needed)\n")
                elif cmd.isdigit():
                    idx = int(cmd) - 1
                    if 0 <= idx < len(sounds):
                        soundboard.play_sound(sounds[idx])
                    else:
                        print("Invalid number")
                elif cmd:
                    # Try to play by name
                    filepath = soundboard.sounds_dir / cmd
                    if filepath.exists():
                        soundboard.play_sound(filepath)
                    else:
                        print(f"Sound not found: {cmd}")

            except EOFError:
                break

    except KeyboardInterrupt:
        print("\n\nInterrupted!")

    finally:
        soundboard.cleanup()
        print("\nGoodbye!")


if __name__ == "__main__":
    main()