"""AliasingAtlas: Interactive Educational Tool for Signal Sampling and Aliasing.

This module provides an interactive graphical tool for exploring the Nyquist-Shannon
sampling theorem and digital signal processing (DSP) concepts. It visualizes the effects
of sampling rate, quantization, anti-alias filtering, and signal reconstruction.

Key Features:
    - Interactive matplotlib-based GUI with real-time visualization
    - Multiple signal models (sine, square, sawtooth, triangle, modulated, chirp)
    - Configurable sampling and reconstruction parameters
    - Preset pedagogical scenarios for guided learning
    - Export functionality for configurations and audio artifacts

Usage:
    The tool can be launched in multiple ways:
    
    1. Command line:     aliasing-atlas
    2. Python module:    python -m aliasing_atlas
    3. Jupyter Notebook: Open AliasingAtlas.ipynb

For installation and detailed documentation, visit:
    https://github.com/Boussetta/NyquistNavigator

License:
    MIT License - See LICENSE file for details
"""

__version__ = "1.0.0"
__author__ = "Wissem Boussetta"
__email__ = "wissem.boussetta@example.com"

# Public API exports
from .app import AliasingToolbox
from .dsp import (
    compute_duration,
    compute_continuous_points,
    apply_anti_alias_filter,
    sample_signal,
    quantize_signal,
    apply_window,
    reconstruct_fft,
    reconstruct_foh,
    compute_spectrum,
    folded_alias_frequency,
    is_aliased,
    reconstruction_metrics,
)
from .signals import SignalRegistry, Signal
from .presets import Preset, get_preset, preset_names
from .learning import build_learning_hint
from .exporting import ensure_export_dir, save_config_json, timestamp_tag, write_wav_mono16

__all__ = [
    "AliasingToolbox",
    "SignalRegistry",
    "Signal",
    "Preset",
    "get_preset",
    "preset_names",
    "build_learning_hint",
    "ensure_export_dir",
    "save_config_json",
    "timestamp_tag",
    "write_wav_mono16",
    "compute_duration",
    "compute_continuous_points",
    "apply_anti_alias_filter",
    "sample_signal",
    "quantize_signal",
    "apply_window",
    "reconstruct_fft",
    "reconstruct_foh",
    "compute_spectrum",
    "folded_alias_frequency",
    "is_aliased",
    "reconstruction_metrics",
]
