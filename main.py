"""
main.py — Air Piano Pro (versi final, dioptimalkan untuk 1366x768)
"""

import logging
import sys
import time
import traceback
import random

import cv2
import numpy as np

import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("air_piano")

from core.audio_engine import AudioEngine
from core.hand_tracker import HandTracker
from core.piano_renderer import PianoRenderer
from core.game_state import GameState
from core.song_loader import SongLoader


class SongModeState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.song = None
        self.started = False
        self.start_time = 0.0
        self.countdown = 3.0
        self.next_note_idx = 0
        self.active_notes = []
        self.hit_notes = []
        self.missed = 0

    def load(self, song):
        self.reset()
        self.song = song

    def start(self):
        self.started = True
        self.start_time = time.time()


class AirPianoGame:

    def __init__(self):
        log.info("🎹 Inisialisasi Air Piano Pro...")

        # ---- kamera ----
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        if not self.cap.isOpened():
            raise RuntimeError(f"Kamera index {config.CAMERA_INDEX} gagal dibuka")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)

        self.cam_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cam_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        log.info(f"✅ Kamera: {self.cam_w}x{self.cam_h}")

        # ---- render size ----
        self.w = config.RENDER_W
        self.h = config.RENDER_H
        log.info(f"✅ Render: {self.w}x{self.h}")

        # ---- area kamera (letterbox fill) ----
        self.keyboard_top = int(self.h * config.KEYBOARD_TOP_RATIO)
        self.cam_area_h = self.keyboard_top
        self.cam_area_w = self.w

        scale = max(self.cam_area_w / self.cam_w,
                    self.cam_area_h / self.cam_h)
        self.cam_scale = scale
        self.cam_scaled_w = int(self.cam_w * scale)
        self.cam_scaled_h = int(self.cam_h * scale)
        self.cam_crop_x = (self.cam_scaled_w - self.cam_area_w) // 2
        self.cam_crop_y = (self.cam_scaled_h - self.cam_area_h) // 2

        # ---- modul ----
        self.audio = AudioEngine()
        self.tracker = HandTracker()
        self.renderer = PianoRenderer(self.w, self.h)
        self.state = GameState(mode=config.MODE_FREE)
        self.song_loader = SongLoader()

        self.song_state = SongModeState()
        self.available_songs = self.song_loader.list_songs()
        self.current_song_idx = 0

        # ---- display ----
        self.fullscreen = config.FULLSCREEN
        self.show_landmarks = config.SHOW_HAND_LANDMARKS
        self.window_name = config.WINDOW_NAME

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.w, self.h)

        if config.WINDOW_START_MAXIMIZED:
            try:
                cv2.setWindowProperty(
                    self.window_name, cv2.WND_PROP_FULLSCREEN,
                    cv2.WINDOW_FULLSCREEN,
                )
                self.fullscreen = True
                log.info("✅ Fullscreen aktif")
            except Exception as e:
                log.warning(f"Fullscreen gagal: {e}")

        # ---- background cache ----
        self.bg_cache = self._make_bg_gradient()

        # ---- fps ----
        self.fps = 0.0
        self.prev_time = time.time()

        self.last_note = ""
        self.last_note_time = 0.0

        log.info("✅ Air Piano Pro siap!")

    def _make_bg_gradient(self):
        bg = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        for y in range(self.h):
            t = y / self.h
            b = int(45 - 15 * t)
            g = int(15 + 5 * t)
            r = int(50 - 20 * t)
            bg[y, :] = (b, g, r)

        random.seed(42)
        for _ in range(400):
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            b = random.randint(120, 255)
            size = 1 if random.random() < 0.85 else 2
            cv2.circle(bg, (x, y), size, (b, b, b), -1)

        return bg

    def _place_camera(self, frame, cam_frame):
        cam_frame = cv2.flip(cam_frame, 1)
        scaled = cv2.resize(cam_frame,
                            (self.cam_scaled_w, self.cam_scaled_h),
                            interpolation=cv2.INTER_LINEAR)
        x1 = self.cam_crop_x
        y1 = self.cam_crop_y
        cropped = scaled[y1:y1 + self.cam_area_h, x1:x1 + self.cam_area_w]

        if (cropped.shape[0] != self.cam_area_h or
                cropped.shape[1] != self.cam_area_w):
            cropped = cv2.resize(scaled, (self.cam_area_w, self.cam_area_h))

        frame[0:self.cam_area_h, 0:self.cam_area_w] = cropped
        return frame

    def run(self):
        try:
            while True:
                ok, cam_frame = self.cap.read()
                if not ok:
                    continue

                dt = max(time.time() - self.prev_time, 1e-5)

                self.state.update(dt)
                self.renderer.update(dt)
                if self.state.mode == config.MODE_SONG and self.song_state.started:
                    self._update_song_mode(dt)

                hands_cam = self.tracker.process(cam_frame, draw=True)

                frame = self.bg_cache.copy()
                frame = self._place_camera(frame, cam_frame)

                for hand in hands_cam:
                    self._handle_fingertip(frame, hand)

                self.renderer.draw(frame)
                self.renderer.draw_trail(frame)

                self._draw_hud(frame)
                if self.state.mode == config.MODE_SONG:
                    self._draw_song_mode(frame)
                if self.state.is_game_over():
                    self._draw_game_over(frame)
                elif self.state.paused:
                    self._draw_pause(frame)

                self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)
                self.prev_time = time.time()

                cv2.imshow(self.window_name, frame)

                key = cv2.waitKey(1) & 0xFF
                if not self._handle_key(key):
                    break

        except KeyboardInterrupt:
            log.info("Interrupted")
        except Exception as e:
            log.error(f"❌ {e}")
            log.error(traceback.format_exc())
        finally:
            self._cleanup()

    def _handle_fingertip(self, frame, hand):
        x_cam, y_cam = hand.smoothed_index_tip
        x_cam_flipped = self.cam_w - x_cam

        x_screen = int(x_cam_flipped * self.cam_scale - self.cam_crop_x)
        y_screen = int(y_cam * self.cam_scale - self.cam_crop_y)

        x_screen = max(0, min(self.w - 1, x_screen))
        y_screen = max(0, min(self.h - 1, y_screen))

        self.renderer.draw_fingertip(frame, x_screen, y_screen, hand.is_pinch)

        note = self.renderer.get_note_at(x_screen, y_screen)
        if note is None:
            return

        now = time.time()
        if not self.tracker.cooldown.can_trigger(note, now):
            return

        self.audio.play(note)
        self.renderer.trigger(note)
        self.renderer.add_trail(x_screen, y_screen)
        self.last_note = note
        self.last_note_time = now

        if self.state.mode == config.MODE_FREE:
            self.state.record_hit(note, correct=True)
        elif self.state.mode == config.MODE_SONG and self.song_state.started:
            self._check_song_hit(note, now)

    def _check_song_hit(self, note, now):
        if not self.song_state.active_notes:
            self.state.record_hit(note, correct=False)
            return

        kb_top = self.renderer.kb_top
        target_note = None
        best_dist = 999999
        for n in self.song_state.active_notes:
            if n["note"] == note and n["y"] >= kb_top - 60:
                dist = abs(n["y"] - kb_top)
                if dist < best_dist:
                    best_dist = dist
                    target_note = n

        if target_note:
            self.state.record_hit(note, correct=True)
            self.song_state.active_notes.remove(target_note)
            self.song_state.hit_notes.append({
                "note": note, "time": now, "x": target_note["x"],
            })
        else:
            self.state.record_hit(note, correct=False)

    def _update_song_mode(self, dt):
        ss = self.song_state
        song = ss.song
        if not song:
            return

        elapsed = time.time() - ss.start_time

        while ss.next_note_idx < len(song.notes):
            n = song.notes[ss.next_note_idx]
            if n.time <= elapsed + 2.0:
                x = self._note_to_x(n.note)
                ss.active_notes.append({
                    "note": n.note, "time": n.time,
                    "x": x, "y": -50,
                })
                ss.next_note_idx += 1
            else:
                break

        fall_speed = config.NOTE_FALL_SPEED
        kb_top = self.renderer.kb_top
        for n in ss.active_notes[:]:
            time_until_hit = n["time"] - elapsed
            n["y"] = kb_top - time_until_hit * fall_speed
            if n["y"] > self.renderer.kb_bottom:
                ss.active_notes.remove(n)
                ss.missed += 1
                self.state.record_miss()

        ss.hit_notes = [h for h in ss.hit_notes
                        if time.time() - h["time"] < 0.5]

        if ss.next_note_idx >= len(song.notes) and not ss.active_notes:
            log.info("🎉 Lagu selesai!")
            self.state.finish()

    def _note_to_x(self, note):
        for n, (x1, y1, x2, y2) in self.renderer.white_rects:
            if n == note:
                return (x1 + x2) // 2
        for n, (x1, y1, x2, y2) in self.renderer.black_rects:
            if n == note:
                return (x1 + x2) // 2
        return self.w // 2

    def _draw_song_mode(self, frame):
        ss = self.song_state
        if not ss.song:
            cv2.putText(frame, "SONG MODE",
                        (self.w // 2 - 150, self.h // 2 - 100),
                        cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 255, 255), 4)
            cv2.putText(frame, "Pilih lagu (1-5):",
                        (self.w // 2 - 150, self.h // 2 - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)
            for i, song_name in enumerate(self.available_songs[:5]):
                song = self.song_loader.load(song_name)
                title = song.title if song else song_name
                y = self.h // 2 + i * 40
                cv2.putText(frame, f"{i+1}. {title}",
                            (self.w // 2 - 200, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            (0, 255, 255), 2)
            cv2.putText(frame, "SPACE = mulai",
                        (self.w // 2 - 90, self.h // 2 + 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            return

        if not ss.started:
            elapsed = time.time() - ss.start_time
            remaining = ss.countdown - elapsed
            if remaining <= 0:
                ss.start()
            else:
                cv2.putText(frame, f"{int(remaining) + 1}",
                            (self.w // 2 - 40, self.h // 2),
                            cv2.FONT_HERSHEY_DUPLEX, 5.0,
                            (0, 255, 255), 6)
                cv2.putText(frame, ss.song.title,
                            (self.w // 2 - 200, self.h // 4),
                            cv2.FONT_HERSHEY_DUPLEX, 1.2,
                            (255, 255, 255), 3)
                return

        kb_top = self.renderer.kb_top
        for n in ss.active_notes:
            x = n["x"]
            y = int(n["y"])
            color = (0, 255, 255) if y < kb_top else (0, 100, 255)
            cv2.rectangle(frame,
                          (x - config.NOTE_WIDTH // 2, y - config.NOTE_HEIGHT // 2),
                          (x + config.NOTE_WIDTH // 2, y + config.NOTE_HEIGHT // 2),
                          color, -1)
            cv2.rectangle(frame,
                          (x - config.NOTE_WIDTH // 2, y - config.NOTE_HEIGHT // 2),
                          (x + config.NOTE_WIDTH // 2, y + config.NOTE_HEIGHT // 2),
                          (255, 255, 255), 2)
            cv2.putText(frame, n["note"],
                        (x - config.NOTE_WIDTH // 2 + 4, y + 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        for h in ss.hit_notes:
            age = time.time() - h["time"]
            alpha = 1.0 - age / 0.5
            if alpha > 0:
                r = int(40 * (1 - alpha)) + 5
                cv2.circle(frame, (h["x"], kb_top), r, (0, 255, 0), 3)

    def _draw_hud(self, frame):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.w, config.HUD_HEIGHT),
                      config.HUD_BG_COLOR, -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

        cv2.putText(frame, f"SCORE {self.state.stats.score}",
                    (15, 38), cv2.FONT_HERSHEY_DUPLEX, 0.9,
                    config.HUD_TEXT_COLOR, 2)

        combo_color = (0, 255, 255) if self.state.stats.combo > 0 else (120, 120, 120)
        cv2.putText(frame, f"x{self.state.stats.combo}",
                    (230, 38), cv2.FONT_HERSHEY_DUPLEX, 0.8, combo_color, 2)

        if self.state.mode == config.MODE_SONG:
            lives_str = "♥" * max(self.state.stats.lives, 0)
            cv2.putText(frame, lives_str, (320, 38),
                        cv2.FONT_HERSHEY_DUPLEX, 0.85, (0, 0, 255), 2)
            if self.song_state.song:
                title = self.song_state.song.title
                if len(title) > 25:
                    title = title[:22] + "..."
                cv2.putText(frame, title, (470, 38),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                            (200, 200, 200), 1)

        mode_color = (0, 255, 0) if self.state.mode == config.MODE_FREE else (255, 200, 0)
        mode_text = "FREE" if self.state.mode == config.MODE_FREE else "SONG"
        cv2.putText(frame, mode_text,
                    (self.w - 100, 38), cv2.FONT_HERSHEY_DUPLEX, 0.75,
                    mode_color, 2)

        if config.SHOW_FPS:
            cv2.putText(frame, f"{int(self.fps)}fps",
                        (self.w - 80, 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        (150, 150, 150), 1)

        if self.last_note and time.time() - self.last_note_time < 1.0:
            cv2.putText(frame, f"♪ {self.last_note}",
                        (15, self.h - 12),
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)

        hint = "Q=quit F=full M=mode P=pause R=restart"
        cv2.putText(frame, hint, (self.w - 360, self.h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (120, 120, 120), 1)

    def _draw_game_over(self, frame):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.w, self.h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.putText(frame, "GAME OVER",
                    (self.w // 2 - 200, self.h // 2 - 80),
                    cv2.FONT_HERSHEY_DUPLEX, 2.2, (0, 0, 255), 5)
        cv2.putText(frame, self.state.get_summary(),
                    (self.w // 2 - 320, self.h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
        cv2.putText(frame, f"Best score: {self.state.highscore.best_score}",
                    (self.w // 2 - 180, self.h // 2 + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 255), 2)
        cv2.putText(frame, "R = restart | Q = quit",
                    (self.w // 2 - 180, self.h // 2 + 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (200, 200, 200), 2)

    def _draw_pause(self, frame):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.w, self.h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        cv2.putText(frame, "PAUSED",
                    (self.w // 2 - 140, self.h // 2),
                    cv2.FONT_HERSHEY_DUPLEX, 2.5, (255, 255, 255), 4)
        cv2.putText(frame, "P = resume | R = restart | Q = quit",
                    (self.w // 2 - 280, self.h // 2 + 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)

    def _handle_key(self, key) -> bool:
        if key == 255:
            return True
        if key == config.KEY_QUIT:
            self.state.finish()
            return False
        if key == config.KEY_TOGGLE_FULLSCREEN:
            self.fullscreen = not self.fullscreen
            cv2.setWindowProperty(
                self.window_name, cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN if self.fullscreen else cv2.WINDOW_NORMAL
            )
        elif key == config.KEY_RESTART:
            self.state.reset(start=True)
            self.song_state.reset()
        elif key == config.KEY_TOGGLE_MODE:
            new_mode = (config.MODE_SONG if self.state.mode == config.MODE_FREE
                        else config.MODE_FREE)
            self.state.set_mode(new_mode)
            self.song_state.reset()
        elif key == config.KEY_PAUSE:
            self.state.toggle_pause()
        elif key == config.KEY_TOGGLE_LANDMARKS:
            self.show_landmarks = not self.show_landmarks
        elif self.state.mode == config.MODE_SONG and ord('1') <= key <= ord('5'):
            idx = key - ord('1')
            if idx < len(self.available_songs):
                self.current_song_idx = idx
                song = self.song_loader.load(self.available_songs[idx])
                if song:
                    self.song_state.load(song)
                    self.song_state.start_time = time.time()
        elif key == ord(' '):
            if self.state.mode == config.MODE_SONG:
                if self.song_state.song and not self.song_state.started:
                    self.song_state.start_time = time.time()
                elif not self.song_state.song and self.available_songs:
                    song = self.song_loader.load(self.available_songs[0])
                    if song:
                        self.song_state.load(song)
                        self.song_state.start_time = time.time()
        return True

    def _cleanup(self):
        log.info("🧹 Cleanup...")
        try:
            self.audio.cleanup()
        except Exception:
            pass
        try:
            self.tracker.cleanup()
        except Exception:
            pass
        try:
            self.cap.release()
        except Exception:
            pass
        cv2.destroyAllWindows()
        log.info("✅ Selesai.")


def main():
    try:
        game = AirPianoGame()
        game.run()
        return 0
    except RuntimeError as e:
        log.error(f"❌ {e}")
        return 1
    except Exception as e:
        log.error(f"❌ Fatal: {e}")
        log.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())