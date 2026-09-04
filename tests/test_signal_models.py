import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aliasing_atlas.signals import SignalRegistry


@pytest.mark.parametrize("wave_type", ["Sine", "Square", "Sawtooth", "Triangle", "AM", "FM", "Chirp"])
def test_registered_signal_models_return_finite_arrays(wave_type):
    t = np.linspace(0.0, 1.0, 1001)
    y = SignalRegistry.create_signal(wave_type, t, 5.0, 2.0, 0.5, 0.25, 5)

    assert y.shape == t.shape
    assert np.isfinite(y).all()
    assert np.max(np.abs(y)) > 0.0


def test_am_bandwidth_prediction_includes_upper_sideband():
    assert SignalRegistry.get_max_freq("AM", 25.0, 3.0, 0.7) == 28.0


def test_fm_bandwidth_prediction_uses_carson_rule():
    assert SignalRegistry.get_max_freq("FM", 25.0, 3.0, 4.0) == 40.0


def test_square_bandwidth_expands_with_harmonics():
    assert SignalRegistry.get_max_freq("Square", 5.0, 0.0, 0.0, n_harm=4) == 35.0
