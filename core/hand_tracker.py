"""
core/hand_tracker.py — Deteksi tangan MediaPipe
"""

import logging
from dataclasses import dataclass, field
from collections import deque
import numpy as np
import cv2
import mediapipe as mp

import config

log = logging.getLogger("air_piano.hand")


@dataclass
class HandInfo:
    index_tip: tuple = (0, 0)
    thumb_tip: tuple = (0, 0)
    wrist: tuple = (0, 0)
    palm_center: tuple = (0, 0)
    is_pinch: bool = False
    hand_label: str = "Unknown"
    landmarks: list = field(default_factory=list)
    smoothed_index_tip: tuple = (0, 0)


class PositionSmoother:
    def __init__(self, window: int = 5):
        self.window = window
        self.buffers: dict = {}

    def smooth(self, hand_id: int, pos: tuple) -> tuple:
        if hand_id not in self.buffers:
            self.buffers[hand_id] = deque(maxlen=self.window)
        self.buffers[hand_id].append(pos)
        if not self.buffers[hand_id]:
            return pos
        arr = np.array(self.buffers[hand_id], dtype=float)
        return int(arr[:, 0].mean()), int(arr[:, 1].mean())

    def reset(self):
        self.buffers.clear()


class CooldownManager:
    def __init__(self, cooldown_sec: float):
        self.cooldown_sec = cooldown_sec
        self.last_time: dict = {}

    def can_trigger(self, key: str, now: float) -> bool:
        last = self.last_time.get(key, 0.0)
        if now - last >= self.cooldown_sec:
            self.last_time[key] = now
            return True
        return False

    def reset(self):
        self.last_time.clear()


class HandTracker:

    THUMB_TIP = 4
    INDEX_TIP = 8
    WRIST = 0
    PALM_IDS = (0, 5, 9, 13, 17)

    def __init__(self):
        log.info("✋ Inisialisasi HandTracker...")

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.MAX_NUM_HANDS,
            model_complexity=config.MODEL_COMPLEXITY,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )

        self.smoother = PositionSmoother(window=5)
        self.cooldown = CooldownManager(config.KEY_COOLDOWN)

        log.info(f"✅ HandTracker siap (max {config.MAX_NUM_HANDS} tangan)")

    def process(self, frame_bgr: np.ndarray, draw: bool = True) -> list:
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        rgb.flags.writeable = True

        hands_info = []
        if not results.multi_hand_landmarks:
            return hands_info

        for idx, hand_lms in enumerate(results.multi_hand_landmarks):
            hand_label = "Unknown"
            if results.multi_handedness and idx < len(results.multi_handedness):
                hand_label = results.multi_handedness[idx].classification[0].label

            landmarks_px = [(int(lm.x * w), int(lm.y * h))
                            for lm in hand_lms.landmark]

            index_tip = landmarks_px[self.INDEX_TIP]
            thumb_tip = landmarks_px[self.THUMB_TIP]
            wrist = landmarks_px[self.WRIST]

            palm_xs = [landmarks_px[i][0] for i in self.PALM_IDS]
            palm_ys = [landmarks_px[i][1] for i in self.PALM_IDS]
            palm_center = (int(np.mean(palm_xs)), int(np.mean(palm_ys)))

            dist = np.hypot(index_tip[0] - thumb_tip[0],
                            index_tip[1] - thumb_tip[1])
            is_pinch = dist < config.PINCH_THRESHOLD

            smoothed = self.smoother.smooth(idx, index_tip)

            info = HandInfo(
                index_tip=index_tip,
                thumb_tip=thumb_tip,
                wrist=wrist,
                palm_center=palm_center,
                is_pinch=is_pinch,
                hand_label=hand_label,
                landmarks=landmarks_px,
                smoothed_index_tip=smoothed,
            )
            hands_info.append(info)

            if draw:
                self._draw_hand(frame_bgr, hand_lms, info)

        return hands_info

    def _draw_hand(self, frame, hand_lms, info):
        self.mp_draw.draw_landmarks(
            frame, hand_lms, self.mp_hands.HAND_CONNECTIONS,
            self.mp_styles.get_default_hand_landmarks_style(),
            self.mp_styles.get_default_hand_connections_style(),
        )
        sx, sy = info.smoothed_index_tip
        color = (0, 255, 255) if not info.is_pinch else (0, 0, 255)
        cv2.circle(frame, (sx, sy), 10, color, -1)
        cv2.circle(frame, (sx, sy), 14, (255, 255, 255), 2)
        if info.is_pinch:
            cv2.line(frame, info.thumb_tip, info.index_tip, (0, 0, 255), 2)

    def cleanup(self):
        try:
            self.hands.close()
        except Exception:
            pass
        self.smoother.reset()
        self.cooldown.reset()
        log.info("✋ HandTracker cleanup")