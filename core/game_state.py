"""
core/game_state.py — State game Air Piano Pro
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict

import config

log = logging.getLogger("air_piano.state")

HIGHSCORE_FILE = config.BASE_DIR / "highscore.json"


@dataclass
class Stats:
    score: int = 0
    combo: int = 0
    max_combo: int = 0
    lives: int = config.STARTING_LIVES
    correct_hits: int = 0
    wrong_hits: int = 0
    missed_notes: int = 0
    start_time: float = 0.0
    last_hit_time: float = 0.0

    @property
    def total_hits(self) -> int:
        return self.correct_hits + self.wrong_hits

    @property
    def accuracy(self) -> float:
        if self.total_hits == 0:
            return 0.0
        return self.correct_hits / self.total_hits * 100.0

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        return time.time() - self.start_time


@dataclass
class HighScore:
    best_score: int = 0
    best_combo: int = 0
    best_accuracy: float = 0.0
    total_plays: int = 0
    last_played: str = ""

    @classmethod
    def load(cls) -> "HighScore":
        if not HIGHSCORE_FILE.exists():
            return cls()
        try:
            data = json.loads(HIGHSCORE_FILE.read_text(encoding="utf-8"))
            return cls(**{k: data.get(k, v) for k, v in cls().__dict__.items()})
        except Exception as e:
            log.warning(f"Gagal load highscore: {e}")
            return cls()

    def save(self):
        try:
            HIGHSCORE_FILE.write_text(
                json.dumps(asdict(self), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            log.warning(f"Gagal save highscore: {e}")

    def update(self, stats: Stats, mode: str):
        changed = False
        if stats.score > self.best_score:
            self.best_score = stats.score
            changed = True
        if stats.max_combo > self.best_combo:
            self.best_combo = stats.max_combo
            changed = True
        if stats.accuracy > self.best_accuracy:
            self.best_accuracy = stats.accuracy
            changed = True
        self.total_plays += 1
        self.last_played = time.strftime("%Y-%m-%d %H:%M:%S")
        self.save()
        return changed


class GameState:

    def __init__(self, mode: str = config.DEFAULT_MODE):
        self.mode = mode
        self.stats = Stats()
        self.highscore = HighScore.load()
        self.paused = False
        self.game_over = False
        self.reset(start=True)
        log.info(f"🎮 GameState init (mode: {mode})")

    def reset(self, start: bool = True):
        self.stats = Stats()
        self.stats.start_time = time.time() if start else 0.0
        self.stats.last_hit_time = time.time()
        self.paused = False
        self.game_over = False

    def set_mode(self, mode: str):
        if mode not in (config.MODE_FREE, config.MODE_SONG):
            return
        self.mode = mode
        self.reset(start=True)

    def record_hit(self, note: str, correct: bool = True):
        if self.game_over or self.paused:
            return
        now = time.time()
        self.stats.last_hit_time = now

        if correct:
            self.stats.correct_hits += 1
            self.stats.combo += 1
            self.stats.max_combo = max(self.stats.max_combo, self.stats.combo)
            bonus = int(config.SCORE_PER_CORRECT_NOTE *
                        config.SCORE_COMBO_MULTIPLIER * self.stats.combo)
            self.stats.score += config.SCORE_PER_CORRECT_NOTE + bonus
        else:
            self.stats.wrong_hits += 1
            self.stats.combo = 0
            if self.mode == config.MODE_SONG:
                self.stats.lives -= 1
                self._check_game_over()

    def record_miss(self):
        if self.game_over or self.paused:
            return
        self.stats.missed_notes += 1
        self.stats.combo = 0
        if self.mode == config.MODE_SONG:
            self.stats.lives -= 1
            self._check_game_over()

    def update(self, dt: float):
        if self.game_over or self.paused:
            return
        now = time.time()
        if self.stats.combo > 0:
            if now - self.stats.last_hit_time > config.COMBO_TIMEOUT:
                self.stats.combo = 0

    def _check_game_over(self):
        if self.stats.lives <= 0:
            self.game_over = True
            self.highscore.update(self.stats, self.mode)
            log.info(f"💀 GAME OVER! Score: {self.stats.score}")

    def is_game_over(self) -> bool:
        return self.game_over

    def finish(self):
        if not self.game_over and self.stats.score > 0:
            self.highscore.update(self.stats, self.mode)
        self.game_over = True

    def toggle_pause(self):
        self.paused = not self.paused

    def get_summary(self) -> str:
        s = self.stats
        return (f"Score: {s.score} | Combo: {s.max_combo} | "
                f"Benar: {s.correct_hits} | Salah: {s.wrong_hits} | "
                f"Akurasi: {s.accuracy:.1f}%")