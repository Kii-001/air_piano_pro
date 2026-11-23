"""
core/song_loader.py — Load lagu untuk Song Mode
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path

import config

log = logging.getLogger("air_piano.song")


@dataclass
class Note:
    note: str
    time: float
    duration: float = 0.5

    def __post_init__(self):
        if self.note not in config.NOTE_FREQS:
            raise ValueError(f"Nada tidak valid: {self.note}")
        if self.time < 0:
            raise ValueError(f"Time negatif: {self.time}")
        if self.duration <= 0:
            raise ValueError(f"Duration harus > 0: {self.duration}")


@dataclass
class Song:
    title: str
    composer: str = "Unknown"
    bpm: int = 100
    difficulty: str = "easy"
    notes: list = field(default_factory=list)

    @property
    def duration(self) -> float:
        if not self.notes:
            return 0.0
        return max(n.time + n.duration for n in self.notes)

    @property
    def note_count(self) -> int:
        return len(self.notes)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "composer": self.composer,
            "bpm": self.bpm,
            "difficulty": self.difficulty,
            "notes": [asdict(n) for n in self.notes],
        }


def _make_builtin_songs() -> dict:
    def seq_to_notes(seq, start=0.0):
        notes = []
        t = start
        for note, dur in seq:
            notes.append(Note(note=note, time=round(t, 3), duration=dur))
            t += dur
        return notes

    songs = {}

    twinkle_seq = [
        ("C4", 0.5), ("C4", 0.5), ("G4", 0.5), ("G4", 0.5),
        ("A4", 0.5), ("A4", 0.5), ("G4", 1.0),
        ("F4", 0.5), ("F4", 0.5), ("E4", 0.5), ("E4", 0.5),
        ("D4", 0.5), ("D4", 0.5), ("C4", 1.0),
        ("G4", 0.5), ("G4", 0.5), ("F4", 0.5), ("F4", 0.5),
        ("E4", 0.5), ("E4", 0.5), ("D4", 1.0),
        ("G4", 0.5), ("G4", 0.5), ("F4", 0.5), ("F4", 0.5),
        ("E4", 0.5), ("E4", 0.5), ("D4", 1.0),
        ("C4", 0.5), ("C4", 0.5), ("G4", 0.5), ("G4", 0.5),
        ("A4", 0.5), ("A4", 0.5), ("G4", 1.0),
        ("F4", 0.5), ("F4", 0.5), ("E4", 0.5), ("E4", 0.5),
        ("D4", 0.5), ("D4", 0.5), ("C4", 1.0),
    ]
    songs["twinkle"] = Song(
        title="Twinkle Twinkle Little Star",
        composer="Traditional", bpm=100, difficulty="easy",
        notes=seq_to_notes(twinkle_seq),
    )

    ode_seq = [
        ("E4", 0.4), ("E4", 0.4), ("F4", 0.4), ("G4", 0.4),
        ("G4", 0.4), ("F4", 0.4), ("E4", 0.4), ("D4", 0.4),
        ("C4", 0.4), ("C4", 0.4), ("D4", 0.4), ("E4", 0.4),
        ("E4", 0.6), ("D4", 0.2), ("D4", 0.8),
        ("E4", 0.4), ("E4", 0.4), ("F4", 0.4), ("G4", 0.4),
        ("G4", 0.4), ("F4", 0.4), ("E4", 0.4), ("D4", 0.4),
        ("C4", 0.4), ("C4", 0.4), ("D4", 0.4), ("E4", 0.4),
        ("D4", 0.6), ("C4", 0.2), ("C4", 0.8),
    ]
    songs["ode_to_joy"] = Song(
        title="Ode to Joy", composer="Ludwig van Beethoven",
        bpm=120, difficulty="easy", notes=seq_to_notes(ode_seq),
    )

    hb_seq = [
        ("C4", 0.4), ("C4", 0.2), ("D4", 0.6), ("C4", 0.6),
        ("F4", 0.6), ("E4", 1.0),
        ("C4", 0.4), ("C4", 0.2), ("D4", 0.6), ("C4", 0.6),
        ("G4", 0.6), ("F4", 1.0),
        ("C4", 0.4), ("C4", 0.2), ("C5", 0.6), ("A4", 0.6),
        ("F4", 0.6), ("E4", 0.6), ("D4", 0.6),
        ("A#4", 0.4), ("A#4", 0.2), ("A4", 0.6), ("F4", 0.6),
        ("G4", 0.6), ("F4", 1.0),
    ]
    songs["happy_birthday"] = Song(
        title="Happy Birthday", composer="Traditional",
        bpm=90, difficulty="medium", notes=seq_to_notes(hb_seq),
    )

    mary_seq = [
        ("E4", 0.4), ("D4", 0.4), ("C4", 0.4), ("D4", 0.4),
        ("E4", 0.4), ("E4", 0.4), ("E4", 0.8),
        ("D4", 0.4), ("D4", 0.4), ("D4", 0.8),
        ("E4", 0.4), ("G4", 0.4), ("G4", 0.8),
        ("E4", 0.4), ("D4", 0.4), ("C4", 0.4), ("D4", 0.4),
        ("E4", 0.4), ("E4", 0.4), ("E4", 0.4), ("E4", 0.4),
        ("D4", 0.4), ("D4", 0.4), ("E4", 0.4), ("D4", 0.4),
        ("C4", 1.0),
    ]
    songs["mary_lamb"] = Song(
        title="Mary Had a Little Lamb", composer="Traditional",
        bpm=100, difficulty="easy", notes=seq_to_notes(mary_seq),
    )

    jingle_seq = [
        ("E4", 0.4), ("E4", 0.4), ("E4", 0.8),
        ("E4", 0.4), ("E4", 0.4), ("E4", 0.8),
        ("E4", 0.4), ("G4", 0.4), ("C4", 0.4), ("D4", 0.4),
        ("E4", 1.0),
        ("F4", 0.4), ("F4", 0.4), ("F4", 0.4), ("F4", 0.4),
        ("F4", 0.4), ("E4", 0.4), ("E4", 0.4), ("E4", 0.4),
        ("E4", 0.4), ("D4", 0.4), ("D4", 0.4), ("E4", 0.4),
        ("D4", 0.8), ("G4", 0.8),
    ]
    songs["jingle_bells"] = Song(
        title="Jingle Bells", composer="James Lord Pierpont",
        bpm=110, difficulty="medium", notes=seq_to_notes(jingle_seq),
    )

    return songs


class SongLoader:

    def __init__(self, songs_dir: Path = config.SONGS_DIR):
        self.songs_dir = songs_dir
        self.songs_dir.mkdir(parents=True, exist_ok=True)
        self.builtin = _make_builtin_songs()
        self._cache: dict = {}
        log.info(f"🎼 SongLoader: {len(self.builtin)} lagu bawaan")
        self._export_builtin_if_missing()

    def _export_builtin_if_missing(self):
        for key, song in self.builtin.items():
            path = self.songs_dir / f"{key}.json"
            if not path.exists():
                try:
                    path.write_text(
                        json.dumps(song.to_dict(), indent=2,
                                   ensure_ascii=False),
                        encoding="utf-8",
                    )
                except Exception as e:
                    log.warning(f"Gagal export {key}: {e}")

    def list_songs(self) -> list:
        songs = set(self.builtin.keys())
        for f in self.songs_dir.glob("*.json"):
            songs.add(f.stem)
        return sorted(songs)

    def load(self, name: str):
        name = name.lower().replace(".json", "")
        if name in self._cache:
            return self._cache[name]

        path = self.songs_dir / f"{name}.json"
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                notes = [Note(**n) for n in data.get("notes", [])]
                song = Song(
                    title=data.get("title", name),
                    composer=data.get("composer", "Unknown"),
                    bpm=data.get("bpm", 100),
                    difficulty=data.get("difficulty", "easy"),
                    notes=notes,
                )
                self._cache[name] = song
                return song
            except Exception as e:
                log.warning(f"Gagal load {path.name}: {e}")

        if name in self.builtin:
            self._cache[name] = self.builtin[name]
            return self.builtin[name]

        return None

    def get_info(self, name: str) -> str:
        song = self.load(name)
        if not song:
            return f"Lagu '{name}' tidak ditemukan"
        return (f"{song.title} | {song.composer} | "
                f"{song.note_count} notes | {song.duration:.1f}s")