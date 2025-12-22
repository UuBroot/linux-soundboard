#!/usr/bin/env python3
"""
PipeWire Virtual Audio Cable for Discord Soundboard
Routes audio files through your Discord microphone input

This creates a virtual audio device that combines your real mic + soundboard audio
"""

import subprocess
import json
import time
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path


class PipeWireVirtualDevice:
    """Manages PipeWire virtual audio devices"""

    def __init__(self):
        self.virtual_sink_name = "soundboard_output"
        self.virtual_source_name = "soundboard_input"
        self.loopback_module = None

    def create_virtual_device(self):
        """Create a virtual audio device (null sink) for the soundboard"""
        print("Creating virtual audio device...")

        # Create a null sink (virtual output device)
        cmd = [
            'pactl', 'load-module', 'module-null-sink',
            f'sink_name={self.virtual_sink_name}',
            'sink_properties=device.description="Soundboard_Output"'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ Created virtual output: {self.virtual_sink_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual device: {e.stderr}")
            return False

    def create_combined_source(self, mic_source=None):
        """
        Create a combined source that mixes your real microphone + soundboard
        This is what Discord will use as input
        """
        print("Creating combined audio source (mic + soundboard)...")

        # If no mic specified, use default
        if not mic_source:
            result = subprocess.run(
                ['pactl', 'get-default-source'],
                capture_output=True, text=True
            )
            mic_source = result.stdout.strip()

        print(f"Using microphone: {mic_source}")

        # Create a combined source that mixes multiple inputs
        # This combines: real mic + soundboard output
        cmd = [
            'pactl', 'load-module', 'module-combine-sink',
            f'sink_name=discord_combined',
            'sink_properties=device.description="Discord_Mic+Soundboard"'
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ Created combined sink")
        except subprocess.CalledProcessError as e:
            print(f"Note: {e.stderr}")

        # Create loopback from soundboard to combined output
        cmd1 = [
            'pactl', 'load-module', 'module-loopback',
            f'source={self.virtual_sink_name}.monitor',
            'sink=discord_combined',
            'latency_msec=1'
        ]

        # Create loopback from real mic to combined output
        cmd2 = [
            'pactl', 'load-module', 'module-loopback',
            f'source={mic_source}',
            'sink=discord_combined',
            'latency_msec=1'
        ]

        try:
            result1 = subprocess.run(cmd1, capture_output=True, text=True, check=True)
            result2 = subprocess.run(cmd2, capture_output=True, text=True, check=True)
            self.loopback_module = result1.stdout.strip()
            print(f"✓ Created audio mixing loopbacks")
            print(f"✓ Your mic + soundboard are now combined!")
            print(f"✓ Set Discord input to: Monitor of Discord_Mic+Soundboard")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating loopback: {e.stderr}")
            return False

    def list_devices(self):
        """List all audio devices"""
        print("\n=== Available Audio Devices ===")

        # List sinks (outputs)
        print("\nOutput Devices (Sinks):")
        result = subprocess.run(
            ['pactl', 'list', 'short', 'sinks'],
            capture_output=True, text=True
        )
        print(result.stdout)

        # List sources (inputs)
        print("Input Devices (Sources):")
        result = subprocess.run(
            ['pactl', 'list', 'short', 'sources'],
            capture_output=True, text=True
        )
        print(result.stdout)

    def cleanup(self):
        """Remove virtual devices"""
        print("\nCleaning up virtual devices...")

        # Unload loopback module
        if self.loopback_module:
            subprocess.run(['pactl', 'unload-module', self.loopback_module])

        # Find and unload the null sink module
        result = subprocess.run(
            ['pactl', 'list', 'short', 'modules'],
            capture_output=True, text=True
        )

        for line in result.stdout.split('\n'):
            if 'module-null-sink' in line and self.virtual_sink_name in line:
                module_id = line.split()[0]
                subprocess.run(['pactl', 'unload-module', module_id])
                print(f"✓ Removed virtual device")
                break


class Soundboard:
    """Plays audio files through the virtual device"""

    def __init__(self, virtual_device_name):
        self.device_name = virtual_device_name
        self.sounds_dir = Path("sounds")
        self.sounds_dir.mkdir(exist_ok=True)

        # Find the device ID
        self.device_id = self._find_device_id()

    def _find_device_id(self):
        """Find the sounddevice ID for our virtual device"""
        devices = sd.query_devices()

        for idx, device in enumerate(devices):
            if self.device_name in device['name']:
                print(f"Found virtual device: {device['name']} (ID: {idx})")
                return idx

        print(f"Warning: Could not find device '{self.device_name}'")
        print("Using default output device")
        return None

    def list_sounds(self):
        """List all available sound files"""
        sounds = list(self.sounds_dir.glob('*.*'))

        if not sounds:
            print(f"\nNo sound files found in {self.sounds_dir}")
            print("Add .mp3, .wav, or .ogg files to the sounds/ directory")
            return []

        print("\n=== Available Sounds ===")
        for i, sound in enumerate(sounds, 1):
            print(f"{i}. {sound.name}")

        return sounds

    def play_sound(self, filepath):
        """Play a sound file through the virtual device"""
        try:
            print(f"\n🔊 Playing: {filepath.name}")

            # Load the audio file
            data, samplerate = sf.read(filepath)

            # Play through the virtual device
            sd.play(data, samplerate, device=self.device_id)
            sd.wait()

            print("✓ Finished playing")

        except Exception as e:
            print(f"Error playing sound: {e}")

    def play_sound_by_name(self, filename):
        """Play a sound by filename"""
        filepath = self.sounds_dir / filename

        if not filepath.exists():
            print(f"Sound file not found: {filename}")
            return False

        self.play_sound(filepath)
        return True


def setup_discord_input():
    """Instructions for setting up Discord to use the virtual input"""
    print("\n" + "=" * 60)
    print("DISCORD SETUP INSTRUCTIONS")
    print("=" * 60)
    print("\n1. Open Discord → User Settings → Voice & Video")
    print("2. Under 'INPUT DEVICE', select:")
    print("   → 'Monitor of Discord_Mic+Soundboard'")
    print("\n3. Test with Input Sensitivity or Push to Talk")
    print("\n4. Now you can:")
    print("   - Talk normally (your real mic works)")
    print("   - Play soundboard sounds (mixed with your voice)")
    print("   - Everyone hears both!")
    print("=" * 60 + "\n")


def main():
    """Main soundboard application"""

    print("=" * 60)
    print("PIPEWIRE DISCORD SOUNDBOARD")
    print("=" * 60)

    # Create virtual device manager
    vdev = PipeWireVirtualDevice()

    # Setup virtual audio routing
    print("\n[1/3] Setting up virtual audio devices...")
    if not vdev.create_virtual_device():
        print("Failed to create virtual device. Is PulseAudio/PipeWire running?")
        return

    print("\n[2/3] Mixing your microphone with soundboard...")
    vdev.create_combined_source()

    # List available devices
    vdev.list_devices()

    # Show Discord setup instructions
    setup_discord_input()

    # Create soundboard
    print("[3/3] Initializing soundboard...")
    soundboard = Soundboard(vdev.virtual_sink_name)

    # List available sounds
    sounds = soundboard.list_sounds()

    if not sounds:
        print("\nAdd some sound files to the 'sounds/' directory first!")
        vdev.cleanup()
        return

    # Interactive menu
    print("\n" + "=" * 60)
    print("SOUNDBOARD READY!")
    print("=" * 60)
    print("\nCommands:")
    print("  1-9  : Play sound by number")
    print("  l    : List sounds")
    print("  d    : List audio devices")
    print("  q    : Quit")
    print("=" * 60 + "\n")

    try:
        while True:
            command = input("Command> ").strip().lower()

            if command == 'q':
                break
            elif command == 'l':
                sounds = soundboard.list_sounds()
            elif command == 'd':
                vdev.list_devices()
            elif command.isdigit():
                idx = int(command) - 1
                if 0 <= idx < len(sounds):
                    soundboard.play_sound(sounds[idx])
                else:
                    print("Invalid sound number")
            elif command:
                # Try to play by filename
                soundboard.play_sound_by_name(command)

    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        # Cleanup virtual devices
        vdev.cleanup()
        print("Goodbye!")


if __name__ == "__main__":
    import sys

    # Check dependencies
    try:
        import sounddevice
        import soundfile
    except ImportError:
        print("Missing dependencies. Install with:")
        print("  pip install sounddevice soundfile numpy")
        sys.exit(1)

    # Check if pactl is available
    import shutil

    if not shutil.which('pactl'):
        print("Error: 'pactl' not found")
        print("Install PulseAudio utilities:")
        print("  sudo apt install pulseaudio-utils")
        sys.exit(1)

    main()