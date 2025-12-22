#!/usr/bin/env python3
"""
PipeWire Python Examples with Audio Playback
Demonstrates control AND audio generation
"""

# Example 1: Using pulsectl (PipeWire control)
# Install: pip install pulsectl

import pulsectl
import time


def list_audio_devices():
    """List all audio sinks and sources"""
    with pulsectl.Pulse('device-lister') as pulse:
        print("=== Audio Output Devices (Sinks) ===")
        for sink in pulse.sink_list():
            print(f"ID: {sink.index}")
            print(f"Name: {sink.name}")
            print(f"Description: {sink.description}")
            print(f"Volume: {sink.volume.value_flat * 100:.0f}%")
            print(f"Muted: {sink.mute}")
            print("-" * 40)


def control_volume(sink_index=0, volume_percent=50):
    """Set volume for a specific sink"""
    with pulsectl.Pulse('volume-controller') as pulse:
        sinks = pulse.sink_list()
        if sink_index < len(sinks):
            sink = sinks[sink_index]
            pulse.volume_set_all_chans(sink, volume_percent / 100.0)
            print(f"Volume set to {volume_percent}% for {sink.description}")
        else:
            print(f"Sink index {sink_index} not found")


def unmute_default_sink():
    """Unmute the default audio output"""
    with pulsectl.Pulse('unmuter') as pulse:
        sink = pulse.get_sink_by_name(pulse.server_info().default_sink_name)
        if sink.mute:
            pulse.mute(sink, 0)
            print(f"Unmuted: {sink.description}")
        else:
            print(f"Already unmuted: {sink.description}")


# Example 2: Generate and play audio
# Install: pip install sounddevice numpy

def play_beep_tone(frequency=440, duration=1.0, volume=0.3):
    """
    Play a beep tone through PipeWire
    This will actually produce sound you can hear!
    """
    try:
        import sounddevice as sd
        import numpy as np

        print(f"Playing {frequency}Hz tone for {duration} seconds...")

        # Generate a sine wave
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        wave = volume * np.sin(2 * np.pi * frequency * t)

        # Play the sound
        sd.play(wave, sample_rate)
        sd.wait()  # Wait until sound finishes

        print("Done playing!")

    except ImportError:
        print("sounddevice not installed. Run: pip install sounddevice numpy")
    except Exception as e:
        print(f"Error playing audio: {e}")


def play_musical_scale():
    """Play a musical scale (C major)"""
    try:
        import sounddevice as sd
        import numpy as np

        # C major scale frequencies
        notes = {
            'C': 261.63,
            'D': 293.66,
            'E': 329.63,
            'F': 349.23,
            'G': 392.00,
            'A': 440.00,
            'B': 493.88,
            'C2': 523.25
        }

        print("Playing C major scale...")
        sample_rate = 44100
        duration = 0.5

        for note_name, freq in notes.items():
            print(f"  Playing {note_name} ({freq:.2f}Hz)")
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = 0.3 * np.sin(2 * np.pi * freq * t)

            # Add fade out to avoid clicks
            fade = np.linspace(1, 0, int(sample_rate * 0.1))
            wave[-len(fade):] *= fade

            sd.play(wave, sample_rate)
            sd.wait()
            time.sleep(0.1)

        print("Scale complete!")

    except ImportError:
        print("sounddevice not installed. Run: pip install sounddevice numpy")


def play_wav_file(filepath):
    """Play a WAV file through PipeWire"""
    try:
        import sounddevice as sd
        import soundfile as sf

        print(f"Playing: {filepath}")
        data, sample_rate = sf.read(filepath)
        sd.play(data, sample_rate)
        sd.wait()
        print("Playback finished!")

    except ImportError:
        print("Missing libraries. Run: pip install sounddevice soundfile")
    except FileNotFoundError:
        print(f"File not found: {filepath}")


def record_audio(duration=3, filename="recording.wav"):
    """Record audio from default microphone"""
    try:
        import sounddevice as sd
        import soundfile as sf

        print(f"Recording for {duration} seconds...")
        sample_rate = 44100

        recording = sd.rec(int(duration * sample_rate),
                           samplerate=sample_rate,
                           channels=2)
        sd.wait()

        sf.write(filename, recording, sample_rate)
        print(f"Saved to: {filename}")

    except ImportError:
        print("Missing libraries. Run: pip install sounddevice soundfile")


def test_audio_system():
    """Test if audio system is working"""
    try:
        import sounddevice as sd

        print("=== Audio System Info ===")
        print(f"Default input device: {sd.query_devices(kind='input')['name']}")
        print(f"Default output device: {sd.query_devices(kind='output')['name']}")
        print("\nAll devices:")
        print(sd.query_devices())

    except ImportError:
        print("sounddevice not installed. Run: pip install sounddevice")


if __name__ == "__main__":
    print("PipeWire Python Examples with Audio Playback\n")

    try:
        # Check audio system
        print("1. Checking audio system:")
        test_audio_system()

        print("\n2. Listing PipeWire devices:")
        list_audio_devices()

        print("\n3. Ensuring audio is unmuted:")
        unmute_default_sink()

        print("\n4. Setting volume to 50%:")
        control_volume(0, 50)

        print("\n5. Playing test tone (you should hear this!):")
        play_beep_tone(440, 1.0, 0.3)

        print("\n6. Playing musical scale:")
        play_musical_scale()

        # Uncomment to test recording
        # print("\n7. Recording audio:")
        # record_audio(3, "test_recording.wav")

    except pulsectl.PulseError as e:
        print(f"PulseAudio/PipeWire error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have the required packages:")
        print("  pip install pulsectl sounddevice numpy soundfile")