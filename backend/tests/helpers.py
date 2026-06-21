"""Shared test helpers for building synthetic MediaPipe landmark sets."""
from typing import Dict, Tuple


def make_landmarks(overrides: Dict[int, Tuple[float, float, float]] = None):
    """Build a full 33-point landmark list (zeros by default).

    `overrides` maps a landmark index -> (x, y, z).
    """
    overrides = overrides or {}
    landmarks = []
    for i in range(33):
        x, y, z = overrides.get(i, (0.0, 0.0, 0.0))
        landmarks.append({
            "index": i,
            "name": f"landmark_{i}",
            "x": float(x),
            "y": float(y),
            "z": float(z),
            "confidence": 1.0,
        })
    return landmarks
