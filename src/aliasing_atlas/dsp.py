"""Pure DSP helpers for sampling, reconstruction, and analysis."""

from typing import Optional, Tuple

import numpy as np


def compute_duration(f_sig: float, cycles: float = 3.0) -> float:
    """Return visualization duration that shows a fixed number of cycles."""
    return cycles / f_sig if f_sig > 0 else 1.0


def compute_continuous_points(max_freq: float, minimum: int = 1000, scale: int = 20) -> int:
    """Pick continuous-time resolution based on highest modeled frequency."""
    return max(minimum, int(scale * max(max_freq, 1.0)))


def apply_anti_alias_filter(
    y_cont: np.ndarray,
    t_cont: np.ndarray,
    f_samp: float,
    aaf_type: str,
    scipy_signal=None,
) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray], Optional[float]]:
    """Apply optional anti-alias filtering to a continuous-time proxy signal."""
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
    """Sample a continuous-time proxy signal at a target sample rate."""
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