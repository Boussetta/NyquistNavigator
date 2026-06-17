import sys
from pathlib import Path

import numpy as np

# Ensure src-layout imports work without requiring editable install.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aliasing_atlas import dsp


def test_quantize_signal_two_bits_known_levels():
    y = np.array([-1.0, -0.4, 0.1, 0.8, 1.0])
    q = dsp.quantize_signal(y, bits=2)
    expected = np.array([-1.0, -1.0 / 3.0, 1.0 / 3.0, 1.0, 1.0])
    np.testing.assert_allclose(q, expected, atol=1e-12)


def test_folded_alias_frequency_and_flag():
    max_freq = 60.0
    f_samp = 80.0
    assert dsp.is_aliased(max_freq, f_samp)
    assert dsp.folded_alias_frequency(max_freq, f_samp) == 20.0


def test_fft_reconstruction_beats_foh_for_periodic_sine():
    f_sig = 5.0
    f_samp = 80.0
    duration = 1.0

    t_samp = np.linspace(0.0, duration, int(duration * f_samp), endpoint=False)
    y_samp = np.sin(2 * np.pi * f_sig * t_samp)

    t_out = np.linspace(0.0, duration, 2000, endpoint=False)
    y_true = np.sin(2 * np.pi * f_sig * t_out)

    y_fft = dsp.reconstruct_fft(y_samp, len(t_out))
    y_foh = dsp.reconstruct_foh(t_out, t_samp, y_samp)

    rmse_fft, _ = dsp.reconstruction_metrics(y_true, y_fft)
    rmse_foh, _ = dsp.reconstruction_metrics(y_true, y_foh)

    assert rmse_fft < rmse_foh


def test_apply_ideal_aaf_reduces_out_of_band_energy():
    fs_cont = 2000.0
    f_samp = 40.0
    duration = 1.0
    t_cont = np.linspace(0.0, duration, int(fs_cont * duration), endpoint=False)

    y_cont = np.sin(2 * np.pi * 10.0 * t_cont) + 0.5 * np.sin(2 * np.pi * 120.0 * t_cont)
    y_filt, _, _, _ = dsp.apply_anti_alias_filter(y_cont, t_cont, f_samp, "Ideal")

    n = len(y_cont)
    freqs = np.fft.rfftfreq(n, 1.0 / fs_cont)
    mag_before = np.abs(np.fft.rfft(y_cont))
    mag_after = np.abs(np.fft.rfft(y_filt))

    idx_120 = np.argmin(np.abs(freqs - 120.0))
    assert mag_after[idx_120] < 0.05 * mag_before[idx_120]
