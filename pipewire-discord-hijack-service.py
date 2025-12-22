#!/usr/bin/env python3
"""
PipeWire Microphone Stream Hijacker
Intercepts your existing mic and injects soundboard audio into it.

No Discord configuration needed - it hijacks whatever mic Discord is using!
"""

import subprocess
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
import sys
import threading
import queue


class MicrophoneHijacker:
    """
    Hijacks your microphone stream and adds soundboard audio on top.
    Discord uses your mic normally, but sounds get injected into the stream.
    """

    def __init__(self):
        self.original_default_source = None
        self.virtual_mic_name = "hijacked_microphone"
        self.soundboard_sink = "soundboard_injection"
        self.modules_loaded = []
        self.sounds_dir = Path("sounds")
        self.sounds_dir.mkdir(exist_ok=True)

        # For real-time audio mixing
        self.audio_queue = queue.Queue()
        self.is_running = False

    def get_current_mic(self):
        """Get the currently active microphone"""
        result = subprocess.run(
            ['pactl', 'get-default-source'],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    def setup_hijack(self):
        """
        Create a pass-through mic that sits between real mic and Discord.

        Flow: Real Mic -> Virtual Mic (with soundboard injection) -> Discord
        """

        print("\n[1/3] Identifying your current microphone...")
        self.original_default_source = self.get_current_mic()
        print(f"  Current mic: {self.original_default_source}")

        print("\n[2/3] Creating soundboard injection point...")
        # Create null sink for soundboard
        cmd = [
            'pactl', 'load-module', 'module-null-sink',
            f'sink_name={self.soundboard_sink}',
            'sink_properties=device.description="Soundboard_Injection"'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self.modules_loaded.append(result.stdout.strip())
            print(f"  ✓ Created injection point")

        print("\n[3/3] Hijacking microphone stream...")
        # Create a null sink that will act as our mixer
        cmd = [
            'pactl', 'load-module', 'module-null-sink',
            f'sink_name=mic_mixer',
            'sink_properties=device.description="Microphone_Mixer"'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self.modules_loaded.append(result.stdout.strip())

        # Route original mic into mixer
        cmd = [
            'pactl', 'load-module', 'module-loopback',
            f'source={self.original_default_source}',
            'sink=mic_mixer',
            'latency_msec=1',
            'source_dont_move=true',
            'sink_dont_move=true'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self.modules_loaded.append(result.stdout.strip())

        # Route soundboard into mixer
        cmd = [
            'pactl', 'load-module', 'module-loopback',
            f'source={self.soundboard_sink}.monitor',
            'sink=mic_mixer',
            'latency_msec=1',
            'source_dont_move=true',
            'sink_dont_move=true'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self.modules_loaded.append(result.stdout.strip())

        # Create the hijacked microphone from mixer output
        cmd = [
            'pactl', 'load-module', 'module-remap-source',
            f'source_name={self.virtual_mic_name}',
            'master=mic_mixer.monitor',
            'source_properties=device.description="Microphone"'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self.modules_loaded.append(result.stdout.strip())
            print(f"  ✓ Created hijacked microphone")

        # Set as default (this is what Discord will pick up)
        subprocess.run(['pactl', 'set-default-source', self.virtual_mic_name])

        print("\n" + "=" * 70)
        print("✓ MICROPHONE HIJACKED!")
        print("=" * 70)
        print("\nWhat happened:")
        print(f"  • Your real mic: {self.original_default_source}")
        print(f"  • Hijacked mic: {self.virtual_mic_name} (now system default)")
        print(f"  • Soundboard injection: {self.soundboard_sink}")
        print("\nHow it works:")
        print("  Real Mic ──┐")
        print("             ├──> Hijacked Mic ──> Discord")
        print("  Soundboard ┘")
        print("\n  Discord thinks it's using your normal mic!")
        print("  But we're secretly mixing in soundboard audio.")
        print("=" * 70 + "\n")

    def get_soundboard_device_id(self):
        """Find device ID for soundboard output"""
        devices = sd.query_devices()
        for idx, device in enumerate(devices):
            if self.soundboard_sink in device['name']:
                return idx
        return None

    def play_sound(self, filepath, volume=1.0):
        """Inject sound into the mic stream"""
        device_id = self.get_soundboard_device_id()

        if device_id is None:
            print("Error: Soundboard device not found")
            return False

        try:
            print(f"🔊 Injecting: {filepath.name}")
            data, samplerate = sf.read(filepath)

            # Apply volume
            if volume != 1.0:
                data = data * volume

            # Play through soundboard sink (which mixes into mic)
            sd.play(data, samplerate, device=device_id)
            sd.wait()
            print("  ✓ Injection complete")
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def list_sounds(self):
        """List available sounds"""
        sounds = list(self.sounds_dir.glob('*.*'))

        if not sounds:
            print(f"\n📁 No sounds in {self.sounds_dir}/")
            print("   Add .mp3, .wav, or .ogg files")
            return []

        print("\n=== 🎵 Available Sounds ===")
        for i, sound in enumerate(sounds, 1):
            size = sound.stat().st_size / 1024
            print(f"  {i}. {sound.name} ({size:.1f} KB)")
        print("=" * 40)

        return sounds

    def test_mic_levels(self):
        """Show current mic input levels"""
        print("\n=== Testing Microphone Levels ===")
        print("Speak into your microphone...")
        print("(Ctrl+C to stop)\n")

        try:
            device_id = None
            devices = sd.query_devices()
            for idx, device in enumerate(devices):
                if self.virtual_mic_name in device['name']:
                    device_id = idx
                    break

            if device_id is None:
                print("Could not find hijacked microphone")
                return

            def audio_callback(indata, frames, time, status):
                volume_norm = np.linalg.norm(indata) * 10
                bars = int(volume_norm)
                print(f"\rLevel: {'█' * bars}{' ' * (50 - bars)}", end='')

            with sd.InputStream(device=device_id, callback=audio_callback):
                sd.sleep(10000)

        except KeyboardInterrupt:
            print("\n")

    def restore(self):
        """Restore original microphone configuration"""
        print("\n" + "=" * 70)
        print("Restoring original configuration...")
        print("=" * 70)

        # Restore original default source
        if self.original_default_source:
            print(f"\nRestoring: {self.original_default_source}")
            subprocess.run(['pactl', 'set-default-source', self.original_default_source])

        # Unload all modules
        print("Removing virtual devices...")
        for module_id in reversed(self.modules_loaded):
            subprocess.run(['pactl', 'unload-module', module_id],
                           capture_output=True, stderr=subprocess.DEVNULL)

        print("✓ Original configuration restored!")
        print("✓ Microphone un-hijacked")


def check_requirements():
    """Check system requirements"""
    import shutil

    if not shutil.which('pactl'):
        print("Error: 'pactl' not found")
        print("Install: sudo apt install pulseaudio-utils")
        return False

    try:
        import sounddevice
        import soundfile
        import numpy
    except ImportError:
        print("Error: Missing Python packages")
        print("Install: pip install sounddevice soundfile numpy")
        return False

    return True


def print_discord_instructions():
    """Show Discord usage instructions"""
    print("\n" + "=" * 70)
    print("DISCORD USAGE")
    print("=" * 70)
    print("\nOption A: Restart Discord (Recommended)")
    print("  1. Close Discord completely")
    print("  2. Run this soundboard script")
    print("  3. Start Discord")
    print("  4. Discord will automatically use the hijacked mic")
    print("\nOption B: Keep Discord Running")
    print("  1. In Discord: Settings → Voice & Video")
    print("  2. Change input device to anything else, then back to 'Default'")
    print("  3. Or select 'Microphone' explicitly")
    print("\nThen:")
    print("  • Join a voice channel")
    print("  • Speak normally (your voice works)")
    print("  • Play soundboard sounds (they mix in automatically)")
    print("=" * 70 + "\n")


def main():
    """Main application"""

    if not check_requirements():
        sys.exit(1)

    print("=" * 70)
    print("PIPEWIRE MICROPHONE HIJACKER")
    print("Invisible soundboard injection")
    print("=" * 70)

    hijacker = MicrophoneHijacker()

    try:
        # Setup hijacking
        hijacker.setup_hijack()

        # Show Discord instructions
        print_discord_instructions()

        # List sounds
        sounds = hijacker.list_sounds()

        if not sounds:
            print("💡 Tip: Add sound files to 'sounds/' directory first")

        # Interactive menu
        print("\n" + "=" * 70)
        print("SOUNDBOARD ACTIVE")
        print("=" * 70)
        print("\nCommands:")
        print("  1-9  : Play sound by number")
        print("  l    : List sounds")
        print("  t    : Test microphone levels")
        print("  v N  : Set volume (0-100), e.g., 'v 50'")
        print("  h    : Show Discord instructions again")
        print("  q    : Quit and restore")
        print("=" * 70 + "\n")

        volume = 1.0

        while True:
            try:
                cmd = input("🎛️  > ").strip().lower()

                if cmd == 'q':
                    break

                elif cmd == 'l':
                    sounds = hijacker.list_sounds()

                elif cmd == 't':
                    hijacker.test_mic_levels()

                elif cmd == 'h':
                    print_discord_instructions()

                elif cmd.startswith('v '):
                    try:
                        vol_str = cmd.split()[1]
                        vol_percent = int(vol_str)
                        if 0 <= vol_percent <= 100:
                            volume = vol_percent / 100
                            print(f"✓ Volume set to {vol_percent}%")
                        else:
                            print("Volume must be 0-100")
                    except (IndexError, ValueError):
                        print("Usage: v 50  (sets volume to 50%)")

                elif cmd.isdigit():
                    idx = int(cmd) - 1
                    if 0 <= idx < len(sounds):
                        hijacker.play_sound(sounds[idx], volume)
                    else:
                        print("Invalid sound number")

                elif cmd:
                    # Try to play by filename
                    filepath = hijacker.sounds_dir / cmd
                    if filepath.exists():
                        hijacker.play_sound(filepath, volume)
                    else:
                        print(f"Sound not found: {cmd}")

            except EOFError:
                break

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted!")

    finally:
        hijacker.restore()
        print("\nGoodbye! 👋")


if __name__ == "__main__":
    main()