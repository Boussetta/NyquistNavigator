"""Curated pedagogical presets for AliasingAtlas.

Presets are pre-configured scenarios that illustrate key DSP concepts through
specific parameter combinations. They provide "one-click" learning examples that
demonstrate:

    1. Safe Nyquist: Oversampling (fs >> 2*f_max) with high fidelity
    2. Near Nyquist: Sampling at exactly or just above Nyquist boundary
    3. Aliasing: Undersampling (fs < 2*f_max) demonstrating aliasing artifacts
    4. AM Sidebands: Modulated signal with spectral analysis

Each preset is immutable (frozen dataclass) to ensure consistent, reproducible
pedagogical examples that cannot be accidentally modified.

Typical Workflow:
    1. User selects a preset from the UI dropdown
    2. Preset values load all simulator parameters atomically
    3. Visualization updates to show the preset scenario
    4. User adjusts parameters incrementally to explore boundaries
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Preset:
    """Immutable configuration snapshot for a pedagogical scenario.
    
    Attributes:
        name: Human-readable preset name.
        f_sig: Signal/carrier frequency in Hz.
        f_samp: Sampling frequency in Hz.
        f_harm: Harmonic or modulation frequency in Hz.
        a_harm: Amplitude or modulation index (0-1 typically).
        phase: Initial phase offset in radians.
        n_harm: Number of Fourier harmonics for synthesis.
        bits: Quantization bit depth.
        wave_type: Waveform type (Sine, Square, AM, etc.).
        aaf_type: Anti-alias filter type (None, Ideal, Butter).
        recon_type: Reconstruction method (FFT, FOH).
        window_type: Spectral windowing (None, Hamming, Hann).
    """

    name: str
    f_sig: float
    f_samp: float
    f_harm: float
    a_harm: float
    phase: float
    n_harm: int
    bits: int
    wave_type: str
    aaf_type: str
    recon_type: str
    window_type: str


# Pedagogical preset library
PRESETS: Dict[str, Preset] = {
    "Safe Nyquist": Preset(
        name="Safe Nyquist",
        f_sig=10.0,
        f_samp=100.0,
        f_harm=20.0,
        a_harm=0.0,
        phase=0.0,
        n_harm=1,
        bits=16,
        wave_type="Sine",
        aaf_type="None",
        recon_type="FFT",
        window_type="None",
    ),
    "Near Nyquist": Preset(
        name="Near Nyquist",
        f_sig=10.0,
        f_samp=22.0,
        f_harm=20.0,
        a_harm=0.0,
        phase=0.0,
        n_harm=1,
        bits=16,
        wave_type="Sine",
        aaf_type="None",
        recon_type="FFT",
        window_type="None",
    ),
    "Aliasing": Preset(
        name="Aliasing",
        f_sig=10.0,
        f_samp=15.0,
        f_harm=20.0,
        a_harm=0.0,
        phase=0.0,
        n_harm=1,
        bits=16,
        wave_type="Sine",
        aaf_type="None",
        recon_type="FFT",
        window_type="None",
    ),
    "AM Sidebands": Preset(
        name="AM Sidebands",
        f_sig=25.0,
        f_samp=180.0,
        f_harm=3.0,
        a_harm=0.7,
        phase=0.0,
        n_harm=1,
        bits=12,
        wave_type="AM",
        aaf_type="Ideal",
        recon_type="FFT",
        window_type="Hann",
    ),
}


def preset_names() -> List[str]:
    """Return list of available preset names in order.
    
    Returns:
        Sorted list of preset identifiers.
    """
    return list(PRESETS.keys())


def get_preset(name: str) -> Preset:
    """Retrieve a preset configuration by name.
    
    Args:
        name: Preset identifier (must exist in PRESETS).
    
    Returns:
        Immutable Preset dataclass with all configuration parameters.
    
    Raises:
        KeyError: If preset name is not found.
    """
    return PRESETS[name]
