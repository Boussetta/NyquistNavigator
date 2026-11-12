"""Pure DSP helpers for sampling, reconstruction, and analysis.

This module provides testable, reusable digital signal processing functions that are
decoupled from the UI. All functions are pure (no side effects) and accept NumPy arrays
or scalar values as inputs.

Core Capabilities:
    - Signal generation and time-domain analysis
    - Sampling and quantization operations
    - Anti-alias filtering and windowing
    - Frequency-domain analysis via FFT
    - Multiple reconstruction methods (FFT-based, first-order hold)
    - Alias detection and folding frequency calculation
    - Reconstruction quality metrics (SNR, MAE, RMSE)

Mathematical Foundation:
    - Sampling: Nyquist-Shannon theorem (fs >= 2*f_max)
    - Aliasing: Frequency folding around Nyquist frequency (fs/2)
    - Reconstruction: FFT interpolation and zero/first-order hold methods
    - Quantization: Uniform mid-rise quantizer for bit depth reduction

Type Hints:
    All functions include complete type hints and comprehensive docstrings
    following Google style conventions.

Dependencies:
    - NumPy: Core array operations
    - SciPy (optional): Butterworth filter design
"""

from typing import Optional, Tuple

import numpy as np


def compute_duration(f_sig: float, cycles: float = 3.0) -> float:
    """Return visualization duration that shows a fixed number of cycles.
    
    Determines how long (in seconds) to display the signal based on the signal
    frequency and desired number of complete oscillation cycles. This ensures
    that lower frequencies still show meaningful variation in the viewport.
    
    Args:
        f_sig: Signal frequency in Hz (must be positive).
        cycles: Number of complete oscillation cycles to display. Default is 3.0.
    
    Returns:
        Duration in seconds. If f_sig is zero or negative, returns 1.0 second default.
    
    Examples:
        >>> compute_duration(10.0, cycles=3.0)  # 0.3 seconds (3 cycles of 10 Hz)
        0.3
        >>> compute_duration(1.0, cycles=2.0)   # 2.0 seconds (2 cycles of 1 Hz)
        2.0
    """
    return cycles / f_sig if f_sig > 0 else 1.0


def compute_continuous_points(max_freq: float, minimum: int = 1000, scale: int = 20) -> int:
    """Pick continuous-time resolution based on highest modeled frequency.
    
    Determines the number of points needed to represent the continuous signal
    with sufficient fidelity for visualization. Uses a scaling rule (points = scale * max_freq)
    to ensure higher frequencies are sampled more densely, maintaining a minimum
    resolution for visibility.
    
    Args:
        max_freq: Highest frequency component in Hz (e.g., from signal or harmonics).
        minimum: Minimum number of points to always use. Default is 1000.
        scale: Points-per-Hertz factor. Default is 20 (20 points per Hz of bandwidth).
    
    Returns:
        Number of continuous-time sample points to use for rendering.
    
    Examples:
        >>> compute_continuous_points(50.0)  # 1000 points (at least 1000)
        1000
        >>> compute_continuous_points(500.0)  # 10000 points (500 * 20)
        10000
    """
    return max(minimum, int(scale * max(max_freq, 1.0)))


def build_sampling_grid(
    f_samp: float, duration: float, min_points: int, min_upsample: int = 4
) -> Tuple[np.ndarray, int, int]:
    """Build a dense time grid on which every sample instant is an exact grid point.

    The grid spans exactly ``n_samples / f_samp`` seconds (one FFT period of the
    sampled sequence, endpoint excluded). Using this grid as the continuous-time
    proxy keeps three things consistent:

        - samples are taken by slicing the grid (no interpolation error),
        - FFT (band-limited periodic) reconstruction lands exactly on the grid,
        - error metrics compare signals at identical time instants.

    Args:
        f_samp: Sampling frequency in Hz (must be positive).
        duration: Requested observation window in seconds (rounded to a whole
            number of sample periods).
        min_points: Minimum number of grid points for a smooth continuous curve.
        min_upsample: Minimum number of grid points per sample period, so the
            continuous proxy is always finer than the sampled sequence.

    Returns:
        A tuple ``(t_cont, n_samples, upsample)`` where ``t_cont`` has
        ``n_samples * upsample`` points and ``t_cont[::upsample]`` are the
        sample instants ``k / f_samp``.

    Examples:
        >>> t, n, k = build_sampling_grid(100.0, 0.3, 1000)
        >>> n, k, len(t)
        (30, 34, 1020)
    """
    n_samples = max(2, int(round(duration * f_samp)))
    upsample = max(int(min_upsample), int(np.ceil(min_points / n_samples)))
    num_points = n_samples * upsample
    t_cont = np.arange(num_points) / (upsample * f_samp)
    return t_cont, n_samples, upsample


def apply_anti_alias_filter(
    y_cont: np.ndarray,
    t_cont: np.ndarray,
    f_samp: float,
    aaf_type: str,
    scipy_signal=None,
    order: int = 5,
) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray], Optional[float]]:
    """Apply optional anti-alias filtering to a continuous-time proxy signal.

    Implements three anti-alias filter types:
        1. "None": No filtering (passthrough)
        2. "Ideal": Ideal brick-wall lowpass filter via frequency-domain zeroing
        3. "Butter": Zero-phase Butterworth lowpass (requires scipy.signal)

    The filter attenuates frequencies above the Nyquist frequency (fs/2) to prevent
    aliasing artifacts when sampling below the signal's Nyquist rate.

    Args:
        y_cont: Continuous-time signal values (numpy array).
        t_cont: Corresponding time vector (numpy array, must be uniform).
        f_samp: Target sampling frequency in Hz.
        aaf_type: Filter type: "None", "Ideal", or "Butter".
        scipy_signal: scipy.signal module (required for "Butter" type).
        order: Butterworth prototype order (default 5).

    Returns:
        A tuple of (y_filtered, sos, None, fs_cont) where:
            - y_filtered: Filtered signal (same shape as y_cont)
            - sos: Butterworth second-order sections (None for "None"/"Ideal")
            - None: reserved for backwards compatibility (formerly ``a``)
            - fs_cont: Rate of the continuous-time grid (None if unfiltered)

        If "Butter" is requested but ``scipy_signal`` is None, the input is
        returned unchanged (the UI reports that SciPy is missing).

    Notes:
        - Ideal filtering uses the FFT, so it treats the window as periodic.
        - Butterworth is applied forward and backward (``sosfiltfilt``): there is no
          group delay, and the effective magnitude response is ``|H(f)|**2``.
          Second-order sections keep the design stable at very low normalized cutoffs.
        - Butterworth filtering uses a periodic extension of the window (consistent
          with the FFT-based paths), so there are no start/end transients.
        - Cutoff is clamped to 0.49*fs_cont to stay below the grid Nyquist rate.
    """
    if aaf_type == "Ideal":
        n = len(y_cont)
        dt = t_cont[1] - t_cont[0]
        yf = np.fft.fft(y_cont)
        xf = np.fft.fftfreq(n, dt)
        yf[np.abs(xf) > f_samp / 2] = 0
        return np.fft.ifft(yf).real, None, None, 1.0 / dt

    if aaf_type == "Butter" and scipy_signal is not None:
        fs_cont = 1.0 / (t_cont[1] - t_cont[0])
        cutoff = min(f_samp / 2, 0.49 * fs_cont)
        sos = scipy_signal.butter(order, cutoff, btype="low", fs=fs_cont, output="sos")
        # Periodic extension (like the FFT-based paths) avoids start/end transients.
        n = len(y_cont)
        y_ext = np.concatenate([y_cont, y_cont, y_cont])
        y_filt = scipy_signal.sosfiltfilt(sos, y_ext, padtype=None)[n : 2 * n]
        return y_filt, sos, None, fs_cont

    return y_cont, None, None, None


def sample_signal(t_cont: np.ndarray, y_cont: np.ndarray, f_samp: float, duration: float) -> Tuple[np.ndarray, np.ndarray]:
    """Sample a continuous-time proxy signal at a target sample rate.

    Takes ``max(2, floor(duration * f_samp))`` samples at instants ``k / f_samp`` and
    reads their values from the proxy by linear interpolation. When the proxy grid
    comes from :func:`build_sampling_grid`, prefer slicing ``y_cont[::upsample]``,
    which is exact.

    Args:
        t_cont: Time vector of the continuous signal.
        y_cont: Amplitude values of the continuous signal.
        f_samp: Target sampling frequency in Hz.
        duration: Total duration to sample in seconds.

    Returns:
        A tuple of (t_samp, y_samp) where:
            - t_samp: Sample instants ``k / f_samp``
            - y_samp: Interpolated amplitude values at the sample instants
    """
    num_samples = max(2, int(np.floor(duration * f_samp)))
    t_samp = np.arange(num_samples) / f_samp
    y_samp = np.interp(t_samp, t_cont, y_cont)
    return t_samp, y_samp


