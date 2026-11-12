"""Signal bandwidth model and per-signal GUI control behaviour."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aliasing_atlas.signals import SignalRegistry


@pytest.fixture
def toolbox():
    from aliasing_atlas.app import AliasingToolbox

    tb = AliasingToolbox()
    yield tb
    plt.close(tb.fig)


def _select_wave(tb, name):
    tb.w_wave.set_active([lbl.get_text() for lbl in tb.w_wave.labels].index(name))


def test_sine_bandwidth_ignores_fourier_harmonic_count():
    assert SignalRegistry.get_max_freq("Sine", 10.0, 20.0, 0.0, n_harm=5) == 10.0
    assert SignalRegistry.get_max_freq("Sine", 10.0, 20.0, 0.3, n_harm=5) == 20.0


@pytest.mark.parametrize("wave_type", ["Square", "Sawtooth", "Triangle"])
def test_extra_tone_is_band_limited(wave_type):
    fs, n = 1000.0, 1000
    t = np.arange(n) / fs
    y = SignalRegistry.create_signal(wave_type, t, 0.0, 30.0, 0.5, 0.0, 1)
    mags = np.abs(np.fft.rfft(y)) / n * 2
    freqs = np.fft.rfftfreq(n, 1 / fs)
    assert mags[freqs == 30.0][0] == pytest.approx(0.5, abs=1e-9)
    assert np.all(mags[freqs > 30.0] < 1e-9)
    assert SignalRegistry.get_max_freq(wave_type, 5.0, 30.0, 0.5, 1) == 30.0


@pytest.mark.parametrize(
    "wave_type, n_harm_active, a_harm_active",
    [("Sine", False, True), ("Square", True, True), ("AM", False, True), ("FM", False, True), ("Chirp", False, False)],
)
def test_only_unused_controls_are_dimmed(toolbox, wave_type, n_harm_active, a_harm_active):
    _select_wave(toolbox, wave_type)
    assert toolbox.s_f_harm.label.get_alpha() == 1.0
    assert (toolbox.s_n_harm.label.get_alpha() == 1.0) is n_harm_active
    assert (toolbox.s_f_harm_amp.label.get_alpha() == 1.0) is a_harm_active


def test_modulated_labels(toolbox):
    _select_wave(toolbox, "FM")
    assert toolbox.s_f_harm.label.get_text() == "Message Freq (Hz)"
    assert toolbox.s_f_harm_amp.label.get_text() == "Mod Index (beta)"


def test_reset_restores_first_preset_and_selector(toolbox):
    toolbox._preset_callback("Aliasing")
    toolbox.w_preset.set_active(2)
    toolbox.s_f_samp.set_val(400.0)

    toolbox._reset_callback(None)

    assert toolbox.w_preset.value_selected == "Safe Nyquist"
    assert toolbox.s_f_samp.val == 100.0
    assert "ALIASING" not in toolbox.status_text.get_text()
