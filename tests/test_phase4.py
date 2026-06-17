import sys
from pathlib import Path

import numpy as np

# Ensure src-layout imports work without requiring editable install.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aliasing_atlas.learning import build_learning_hint
from aliasing_atlas.signals import SignalRegistry


def test_chirp_registration_and_shape():
    t = np.linspace(0.0, 1.0, 1000)
    y = SignalRegistry.create_signal("Chirp", t, 5.0, 25.0, 0.0, 0.0)
    assert y.shape == t.shape
    assert np.isfinite(y).all()


def test_chirp_max_freq_prediction():
    max_freq = SignalRegistry.get_max_freq("Chirp", f_sig=8.0, f_harm=30.0, a_harm=0.0, n_harm=1)
    assert max_freq == 30.0


def test_learning_hint_aliasing_message():
    hint = build_learning_hint(
        wave_type="Sine",
        aliased=True,
        max_freq=10.0,
        f_samp=15.0,
        recon_type="FFT",
        aaf_type="None",
        bits=16,
    )
    assert "Aliasing is active" in hint


def test_learning_hint_low_bits_message():
    hint = build_learning_hint(
        wave_type="Sine",
        aliased=False,
        max_freq=10.0,
        f_samp=50.0,
        recon_type="FFT",
        aaf_type="None",
        bits=3,
    )
    assert "quantization is coarse" in hint
