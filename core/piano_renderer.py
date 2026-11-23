"""
core/piano_renderer.py — Render tuts piano + efek
"""

import logging
import time
import cv2
import numpy as np

import config

log = logging.getLogger("air_piano.renderer")


class PianoRenderer:

    def __init__(self, width: int, height: int):
        self.w = width
        self.h = height

        self.kb_top = int(height * config.KEYBOARD_TOP_RATIO)
        self.kb_height = int(height * config.KEYBOARD_HEIGHT_RATIO)
        self.kb_bottom = min(self.kb_top + self.kb_height, height)

        self.white_key_count = len(config.WHITE_KEYS)
        self.white_key_width = width / self.white_key_count

        self.black_key_width = self.white_key_width * config.BLACK_KEY_WIDTH_RATIO
        self.black_key_height = self.kb_height * config.BLACK_KEY_HEIGHT_RATIO

        self.white_rects = []
        self.black_rects = []
        self._compute_rects()

        self.glow = {note: 0.0 for note in config.NOTE_NAMES}
        self.trail = []

        log.info(f"🎨 PianoRenderer: {len(self.white_rects)} putih + "
                 f"{len(self.black_rects)} hitam @ {self.kb_top}-{self.kb_bottom} "
                 f"({width}x{height})")

    def _compute_rects(self):
        for i, note in enumerate(config.WHITE_KEYS):
            x1 = i * self.white_key_width
            x2 = x1 + self.white_key_width
            self.white_rects.append((note, (int(x1), self.kb_top,
                                            int(x2), self.kb_bottom)))

        black_positions = [
            (0, "C#4"), (1, "D#4"), (3, "F#4"), (4, "G#4"), (5, "A#4"),
            (7, "C#5"), (8, "D#5"), (10, "F#5"), (11, "G#5"), (12, "A#5"),
        ]
        for white_idx, note in black_positions:
            x_center = (white_idx + 1) * self.white_key_width
            x1 = x_center - self.black_key_width / 2
            x2 = x1 + self.black_key_width
            y1 = self.kb_top
            y2 = self.kb_top + self.black_key_height
            self.black_rects.append((note, (int(x1), int(y1),
                                            int(x2), int(y2))))

    def get_note_at(self, x: int, y: int):
        if y < self.kb_top or y > self.kb_bottom:
            return None
        for note, (x1, y1, x2, y2) in self.black_rects:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return note
        for note, (x1, y1, x2, y2) in self.white_rects:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return note
        return None

    def trigger(self, note: str):
        if note in self.glow:
            self.glow[note] = 1.0

    def update(self, dt: float):
        decay = config.KEY_GLOW_DECAY * (dt * 60)
        for note in self.glow:
            if self.glow[note] > 0:
                self.glow[note] = max(0.0, self.glow[note] - decay)

        now = time.time()
        self.trail = [(x, y, t) for (x, y, t) in self.trail
                      if now - t < config.TRAIL_LIFE]
        if len(self.trail) > config.TRAIL_MAX_POINTS:
            self.trail = self.trail[-config.TRAIL_MAX_POINTS:]

    def add_trail(self, x: int, y: int):
        self.trail.append((x, y, time.time()))

    def draw(self, frame: np.ndarray):
        # tuts putih dengan gradient
        for note, (x1, y1, x2, y2) in self.white_rects:
            glow = self.glow.get(note, 0.0)

            for y in range(y1, y2):
                t = (y - y1) / max(1, (y2 - y1))
                base = int(250 - 40 * t)
                if glow > 0.01:
                    r = int(base * (1 - glow) + 100 * glow)
                    g = int(base * (1 - glow) + 220 * glow)
                    b = int(base * (1 - glow) + 255 * glow)
                    cv2.line(frame, (x1, y), (x2, y), (b, g, r), 1)
                else:
                    cv2.line(frame, (x1, y), (x2, y), (base, base, base), 1)

            cv2.rectangle(frame, (x1, y1), (x2, y2),
                          config.WHITE_KEY_BORDER, 2)

            if "#" not in note:
                cv2.putText(frame, note, (x1 + 5, y2 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            config.FONT_SCALE_KEY_LABEL,
                            (60, 60, 60),
                            config.FONT_THICKNESS_KEY_LABEL)

        # tuts hitam dengan bayangan
        for note, (x1, y1, x2, y2) in self.black_rects:
            glow = self.glow.get(note, 0.0)

            cv2.rectangle(frame, (x1 + 3, y1 + 3), (x2 + 3, y2 + 3),
                          (10, 10, 10), -1)

            for y in range(y1, y2):
                t = (y - y1) / max(1, (y2 - y1))
                base = int(20 + 30 * t)
                if glow > 0.01:
                    r = int(base * (1 - glow) + 50 * glow)
                    g = int(base * (1 - glow) + 200 * glow)
                    b = int(base * (1 - glow) + 255 * glow)
                    cv2.line(frame, (x1, y), (x2, y), (b, g, r), 1)
                else:
                    cv2.line(frame, (x1, y), (x2, y), (base, base, base), 1)

            cv2.rectangle(frame, (x1, y1), (x2, y2),
                          config.BLACK_KEY_BORDER, 2)

    def draw_trail(self, frame: np.ndarray):
        if not self.trail:
            return
        now = time.time()
        for (x, y, t) in self.trail:
            age = (now - t) / config.TRAIL_LIFE
            if age >= 1.0:
                continue
            alpha = 1.0 - age
            radius = int(14 * alpha) + 2
            r = int(255 * alpha)
            g = int(200 * alpha)
            b = 50
            cv2.circle(frame, (x, y), radius, (b, g, r), -1)

    def draw_fingertip(self, frame, x, y, is_pinch=False, label=""):
        color = (0, 0, 255) if is_pinch else (0, 255, 255)
        cv2.circle(frame, (x, y), config.FINGERTIP_RADIUS, color, -1)
        cv2.circle(frame, (x, y), config.FINGERTIP_RADIUS + 4,
                   (255, 255, 255), 2)
        if label:
            cv2.putText(frame, label, (x + 15, y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)