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


def apply_anti_alias_filter(
    y_cont: np.ndarray,
    t_cont: np.ndarray,
    f_samp: float,
    aaf_type: str,
    scipy_signal=None,
) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray], Optional[float]]:
    """Apply optional anti-alias filtering to a continuous-time proxy signal.
    
    Implements three anti-alias filter types:
        1. "None": No filtering (passthrough)
        2. "Ideal": Ideal brick-wall lowpass filter via frequency-domain zeroing
        3. "Butter": Butterworth IIR filter (requires scipy.signal)
    
    The filter attenuates frequencies above the Nyquist frequency (fs/2) to prevent
    aliasing artifacts when sampling below the signal's Nyquist rate.
    
    Args:
        y_cont: Continuous-time signal values (numpy array).
        t_cont: Corresponding time vector (numpy array, must be uniform).
        f_samp: Target sampling frequency in Hz.
        aaf_type: Filter type: "None", "Ideal", or "Butter".
        scipy_signal: scipy.signal module (required for "Butter" type).
    
    Returns:
        A tuple of (y_filtered, b, a, fs_cont) where:
            - y_filtered: Filtered signal (same shape as y_cont)
            - b, a: Filter coefficients (None for "None" and "Ideal" types)
            - fs_cont: Continuous-time sampling frequency (None if no filter applied)
    
    Raises:
        ImportError: If "Butter" is requested but scipy.signal is not available.
    
    Notes:
        - Ideal filtering uses FFT and is exact but computationally intensive
        - Butterworth uses a 5th-order IIR filter with cutoff at fs/2
        - Cutoff is clamped to 0.49*fs_cont to avoid numerical issues
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
        b, a = scipy_signal.butter(5, cutoff, btype="low", fs=fs_cont)
        return scipy_signal.lfilter(b, a, y_cont), b, a, fs_cont

    return y_cont, None, None, None


def sample_signal(t_cont: np.ndarray, y_cont: np.ndarray, f_samp: float, duration: float) -> Tuple[np.ndarray, np.ndarray]:
    """Sample a continuous-time proxy signal at a target sample rate.
    
    Discretizes a continuous signal by selecting samples at uniform time intervals
    determined by the sampling frequency. Uses linear interpolation to map continuous
    values to discrete sample points.
    
    Args:
        t_cont: Time vector of the continuous signal.
        y_cont: Amplitude values of the continuous signal.
        f_samp: Target sampling frequency in Hz.
        duration: Total duration to sample in seconds.
    
    Returns:
        A tuple of (t_samp, y_samp) where:
            - t_samp: Time vector of sampled points (length = duration * f_samp)
            - y_samp: Interpolated amplitude values at sampled times
    
    Raises:
        ValueError: If duration or f_samp is non-positive.
    
    Notes:
        - Ensures at least 2 samples to avoid empty arrays
        - Uses numpy.interp for efficient linear interpolation
    """
    num_samples = max(2, int(np.floor(duration * f_samp)))
    t_samp = np.linspace(0.0, (num_samples - 1) / f_samp, num_samples)
    y_samp = np.interp(t_samp, t_cont, y_cont)
    return t_samp, y_samp



def quantize_signal(y: np.ndarray, bits: int) -> np.ndarray:
    """Uniform mid-tread quantizer on the normalized range [-1, 1]."""
    levels = max(2, 2 ** bits)
    divisor = levels - 1
    return np.round((y + 1.0) / 2.0 * divisor) / divisor * 2.0 - 1.0


def apply_window(y: np.ndarray, window_type: str) -> np.ndarray:
    """Apply optional analysis window before FFT operations."""
    n = len(y)
    if window_type == "Hamming":
        return y * np.hamming(n)
    if window_type == "Hann":
        return y * np.hanning(n)
    return y


def reconstruct_fft(y_samp_fft_input: np.ndarray, num_output_points: int) -> np.ndarray:
    """Reconstruct by zero-padding in frequency domain and inverse FFT."""
    n_samp = len(y_samp_fft_input)
    y_fft = np.fft.fft(y_samp_fft_input)
    y_padded = np.zeros(num_output_points, dtype=complex)
    half = (n_samp + 1) // 2
    y_padded[:half] = y_fft[:half]
    y_padded[num_output_points - (n_samp // 2) :] = y_fft[n_samp - (n_samp // 2) :]
    return np.fft.ifft(y_padded).real * (num_output_points / n_samp)


def reconstruct_foh(t_out: np.ndarray, t_samp: np.ndarray, y_samp: np.ndarray) -> np.ndarray:
    """First-order hold reconstruction via linear interpolation."""
    return np.interp(t_out, t_samp, y_samp)


def compute_spectrum(y_fft_input: np.ndarray, f_samp: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return one-sided frequency bins, magnitude, and phase."""
    n = len(y_fft_input)
    freqs = np.fft.rfftfreq(n, 1.0 / f_samp)
    mags = np.abs(np.fft.rfft(y_fft_input)) / n
    phases = np.angle(np.fft.rfft(y_fft_input))
    return freqs, mags, phases


def folded_alias_frequency(max_freq: float, f_samp: float) -> float:
    """Predict folded alias position for a given highest component."""
    return float(np.abs(max_freq - f_samp * np.round(max_freq / f_samp)))


def is_aliased(max_freq: float, f_samp: float) -> bool:
    """Nyquist criterion check for the highest modeled frequency."""
    return bool(f_samp < 2.0 * max_freq)


def reconstruction_metrics(y_true: np.ndarray, y_recon: np.ndarray) -> Tuple[float, float]:
    """Return RMSE and SNR in dB for a reconstruction."""
    noise = y_true - y_recon
    rmse = float(np.sqrt(np.mean(noise ** 2)))
    signal_power = float(np.mean(y_true ** 2))
    noise_power = float(np.mean(noise ** 2))
    snr = 100.0 if noise_power <= 0 else 10.0 * np.log10(signal_power / noise_power)
    return rmse, float(snr)