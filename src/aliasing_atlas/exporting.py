"""Export helpers for configs and audio artifacts."""

from __future__ import annotations

import json
import wave
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np


def timestamp_tag(now: Optional[datetime] = None) -> str:
    """Return a compact timestamp for file naming."""
    current = now or datetime.now()
    return current.strftime("%Y%m%d_%H%M%S")


def ensure_export_dir(base_dir: str = "exports") -> Path:
    """Ensure export directory exists and return it."""
    out_dir = Path(base_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def save_config_json(path: Path, payload: Dict[str, Any]) -> Path:
    """Save config payload as pretty JSON."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    return path


def write_wav_mono16(path: Path, samples: np.ndarray, sample_rate: int) -> Path:
    """Write mono PCM16 WAV from floating point audio in [-1, 1]."""
    x = np.asarray(samples, dtype=np.float64)
    x = np.clip(x, -1.0, 1.0)
    pcm = (x * 32767.0).astype(np.int16)

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(int(sample_rate))
        wf.writeframes(pcm.tobytes())

    return path
