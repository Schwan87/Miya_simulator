"""
game/audio.py - Modular audio manager with automatic procedural sound synthesis.
"""

import os
import math
import struct
import wave
import pygame

class SoundSynthesizer:
    """Generates procedural sound effects using Python standard library wave/math."""
    
    @staticmethod
    def create_wav(filepath, sample_rate, samples):
        """Write raw floating point samples (-1.0 to 1.0) as 16-bit PCM WAV."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            raw_data = bytearray()
            for s in samples:
                # Clamp sample
                clamped = max(-1.0, min(1.0, s))
                int_val = int(clamped * 32767.0)
                raw_data.extend(struct.pack('<h', int_val))
            wav_file.writeframes(raw_data)

    @classmethod
    def generate_all_defaults(cls, sound_dir):
        """Generates shoot, hit, bullseye, miss, click if not present."""
        os.makedirs(sound_dir, exist_ok=True)
        sr = 44100

        shoot_path = os.path.join(sound_dir, "shoot.wav")
        if not os.path.exists(shoot_path):
            # Bow release snap: frequency drop from 600Hz to 120Hz with quick decay
            duration = 0.22
            total_samples = int(sr * duration)
            samples = []
            for i in range(total_samples):
                t = i / sr
                env = math.exp(-14.0 * t)
                freq = 650.0 * math.exp(-12.0 * t) + 120.0
                val = math.sin(2.0 * math.pi * freq * t) * env
                # add slight mechanical click at beginning
                if t < 0.015:
                    click = math.sin(2.0 * math.pi * 1200.0 * t) * (1.0 - t / 0.015)
                    val = 0.7 * val + 0.3 * click
                samples.append(val * 0.75)
            cls.create_wav(shoot_path, sr, samples)

        hit_path = os.path.join(sound_dir, "hit.wav")
        if not os.path.exists(hit_path):
            # Target impact thud: punchy low-mid thwack
            duration = 0.28
            total_samples = int(sr * duration)
            samples = []
            for i in range(total_samples):
                t = i / sr
                env = math.exp(-15.0 * t)
                freq = 240.0 * math.exp(-20.0 * t) + 85.0
                # pseudo noise component for wood crack
                noise = ((math.sin(i * 123.456) * 43758.5453) % 1.0) * 2.0 - 1.0
                val = (0.7 * math.sin(2.0 * math.pi * freq * t) + 0.3 * noise * math.exp(-35.0 * t)) * env
                samples.append(val * 0.85)
            cls.create_wav(hit_path, sr, samples)

        bullseye_path = os.path.join(sound_dir, "bullseye.wav")
        if not os.path.exists(bullseye_path):
            # Bullseye chime: impact + dual harmonic sparkling bell
            duration = 0.65
            total_samples = int(sr * duration)
            samples = []
            for i in range(total_samples):
                t = i / sr
                env = math.exp(-6.0 * t)
                bell1 = math.sin(2.0 * math.pi * 880.0 * t) # A5
                bell2 = math.sin(2.0 * math.pi * 1760.0 * t) * 0.5 # A6
                bell3 = math.sin(2.0 * math.pi * 2640.0 * t) * 0.25 # E7
                val = (bell1 + bell2 + bell3) * env
                if t < 0.08:
                    thud = math.sin(2.0 * math.pi * 180.0 * t) * math.exp(-25.0 * t)
                    val = 0.6 * val + 0.4 * thud
                samples.append(val * 0.8)
            cls.create_wav(bullseye_path, sr, samples)

        miss_path = os.path.join(sound_dir, "miss.wav")
        if not os.path.exists(miss_path):
            # Miss swoosh sound: subtle filtered breeze
            duration = 0.35
            total_samples = int(sr * duration)
            samples = []
            for i in range(total_samples):
                t = i / sr
                # smooth envelope
                env = math.sin(math.pi * (t / duration)) ** 1.8
                freq = 320.0 - 180.0 * (t / duration)
                val = math.sin(2.0 * math.pi * freq * t) * env
                samples.append(val * 0.55)
            cls.create_wav(miss_path, sr, samples)

        click_path = os.path.join(sound_dir, "click.wav")
        if not os.path.exists(click_path):
            # UI button click: short subtle tap
            duration = 0.06
            total_samples = int(sr * duration)
            samples = []
            for i in range(total_samples):
                t = i / sr
                env = math.exp(-60.0 * t)
                val = math.sin(2.0 * math.pi * 1400.0 * t) * env
                samples.append(val * 0.5)
            cls.create_wav(click_path, sr, samples)


class AudioManager:
    """Safely manages and plays game sound effects."""

    def __init__(self, sound_dir=None):
        self.enabled = False
        self.sounds = {}
        
        if sound_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            sound_dir = os.path.join(base_dir, "assets", "sounds")
        
        self.sound_dir = sound_dir
        
        # Initialize mixer if not already initialized
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.enabled = True
        except Exception as e:
            print(f"[AudioManager] Mixer initialization failed: {e}")
            self.enabled = False

        if self.enabled:
            # Generate default sounds if needed
            try:
                SoundSynthesizer.generate_all_defaults(self.sound_dir)
            except Exception as e:
                print(f"[AudioManager] Procedural synthesis warning: {e}")

            # Load sounds safely
            sound_files = {
                "shoot": "shoot.wav",
                "hit": "hit.wav",
                "bullseye": "bullseye.wav",
                "miss": "miss.wav",
                "click": "click.wav"
            }
            for key, filename in sound_files.items():
                filepath = os.path.join(self.sound_dir, filename)
                if os.path.exists(filepath):
                    try:
                        self.sounds[key] = pygame.mixer.Sound(filepath)
                        self.sounds[key].set_volume(0.65)
                    except Exception as e:
                        print(f"[AudioManager] Could not load sound {filename}: {e}")

    def play(self, name):
        """Play a sound effect by name without crashing."""
        if not self.enabled:
            return
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass
