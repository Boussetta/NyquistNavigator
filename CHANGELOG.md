# Changelog

All notable changes to AliasingAtlas are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-06-17

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

- **Comprehensive Testing**: 18 unit tests covering
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

