# Changelog

All notable changes to AliasingAtlas are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Automated tag-based release workflow with package version verification.
- PyPI Trusted Publishing and GitHub Release integration.
- Maintainer release checklist in `RELEASING.md`.
- `build_sampling_grid()` builds a dense time grid on which every sample instant is an exact grid point.
- `quantize_signal(..., full_scale=...)` and `compute_spectrum(..., window_type=...)` parameters.
- End-to-end pipeline accuracy tests.

### Fixed

- FFT reconstruction no longer uses the windowed samples; the analysis window now only affects the spectrum (#15).
- FFT reconstruction, sampling, and error metrics now share one time axis. A 10x oversampled 16-bit sine now reports ~97 dB SNR instead of 14-39 dB (#15).
- Butterworth anti-alias filter is now zero-phase (`sosfiltfilt` with second-order sections), so its delay is no longer counted as reconstruction error. The plotted response shows the effective |H|² (#15).
- Quantizer clips to its full-scale range like a real ADC. The GUI sets the range automatically to the signal peak (#15).
- Magnitude spectrum is amplitude-scaled (a unit sine reads 1.0) and compensates for the window's coherent gain (#15).
- `reconstruction_metrics` no longer emits a divide-by-zero warning for a silent reference (#15).
- The extra tone added to Square/Sawtooth/Triangle is now a pure sinusoid, so aliasing detection is exact. Before, it was a hard-edged wave with unbounded bandwidth (#16).
- Sine bandwidth no longer scales with the unused Fourier-harmonics slider (#16).
- Only controls a model ignores are dimmed. AM/FM keep message frequency and modulation depth/index; Chirp keeps its end frequency and labels it (#16).
- "Reset All" restores the first preset and its selector in a single redraw. The GUI now starts in that preset (#16).
- A missing SciPy no longer hides the reconstruction metrics (#16).

## [1.0.0] - 2026-09-04

### Added

- **Interactive GUI**: Full matplotlib-based 2×2 subplot layout with real-time updates
  - Time-domain view of continuous and sampled signals
  - Frequency-domain FFT spectrum analysis
  - Quantization visualization with bit-depth control
  - Reconstruction error metrics (SNR, MAE, RMSE)

- **Signal Models**: Comprehensive waveform generation
  - Sine, Square, Sawtooth, Triangle waves
  - Amplitude Modulation (AM)
  - Frequency Modulation (FM)
  - Chirp (frequency sweep) signals
  - Fourier series-based synthesis for non-sinusoidal waves

- **Sampling & Reconstruction**
  - Configurable sampling rate (1–1000 Hz range)
  - Anti-alias filtering (None, Ideal brick-wall, Butterworth)
  - Reconstruction methods (FFT-based, First-Order Hold)
  - Windowing options (None, Hann, Hamming) for spectral analysis

- **Quantization**
  - Bit depth control (4–16 bits)
  - Visualization of quantization levels and error
  - Signal-to-Noise Ratio (SNR) calculation

- **Pedagogical Features**
  - Preset scenarios (Safe Nyquist, Near Nyquist, Aliasing, AM Sidebands)
  - Guided Learning Mode with context-aware hints
  - Status bar showing:
    - Alias frequency detection
    - Reconstruction accuracy metrics
    - Active filter and modulation parameters

- **Export Toolkit**
  - Save simulator state as JSON configuration
  - Export audio as PCM16 WAV files (at sampling rate or 16 kHz playback rate)
  - Timestamp-based file naming
  - Local `exports/` directory management

- **Multi-Platform Support**
  - Jupyter Notebook (.ipynb) with Colab compatibility
  - Desktop CLI (`aliasing-atlas` command)
  - Python module entry point (`python -m aliasing_atlas`)

- **Comprehensive Testing**: pytest unit tests covering
  - DSP functions (quantization, filtering, reconstruction)
  - Signal generation (Fourier series, modulation)
  - Preset loading and boundary conditions
  - Learning hints and all pedagogical modes
  - Export (JSON, WAV file creation, timestamps)

- **Professional Documentation**
  - Project structure and code organization
  - Installation and usage instructions
  - Contributing guidelines (CONTRIBUTING.md)
  - Governance and decision-making policy (GOVERNANCE.md)
  - Security policy and best practices (SECURITY.md)
  - Comprehensive docstrings and type hints

### Technical Highlights

- Pure DSP functions decoupled from UI for testability and reusability
- Type-hinted codebase with full docstring coverage
- PEP 508-compliant dependency specifications
- Optional scipy dependency (graceful degradation)
- Notebook JSON validation and robust environment detection

