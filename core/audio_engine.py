"""
core/audio_engine.py — Mesin audio Air Piano Pro
"""

import logging
import wave
import numpy as np
import pygame

import config

log = logging.getLogger("air_piano.audio")


class AudioEngine:

    def __init__(self):
        log.info("🔊 Inisialisasi AudioEngine...")
        try:
            pygame.mixer.pre_init(
                frequency=config.SAMPLE_RATE,
                size=-16,
                channels=config.AUDIO_CHANNELS,
                buffer=config.AUDIO_BUFFER,
            )
            pygame.mixer.init()
            log.info(f"   pygame.mixer: {pygame.mixer.get_init()}")
        except pygame.error as e:
            log.error(f"   ❌ pygame.mixer gagal: {e}")
            raise

        pygame.mixer.set_num_channels(32)

        self.sounds: dict = {}
        self._load_all_notes()
        log.info(f"✅ AudioEngine siap: {len(self.sounds)} nada")

    def _load_all_notes(self):
        for note in config.NOTE_NAMES:
            wav_path = config.SOUNDS_DIR / f"{note}.wav"

            if config.USE_REAL_PIANO_SAMPLES and wav_path.exists():
                try:
                    self.sounds[note] = pygame.mixer.Sound(str(wav_path))
                    self.sounds[note].set_volume(config.AUDIO_VOLUME)
                    continue
                except pygame.error as e:
                    log.warning(f"   ⚠️  Gagal load {wav_path.name}: {e}")

            if not wav_path.exists():
                self._generate_and_save(note, wav_path)

            try:
                self.sounds[note] = pygame.mixer.Sound(str(wav_path))
                self.sounds[note].set_volume(config.AUDIO_VOLUME)
            except pygame.error as e:
                log.error(f"   ❌ Gagal load {note}: {e}")

    def _generate_and_save(self, note: str, path):
        freq = config.NOTE_FREQS[note]
        duration = config.TONE_DURATION
        sr = config.SAMPLE_RATE
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)

        wave_data = np.sin(2 * np.pi * freq * t)
        if config.TONE_HARMONICS:
            wave_data += 0.35 * np.sin(2 * np.pi * freq * 2 * t)
            wave_data += 0.18 * np.sin(2 * np.pi * freq * 3 * t)
            wave_data += 0.08 * np.sin(2 * np.pi * freq * 4 * t)

        attack = int(0.008 * sr)
        decay = int(0.05 * sr)
        sustain_level = 0.7
        release = int(0.15 * sr)

        env = np.ones_like(t)
        if attack > 0:
            env[:attack] = np.linspace(0, 1, attack)
        if decay > 0:
            env[attack:attack + decay] = np.linspace(1, sustain_level, decay)
        env[attack + decay:-release] = sustain_level
        if release > 0:
            env[-release:] = np.linspace(sustain_level, 0, release)

        wave_data = wave_data * env * config.AUDIO_VOLUME
        max_val = np.max(np.abs(wave_data))
        if max_val > 0:
            wave_data = wave_data / max_val * 0.9

        audio_int16 = (wave_data * 32767).astype(np.int16)
        if config.AUDIO_CHANNELS == 2:
            audio_int16 = np.column_stack([audio_int16, audio_int16])

        with wave.open(str(path), 'wb') as wf:
            wf.setnchannels(config.AUDIO_CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(audio_int16.tobytes())

    def play(self, note: str) -> bool:
        if note not in self.sounds:
            return False
        try:
            self.sounds[note].play()
            return True
        except pygame.error as e:
            log.error(f"   Gagal play {note}: {e}")
            return False

    def stop_all(self):
        try:
            pygame.mixer.stop()
        except pygame.error:
            pass

    def set_volume(self, volume: float):
        volume = max(0.0, min(1.0, volume))
        for snd in self.sounds.values():
            snd.set_volume(volume)

    def cleanup(self):
        self.stop_all()
        try:
            pygame.mixer.quit()
        except pygame.error:
            pass
        log.info("🔊 AudioEngine cleanup")

    def __len__(self):
        return len(self.sounds)