import json
import sys
from pathlib import Path

import numpy as np

# Ensure src-layout imports work without requiring editable install.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aliasing_atlas.exporting import ensure_export_dir, save_config_json, timestamp_tag, write_wav_mono16


def test_timestamp_tag_format():
    tag = timestamp_tag()
    assert len(tag) == 15
    assert tag[8] == "_"


def test_save_config_json_roundtrip(tmp_path):
    payload = {"f_sig": 10.0, "wave_type": "Sine"}
    path = tmp_path / "cfg.json"
    save_config_json(path, payload)
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == payload


def test_write_wav_mono16_creates_file(tmp_path):
    sr = 8000
    t = np.linspace(0.0, 0.1, int(sr * 0.1), endpoint=False)
    y = 0.5 * np.sin(2 * np.pi * 440.0 * t)
    path = tmp_path / "tone.wav"
    write_wav_mono16(path, y, sr)
    assert path.exists()
    assert path.stat().st_size > 44


def test_ensure_export_dir_creates(tmp_path):
    target = tmp_path / "exports"
    out = ensure_export_dir(str(target))
    assert out.exists()
    assert out.is_dir()
