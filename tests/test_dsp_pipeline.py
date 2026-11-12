"""End-to-end accuracy checks for the sampling -> quantization -> reconstruction pipeline."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aliasing_atlas import dsp

pytest.importorskip("scipy")
from scipy import signal as sp_signal  # noqa: E402


def _pipeline(window_type="None", aaf_type="None", f_sig=10.0, f_samp=100.0, bits=16):
    t_cont, _, upsample = dsp.build_sampling_grid(f_samp, 3.0 / f_sig, 1000)
    y_cont = np.sin(2 * np.pi * f_sig * t_cont)
    y_filt, _, _, _ = dsp.apply_anti_alias_filter(y_cont, t_cont, f_samp, aaf_type, scipy_signal=sp_signal)
    y_samp = dsp.quantize_signal(y_filt[::upsample], bits)
    y_recon = dsp.reconstruct_fft(y_samp, len(t_cont))
    freqs, mags, _ = dsp.compute_spectrum(y_samp, f_samp, window_type)
    return y_cont, y_recon, freqs, mags


@pytest.mark.parametrize("window_type", ["None", "Hamming", "Hann"])
@pytest.mark.parametrize("aaf_type", ["None", "Ideal", "Butter"])
def test_oversampled_sine_reconstructs_near_quantization_limit(window_type, aaf_type):
    y_cont, y_recon, _, _ = _pipeline(window_type=window_type, aaf_type=aaf_type)
    _, snr = dsp.reconstruction_metrics(y_cont, y_recon)
    assert snr > 80.0


@pytest.mark.parametrize("window_type", ["None", "Hamming", "Hann"])
def test_spectrum_reports_sine_amplitude(window_type):
    _, _, freqs, mags = _pipeline(window_type=window_type)
    peak = int(np.argmax(mags))
    assert freqs[peak] == pytest.approx(10.0)
    assert mags[peak] == pytest.approx(1.0, abs=0.01)


def test_sampling_grid_contains_sample_instants():
    t_cont, n_samples, upsample = dsp.build_sampling_grid(97.0, 0.3, 1000)
    assert len(t_cont) == n_samples * upsample
    np.testing.assert_allclose(t_cont[::upsample], np.arange(n_samples) / 97.0, atol=1e-12)


def test_quantizer_clips_to_full_scale():
    q = dsp.quantize_signal(np.array([-3.0, 1.8, 0.0]), bits=3)
    assert q.min() == -1.0 and q.max() == 1.0
    q_wide = dsp.quantize_signal(np.array([-2.0, 2.0]), bits=8, full_scale=2.0)
    np.testing.assert_allclose(q_wide, [-2.0, 2.0])


def test_butterworth_has_no_group_delay():
    f_samp = 100.0
    t_cont, _, _ = dsp.build_sampling_grid(f_samp, 0.3, 1000)
    y = np.sin(2 * np.pi * 10.0 * t_cont)
    y_filt, sos, _, fs_cont = dsp.apply_anti_alias_filter(y, t_cont, f_samp, "Butter", scipy_signal=sp_signal)
    assert sos is not None and fs_cont is not None
    np.testing.assert_allclose(y_filt, y, atol=1e-3)


def test_metrics_handle_silent_reference_without_warning():
    with np.errstate(all="raise"):
        _, snr = dsp.reconstruction_metrics(np.zeros(4), np.ones(4))
    assert snr == float("-inf")


def test_gui_reconstruction_ignores_window_choice():
    from aliasing_atlas.app import AliasingToolbox
    import matplotlib.pyplot as plt

    toolbox = AliasingToolbox()
    args = dict(f_sig=10.0, f_harm=20.0, a_harm=0.0, phase=0.0, f_samp=100.0, bits=16,
                wave_type="Sine", aaf_type="None", n_harm=1)
    plain = toolbox._build_signal_data(window_type="None", **args)
    hann = toolbox._build_signal_data(window_type="Hann", **args)
    plt.close(toolbox.fig)

    np.testing.assert_allclose(plain["y_recon_fft"], hann["y_recon_fft"])
    _, snr = dsp.reconstruction_metrics(plain["y_cont"], plain["y_recon_fft"])
    assert snr > 80.0
