"""Notebook-facing behaviour: output panel, downloads, layout, and teaching windows."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aliasing_atlas import app as app_module
from aliasing_atlas import dsp


class FakeOutput:
    """Minimal stand-in for ipywidgets.Output that records displayed objects."""

    def __init__(self):
        self.shown = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def notebook_toolbox(monkeypatch, tmp_path):
    pytest.importorskip("IPython")
    out = FakeOutput()
    monkeypatch.setattr(app_module, "display", lambda obj: out.shown.append(obj))
    monkeypatch.setattr(app_module, "clear_output", lambda wait=False: out.shown.clear())
    monkeypatch.chdir(tmp_path)
    tb = app_module.AliasingToolbox(output=out)
    yield tb, out
    plt.close(tb.fig)


def test_play_audio_shows_browser_player_in_output(notebook_toolbox):
    tb, out = notebook_toolbox
    tb._play_audio_callback(None)
    assert len(out.shown) == 1
    assert type(out.shown[0]).__name__ == "Audio"
    assert "shown below" in tb.status_text.get_text()


@pytest.mark.parametrize("callback, suffix", [("_export_wav_callback", ".wav"), ("_export_config_callback", ".json")])
def test_exports_offer_download_link(notebook_toolbox, callback, suffix):
    tb, out = notebook_toolbox
    getattr(tb, callback)(None)
    html = out.shown[-1].data
    assert 'download="aliasing_' in html and suffix in html and "base64," in html
    assert "download link below" in tb.status_text.get_text()


def test_default_figure_fits_notebook_width():
    tb = app_module.AliasingToolbox()
    width_px = tb.fig.get_size_inches()[0] * 100
    plt.close(tb.fig)
    assert width_px <= 1100


def test_legend_lists_only_visible_curves():
    tb = app_module.AliasingToolbox()
    labels = [t.get_text() for t in tb.ax_time.get_legend().get_texts()]
    plt.close(tb.fig)
    assert "FFT Reconstruction" in labels
    assert "FOH Reconstruction" not in labels and "AAF Filtered" not in labels


def test_window_covers_alias_and_modulation():
    assert dsp.compute_observation_window("Sine", 10.0, 20.0, 0.0, f_samp=15.0, alias_freq=5.0) >= 3 / 5.0
    assert dsp.compute_observation_window("AM", 25.0, 3.0, 0.7) == pytest.approx(1.0)
    assert dsp.compute_observation_window("Chirp", 10.0, 3.0, 0.7) == pytest.approx(0.3)


@pytest.mark.parametrize(
    "preset, snr_min, aliased",
    [("Safe Nyquist", 90, False), ("Near Nyquist", 90, False), ("Aliasing", None, True), ("AM Sidebands", 60, False)],
)
def test_presets_demonstrate_their_lesson(preset, snr_min, aliased):
    tb = app_module.AliasingToolbox()
    tb._preset_callback(preset)
    status = tb.status_text.get_text()
    plt.close(tb.fig)
    assert ("ALIASING DETECTED" in status) is aliased
    if snr_min is not None:
        snr = float(status.split("SNR: ")[1].split(" dB")[0])
        assert snr > snr_min


def test_aliasing_preset_spectrum_peaks_at_predicted_alias():
    tb = app_module.AliasingToolbox()
    tb._preset_callback("Aliasing")
    freqs, mags = tb.line_spec.get_data()
    plt.close(tb.fig)
    assert np.asarray(freqs)[np.argmax(mags)] == pytest.approx(5.0)


def test_ideal_aaf_reports_filtered_not_aliased():
    tb = app_module.AliasingToolbox()
    tb._set_radio_value(tb.w_wave, "Square")
    tb.s_n_harm.set_val(15)
    tb._set_radio_value(tb.w_aaf, "Ideal")
    status = tb.status_text.get_text()
    plt.close(tb.fig)
    assert "ALIASING DETECTED" not in status and "AAF removed" in status


def test_down_chirp_sweeps_downward():
    from aliasing_atlas.signals import SignalRegistry

    t = np.arange(4000) / 4000.0
    y = SignalRegistry.create_signal("Chirp", t, 40.0, 5.0, 0.0, 0.0)
    first, last = y[:1000], y[-1000:]
    crossings = lambda seg: np.count_nonzero(np.diff(np.sign(seg)))  # noqa: E731
    assert crossings(first) > 2 * crossings(last)
