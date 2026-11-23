"""
config.py — Konfigurasi terpusat Air Piano Pro
Dioptimalkan untuk layar 1366x768 (auto-detect).
"""

from pathlib import Path

# ============ PATH ============
BASE_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = BASE_DIR / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
SONGS_DIR = ASSETS_DIR / "songs"
LOGS_DIR = BASE_DIR / "logs"

for _d in (ASSETS_DIR, SOUNDS_DIR, SONGS_DIR, LOGS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ============ AUTO-DETECT LAYAR ============
def _detect_screen_size():
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        root.destroy()
        return w, h
    except Exception:
        return 1280, 720

SCREEN_W, SCREEN_H = _detect_screen_size()

# ============ RENDER ============
RENDER_W = SCREEN_W
RENDER_H = SCREEN_H

# ============ KAMERA ============
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 60

# ============ WINDOW ============
WINDOW_NAME = "Air Piano Pro"
FULLSCREEN = False
SHOW_FPS = True
SHOW_HAND_LANDMARKS = False
WINDOW_START_MAXIMIZED = True

# ============ MEDIAPIPE ============
MAX_NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.6
MODEL_COMPLEXITY = 1

# ============ NADA ============
NOTE_NAMES = [
    "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
    "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
]

NOTE_FREQS = {
    "C4": 261.63, "C#4": 277.18, "D4": 293.66, "D#4": 311.13,
    "E4": 329.63, "F4": 349.23, "F#4": 369.99, "G4": 392.00,
    "G#4": 415.30, "A4": 440.00, "A#4": 466.16, "B4": 493.88,
    "C5": 523.25, "C#5": 554.37, "D5": 587.33, "D#5": 622.25,
    "E5": 659.25, "F5": 698.46, "F#5": 739.99, "G5": 783.99,
    "G#5": 830.61, "A5": 880.00, "A#5": 932.33, "B5": 987.77,
}

WHITE_KEYS = ["C4", "D4", "E4", "F4", "G4", "A4", "B4",
              "C5", "D5", "E5", "F5", "G5", "A5", "B5"]
BLACK_KEYS = ["C#4", "D#4", "F#4", "G#4", "A#4",
              "C#5", "D#5", "F#5", "G#5", "A#5"]

# ============ LAYOUT PIANO (1366x768) ============
KEYBOARD_TOP_RATIO = 0.65        # keyboard mulai di 65% tinggi (499px)
KEYBOARD_HEIGHT_RATIO = 0.35     # tinggi keyboard 35% (269px)
BLACK_KEY_HEIGHT_RATIO = 0.62    # tuts hitam 62% tinggi tuts putih
BLACK_KEY_WIDTH_RATIO = 0.58     # tuts hitam 58% lebar tuts putih

# ============ AUDIO ============
SAMPLE_RATE = 44100
AUDIO_CHANNELS = 1
AUDIO_BUFFER = 512
AUDIO_VOLUME = 0.35
TONE_DURATION = 0.55
TONE_HARMONICS = True
KEY_COOLDOWN = 0.12
USE_REAL_PIANO_SAMPLES = False

# ============ VISUAL EFFECTS ============
KEY_GLOW_DECAY = 0.06
TRAIL_LIFE = 0.50
TRAIL_MAX_POINTS = 50
FINGERTIP_RADIUS = 12
PINCH_THRESHOLD = 35

# ============ GAME ============
MODE_FREE = "free"
MODE_SONG = "song"
MODE_RECORD = "record"
DEFAULT_MODE = MODE_FREE

SCORE_PER_CORRECT_NOTE = 10
SCORE_COMBO_MULTIPLIER = 0.1
COMBO_TIMEOUT = 1.5
STARTING_LIVES = 5

# ============ SONG MODE ============
NOTE_FALL_SPEED = 380
NOTE_HIT_WINDOW = 0.18
NOTE_SPAWN_TOP_OFFSET = 100
NOTE_WIDTH = 50
NOTE_HEIGHT = 26

# ============ HUD (1366x768) ============
HUD_HEIGHT = 55
HUD_BG_COLOR = (0, 0, 0)
HUD_TEXT_COLOR = (255, 255, 255)
HUD_ACCENT_COLOR = (0, 255, 255)

WHITE_KEY_COLOR = (245, 245, 245)
WHITE_KEY_BORDER = (80, 80, 80)
BLACK_KEY_COLOR = (30, 30, 30)
BLACK_KEY_BORDER = (0, 0, 0)
KEY_ACTIVE_COLOR = (0, 200, 255)
KEY_GLOW_COLOR = (255, 100, 50)

# ============ FONT ============
FONT_SCALE_HUD = 0.8
FONT_SCALE_KEY_LABEL = 0.5
FONT_THICKNESS_HUD = 2
FONT_THICKNESS_KEY_LABEL = 1

# ============ LOGGING ============
LOG_FILE = LOGS_DIR / "air_piano.log"
LOG_LEVEL = "INFO"

# ============ SHORTCUTS ============
KEY_QUIT = ord('q')
KEY_TOGGLE_FULLSCREEN = ord('f')
KEY_TOGGLE_MODE = ord('m')
KEY_RESTART = ord('r')
KEY_PAUSE = ord('p')
KEY_TOGGLE_LANDMARKS = ord('l')

# ============ VALIDASI ============
assert len(NOTE_NAMES) == 24
assert len(WHITE_KEYS) == 14
assert len(BLACK_KEYS) == 10
assert all(n in NOTE_FREQS for n in NOTE_NAMES)
assert 0.0 < KEYBOARD_TOP_RATIO < 1.0
assert 0.0 < KEYBOARD_HEIGHT_RATIO <= 1.0

print(f"[config] ✅ Loaded")
print(f"[config]    Layar: {SCREEN_W}x{SCREEN_H}")
print(f"[config]    Keyboard: {int(SCREEN_H * KEYBOARD_TOP_RATIO)}-{SCREEN_H} "
      f"({int(SCREEN_H * KEYBOARD_HEIGHT_RATIO)}px)")
print(f"[config]    Nada: {len(NOTE_NAMES)} | Putih: {len(WHITE_KEYS)} | Hitam: {len(BLACK_KEYS)}")