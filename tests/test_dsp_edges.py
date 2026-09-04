import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aliasing_atlas import dsp


@pytest.mark.parametrize("max_freq, f_samp, expected", [(10.0, 20.0, False), (10.0, 19.99, True)])
def test_nyquist_boundary_is_explicit(max_freq, f_samp, expected):
    assert dsp.is_aliased(max_freq, f_samp) is expected


def test_reconstruct_fft_supports_even_and_odd_input_lengths():
    for input_size in (8, 9):
        samples = np.sin(2 * np.pi * np.arange(input_size) / input_size)
        reconstructed = dsp.reconstruct_fft(samples, num_output_points=64)
        assert reconstructed.shape == (64,)
        assert np.isfinite(reconstructed).all()


def test_sampling_keeps_at_least_two_samples_for_short_duration():
    t = np.linspace(0.0, 1.0, 100)
    y = np.sin(2 * np.pi * t)
    t_samp, y_samp = dsp.sample_signal(t, y, f_samp=10.0, duration=0.01)
    assert len(t_samp) == 2
    assert len(y_samp) == 2


def test_butter_filter_falls_back_without_scipy():
    t = np.linspace(0.0, 1.0, 1000)
    y = np.sin(2 * np.pi * 10.0 * t)
    filtered, coefficients_b, coefficients_a, filtered_fs = dsp.apply_anti_alias_filter(
        y, t, f_samp=40.0, aaf_type="Butter", scipy_signal=None
    )
    np.testing.assert_array_equal(filtered, y)
    assert coefficients_b is None
    assert coefficients_a is None
    assert filtered_fs is None


def test_reconstruction_metrics_returns_zero_error_for_identical_signals():
    y = np.array([0.0, 0.5, -0.5])
    rmse, snr = dsp.reconstruction_metrics(y, y)
    assert rmse == 0.0
    assert snr == 100.0