def quantize_signal(y: np.ndarray, bits: int, full_scale: float = 1.0) -> np.ndarray:
    """Uniformly quantize a signal with ``2**bits`` levels spanning ``±full_scale``.

    Like a real ADC, inputs beyond the full-scale range are clipped before
    quantization. With an even number of levels there is no level at exactly
    zero (mid-rise characteristic); the step size is ``2 * full_scale / (2**bits - 1)``.

    Args:
        y: Input signal.
        bits: Bit depth (at least 1).
        full_scale: Positive peak of the converter range (default 1.0).

    Returns:
        Quantized signal, always inside ``[-full_scale, full_scale]``.
    """
    levels = max(2, 2 ** int(bits))
    divisor = levels - 1
    fs_range = float(full_scale) if full_scale > 0 else 1.0
    y_norm = np.clip(np.asarray(y, dtype=np.float64) / fs_range, -1.0, 1.0)
    return (np.round((y_norm + 1.0) / 2.0 * divisor) / divisor * 2.0 - 1.0) * fs_range


def _window_weights(n: int, window_type: str) -> np.ndarray:
    if window_type == "Hamming":
        return np.hamming(n)
    if window_type == "Hann":
        return np.hanning(n)
    return np.ones(n)


def apply_window(y: np.ndarray, window_type: str) -> np.ndarray:
    """Apply optional analysis window ("None", "Hamming", or "Hann") before an FFT."""
    return y * _window_weights(len(y), window_type)


def reconstruct_fft(y_samp_fft_input: np.ndarray, num_output_points: int) -> np.ndarray:
    """Band-limited periodic reconstruction by zero-padding the spectrum.

    The output has ``num_output_points`` points spanning the same period as the input
    (``len(input) / f_samp`` seconds, endpoint excluded). For even-length inputs the
    Nyquist bin is split equally between the positive and negative halves so a
    real signal stays real.
    """
    n_samp = len(y_samp_fft_input)
    y_fft = np.fft.fft(y_samp_fft_input)
    y_padded: np.ndarray = np.zeros(num_output_points, dtype=complex)
    half = (n_samp + 1) // 2
    y_padded[:half] = y_fft[:half]
    y_padded[num_output_points - (n_samp // 2) :] = y_fft[n_samp - (n_samp // 2) :]
    if n_samp % 2 == 0 and num_output_points > n_samp:
        nyq = y_fft[n_samp // 2]
        y_padded[n_samp // 2] = nyq / 2
        y_padded[num_output_points - n_samp // 2] = nyq / 2
    return np.fft.ifft(y_padded).real * (num_output_points / n_samp)


def reconstruct_foh(t_out: np.ndarray, t_samp: np.ndarray, y_samp: np.ndarray) -> np.ndarray:
    """First-order hold reconstruction via linear interpolation."""
    return np.interp(t_out, t_samp, y_samp)


def compute_spectrum(
    y_samp: np.ndarray, f_samp: float, window_type: str = "None"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return one-sided frequency bins, amplitude spectrum, and phase.

    The magnitude is scaled to *amplitude*: a sinusoid of amplitude A that falls on
    a bin reads ≈ A, for any window (the window's coherent gain is compensated).

    Args:
        y_samp: Sampled signal (unwindowed).
        f_samp: Sampling frequency in Hz.
        window_type: Analysis window: "None", "Hamming", or "Hann".

    Returns:
        ``(freqs, amplitudes, phases)`` for bins 0 … f_samp/2.
    """
    n = len(y_samp)
    weights = _window_weights(n, window_type)
    spectrum = np.fft.rfft(np.asarray(y_samp) * weights)
    freqs = np.fft.rfftfreq(n, 1.0 / f_samp)
    mags = np.abs(spectrum) / np.sum(weights)
    # One-sided: double every bin except DC (and Nyquist for even n).
    last = len(mags) - 1 if n % 2 == 0 else len(mags)
    mags[1:last] *= 2.0
    return freqs, mags, np.angle(spectrum)


def folded_alias_frequency(max_freq: float, f_samp: float) -> float:
    """Predict folded alias position for a given highest component."""
    return float(np.abs(max_freq - f_samp * np.round(max_freq / f_samp)))


def is_aliased(max_freq: float, f_samp: float) -> bool:
    """Nyquist criterion check for the highest modeled frequency."""
    return bool(f_samp < 2.0 * max_freq)


def reconstruction_metrics(y_true: np.ndarray, y_recon: np.ndarray) -> Tuple[float, float]:
    """Return RMSE and SNR in dB for a reconstruction.

    SNR is capped at 100 dB for a perfect reconstruction and is ``-inf`` when the
    reference signal is silent but the reconstruction is not.
    """
    noise = y_true - y_recon
    noise_power = float(np.mean(noise ** 2))
    rmse = float(np.sqrt(noise_power))
    signal_power = float(np.mean(y_true ** 2))
    if noise_power <= 0:
        return rmse, 100.0
    if signal_power <= 0:
        return rmse, float("-inf")
    return rmse, float(min(100.0, 10.0 * np.log10(signal_power / noise_power)))
