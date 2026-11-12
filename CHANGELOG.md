# Changelog

All notable changes to AliasingAtlas are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Clicking sliders raised `RuntimeError: Another Axes already grabs mouse input` (shown as an ipympl traceback in Colab). The three control tabs share screen positions, and matplotlib widgets react to clicks even when hidden. Widgets on hidden tabs are now deactivated, so they no longer react or silently change value (#27).
- A slider drag released outside the figure no longer leaves a stale mouse grab that blocks the next slider; drags also end when the pointer leaves the figure (#27).

## [2.0.0] - 2026-11-12

A correctness release. Reconstruction, filtering, quantization, and spectrum readouts now match sampling theory, every preset demonstrates its lesson, and the Colab notebook is rewritten around guided experiments.

### Migration from 1.x

- **Python 3.10 or newer is required.** On Python 3.8/3.9, pip keeps installing 1.0.0.
- **Desktop audio is optional:** `pip install "aliasing-atlas[audio]"` installs `sounddevice`. In notebooks, `pip install "aliasing-atlas[notebook]"`.
- `compute_spectrum()` returns **amplitudes** (a unit sine reads 1.0; it read 0.5 before). Pass `window_type=` instead of pre-windowing the samples.
- `apply_anti_alias_filter(..., "Butter")` returns `(y, sos, None, fs_cont)`: second-order sections replace `b, a`, and filtering is zero-phase.
- `quantize_signal()` clips to `±full_scale` (default 1.0). Pass `full_scale=` for larger signals.
- The extra tone on Square/Sawtooth/Triangle is a pure sinusoid, and a Chirp whose end frequency is below its start now sweeps downward.

### Added

- Release workflow runs tests, Ruff, and mypy before publishing, and limits write/OIDC permissions to the publish job (#18).
- `build_sampling_grid()` builds a dense time grid on which every sample instant is an exact grid point.
- `quantize_signal(..., full_scale=...)` and `compute_spectrum(..., window_type=...)` parameters.
- End-to-end pipeline accuracy tests.
- `AliasingToolbox(figsize=..., output=...)`: in notebooks, audio players and export download links appear in an output panel below the figure (#19).
- `compute_observation_window()` chooses a display window that shows slow modulation, the predicted alias, at least 24 samples, and, when possible, a whole number of periods (#19).
- Colab notebook rewritten: one-step install, a "reading the screen" guide, seven guided experiments, a scripting example, and troubleshooting. The README has an Open in Colab badge (#19).

### Changed

- **Python 3.10+ is now required.** Python 3.8 and 3.9 are end-of-life and no longer available on CI runners (#17).
- `sounddevice` moved to the optional `audio` extra, and `ipympl`/`ipywidgets` to the new `notebook` extra (#17).
- `import aliasing_atlas` no longer imports `matplotlib.pyplot`; `AliasingToolbox` is loaded on first access (#17).

### Removed

- `aliasing_atlas.test_logic` (a test module shipped inside the package) and the `DOCUMENTATION_IMPROVEMENTS.md` process log (#17).
- Placeholder `__email__` package metadata (#17).

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
- GUI layout no longer overlaps: the summary line, sliders, preset/learn titles, and slider values had collided with plot titles and tick labels. The default figure is 11 x 8.2 in, so it fits a notebook. Axes have labels, and legends list only visible curves above the data (#19).
- The AM Sidebands preset now shows the envelope and resolves the sidebands (carrier 1.0, sidebands m/2). The Aliasing preset shows the 5 Hz alias traced by the samples. Near Nyquist reconstructs at ~97 dB (#19).
- With an Ideal anti-alias filter, the status reports filtered content instead of "ALIASING DETECTED", and the learning hint explains the trade-off (#19).
- Chirp supports downward sweeps (end frequency below start) instead of silently clamping them (#19).

## [1.0.0] - 2026-09-04

### Added

- Automated tag-based release workflow with package version verification.
- PyPI Trusted Publishing and GitHub Release integration.
- Maintainer release checklist in `RELEASING.md`.
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

