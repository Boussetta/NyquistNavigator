# AliasingAtlas

<div align="center">

**Interactive Educational Tool for Visualizing Digital Signal Processing Concepts**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-18%20Passing-brightgreen)](#testing)

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation)

</div>

## Overview

**AliasingAtlas** is an interactive educational tool designed to visualize the fundamental principles of the **Nyquist-Shannon sampling theorem** and digital signal processing (DSP). By simulating the sampling, quantization, and reconstruction of various waveforms in real-time, it provides an intuitive platform for exploring signal fidelity, aliasing effects, and core DSP concepts.

The tool combines:
- **Real-time interactive visualization** with matplotlib
- **Multiple signal models** (sine, square, sawtooth, triangle, modulated, chirp)
- **Configurable sampling parameters** (rate, quantization, filtering, reconstruction)
- **Pedagogical presets** for guided learning
- **Export capabilities** for reproducibility and analysis

Perfect for students, educators, and signal processing practitioners who want to deeply understand how signals behave when sampled, quantized, and reconstructed.

## Features

### 🎯 Core Functionality

- **Interactive GUI** with 2×2 subplot layout:
  - Time-domain view of continuous and sampled signals
  - Frequency-domain FFT spectrum analysis
  - Phase spectrum visualization
  - Quantization error plot with metrics

- **Multiple Signal Models:**
  - Basic waveforms: Sine, Square, Sawtooth, Triangle
  - Modulated signals: AM (Amplitude Modulation), FM (Frequency Modulation)
  - Chirp (frequency sweep) for time-varying bandwidth analysis
  - Fourier series synthesis with configurable harmonic count

- **Comprehensive Sampling Control:**
  - Adjustable sampling rate (5–1500 Hz range)
  - Anti-alias filtering (None, Ideal brick-wall, Butterworth IIR)
  - Multiple reconstruction methods (FFT-based, First-Order Hold)
  - Spectral windowing (Hamming, Hann)
  - Quantization (4–16 bits)

- **Real-time Analysis Metrics:**
  - Signal-to-Noise Ratio (SNR) calculation
  - Reconstruction error (MAE, RMSE)
  - Alias detection and folded frequency calculation
  - Zero-Order Hold and FFT reconstruction comparison

### 🎓 Pedagogical Features

- **Preset Scenarios:** One-click loading of curated learning examples:
  - Safe Nyquist (10×oversampling)
  - Near Nyquist (boundary conditions)
  - Aliasing (undersampling demonstration)
  - AM Sidebands (modulation analysis)

- **Guided Learning Mode:** Context-aware hints that explain:
  - Why aliasing is occurring and how to fix it
  - Quantization noise and bit-depth tradeoffs
  - Anti-alias filter necessity and placement
  - Reconstruction method differences

### 💾 Export & Reproducibility

- **JSON Configuration Export:** Save simulator state for reproducibility
- **WAV Audio Export:** Standard PCM16 mono files at configurable sample rates
- **Timestamp-based Organization:** Automatic file naming and directory management

### 🌍 Multi-Platform Support

- **Jupyter Notebook** (`AliasingAtlas.ipynb`) with Google Colab support
- **Desktop CLI:** `aliasing-atlas` command
- **Python Module:** `python -m aliasing_atlas`
- Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.8 or later
- pip or conda

### From PyPI (Recommended)

```bash
pip install aliasing-atlas
```

Then launch:
```bash
aliasing-atlas
```

### For Development

Clone the repository and install in editable mode:

```bash
git clone https://github.com/Boussetta/NyquistNavigator.git
cd sinewave-sampling
pip install -e ".[dev]"
```

## Quick Start

### GUI Application

Simply run:
```bash
aliasing-atlas
```

Or via Python:
```bash
python -m aliasing_atlas
```

### Jupyter Notebook

Open `AliasingAtlas.ipynb` in Jupyter or Google Colab for an interactive notebook experience.

### Programmatic Usage

```python
from aliasing_atlas import AliasingToolbox
import matplotlib.pyplot as plt

# Create and display the interactive tool
toolbox = AliasingToolbox()
plt.show()

# Or use DSP functions directly:
from aliasing_atlas import SignalRegistry, compute_spectrum, sample_signal
import numpy as np

t = np.linspace(0, 1, 1000)
y = SignalRegistry.create_signal('Sine', t, f_sig=10, f_harm=20, a_harm=0.0, phase=0)
y_sampled, t_sampled = sample_signal(t, y, f_samp=30, duration=1.0)
freq, magnitude = compute_spectrum(y_sampled, 1.0/30)
```

## Understanding the Visualization

### Time-Domain Plot (Top-Left)
- **Blue Dashed Line:** Original continuous signal (ideal reference)
- **Yellow Line:** Anti-alias filtered version (if filtering enabled)
- **Green Line:** FFT-based reconstruction (smooth curve)
- **Red Staircase:** Zero-Order Hold reconstruction
- **Dark Red Dots:** Actual sample points

### Frequency-Domain Plots (Right)
- **Magnitude Spectrum:** Frequency components of the signal
  - **Blue Line:** Original signal spectrum
  - **Orange Dashed:** Nyquist limit (fs/2)
  - **Magenta Dashed:** Predicted alias frequency
  - **Black Dashed:** Anti-alias filter response

- **Phase Spectrum:** Phase angle at each frequency

### Quantization Plot (Bottom-Left)
- Residual error between quantized and ideal signal
- Larger errors indicate coarse quantization (low bit-depth)

### Status Bar
Real-time information:
- Alias status (active/inactive)
- SNR and reconstruction metrics
- Active filter and modulation parameters

## Pedagogical Scenarios

### Safe Nyquist
- **Signal:** 10 Hz sine
- **Sampling:** 100 Hz (10× Nyquist)
- **Purpose:** Demonstrates high-fidelity sampling with no aliasing
- **Observation:** Perfect reconstruction; zoom in on quantization effects

### Near Nyquist
- **Signal:** 10 Hz sine
- **Sampling:** 22 Hz (just above 2×f_sig)
- **Purpose:** Boundary conditions at Nyquist limit
- **Observation:** Small reduction in fidelity; small phase distortion

### Aliasing
- **Signal:** 10 Hz sine
- **Sampling:** 15 Hz (below 2×f_sig)
- **Purpose:** Classic aliasing demonstration
- **Observation:** Apparent alias at 5 Hz; reconstruction artifact

### AM Sidebands
- **Signal:** 25 Hz carrier, 3 Hz modulation (70% depth)
- **Sampling:** 180 Hz
- **Purpose:** Modulated signal bandwidth expansion
- **Observation:** Spectral sidebands at 22 Hz and 28 Hz

## DSP Functions (Pure API)

All DSP operations are available as pure functions for integration into other projects:

```python
from aliasing_atlas.dsp import (
    sample_signal,
    quantize_signal,
    apply_anti_alias_filter,
    reconstruct_fft,
    reconstruct_foh,
    compute_spectrum,
    is_aliased,
    folded_alias_frequency,
)

# Example: Full pipeline
import numpy as np

# 1. Generate signal
t_cont = np.linspace(0, 0.3, 3000)
y_cont = np.sin(2*np.pi*10*t_cont)

# 2. Apply anti-alias filter
y_filt, _, _, _ = apply_anti_alias_filter(y_cont, t_cont, f_samp=30, aaf_type='Ideal')

# 3. Sample
t_samp, y_samp = sample_signal(t_cont, y_filt, f_samp=30, duration=0.3)

# 4. Quantize
y_quant = quantize_signal(y_samp, bits=8)

# 5. Reconstruct
y_recon = reconstruct_fft(t_samp, y_quant, f_samp=30)

# 6. Analyze
freq, mag = compute_spectrum(y_quant, fs=30)
aliased = is_aliased(f_sig=10, f_samp=30)
alias_freq = folded_alias_frequency(f_sig=10, f_samp=30)
```

## Testing

Run the comprehensive test suite (18 passing tests):

```bash
pip install pytest
pytest tests/
```

Test coverage includes:
- DSP functions (sampling, quantization, filtering, reconstruction)
- Signal generation (Fourier series, modulation, chirp)
- Preset scenarios and pedagogical modes
- Export functionality (JSON, WAV)

## Project Structure

```
sinewave-sampling/
├── src/aliasing_atlas/              # Main package
│   ├── __init__.py                  # Version & public API
│   ├── __main__.py                  # CLI entry point
│   ├── app.py                       # Interactive GUI (1000+ lines)
│   ├── dsp.py                       # Pure DSP functions
│   ├── signals.py                   # Signal generation models
│   ├── presets.py                   # Pedagogical presets
│   ├── learning.py                  # Learning hint engine
│   └── exporting.py                 # Export utilities
├── tests/                           # Test suite
│   ├── test_logic.py
│   ├── test_dsp.py
│   ├── test_presets.py
│   ├── test_phase4.py
│   └── test_exporting.py
├── AliasingAtlas.ipynb              # Interactive Jupyter notebook
├── pyproject.toml                   # Build configuration (PEP 517/518)
├── CONTRIBUTING.md                  # Contribution guidelines
├── GOVERNANCE.md                    # Project governance
├── SECURITY.md                      # Security policy
├── CHANGELOG.md                     # Release notes
└── README.md                        # This file
```

## Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md):** Guidelines for contributing code and bug reports
- **[GOVERNANCE.md](GOVERNANCE.md):** Project decision-making and maintainer policies
- **[SECURITY.md](SECURITY.md):** Security considerations and reporting vulnerabilities
- **[CHANGELOG.md](CHANGELOG.md):** Detailed release notes and feature history

## Examples

### Example 1: Observing Aliasing

1. Set Signal Frequency to **10 Hz**
2. Set Sampling Rate to **15 Hz** (below 2×10=20 Hz Nyquist)
3. Observe the predicted alias frequency (5 Hz) in status bar
4. Notice the green FFT reconstruction shows a 5 Hz sine instead of 10 Hz
5. Gradually increase sampling rate and watch the alias frequency decrease to zero

### Example 2: Quantization Effects

1. Set Bit Depth to **4 bits** (16 levels)
2. Observe heavy staircase patterns in time-domain plot
3. Notice large error residuals in quantization plot
4. Gradually increase bit depth and watch noise decrease
5. At 16 bits, quantization noise becomes imperceptible

### Example 3: Modulation

1. Select "AM" waveform from Waveform selector
2. Set Harmonic Frequency to **3 Hz** and Harmonic Amp to **0.7**
3. Observe sidebands at ±3 Hz around carrier frequency in spectrum
4. Toggle Anti-Alias to see filter response relative to modulation bandwidth
5. Try FM for comparison of bandwidth and spectral characteristics

## References

### Textbooks
- **Oppenheim & Schafer,** "Discrete-Time Signal Processing" (3rd ed.)
- **Proakis & Salehi,** "Digital Signal Processing" (4th ed.)
- **Lyons,** "Understanding Digital Signal Processing" (3rd ed.)

### Standards
- **IEEE 1057-2017:** Standard for Digitizing Waveform Recorders
- **Nyquist-Shannon Sampling Theorem:** http://mathworld.wolfram.com/SamplingTheorem.html

## License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

## Citation

If you use AliasingAtlas in academic research or teaching, please cite:

```bibtex
@software{aliasingatlas2024,
  author = {Wissem Boussetta},
  title = {AliasingAtlas: Interactive Tool for Visualizing Sampling and Aliasing},
  year = {2024},
  url = {https://github.com/Boussetta/NyquistNavigator}
}
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct
- Development setup
- Pull request guidelines
- Coding standards
- Testing requirements

## Acknowledgments

- Inspired by educational signal processing visualizations
- Built with matplotlib for interactive visualization
- NumPy/SciPy for numerical computation
- Sounddevice and IPython for audio integration

## Troubleshooting

### "Module not found" when importing

Ensure package is installed:
```bash
pip install -e .
```

### Audio not playing in Colab

The tool automatically detects the environment:
- **Desktop:** Uses sounddevice for audio output
- **Jupyter/Colab:** Uses IPython.display.Audio with HTML5 playback

If audio still doesn't play, check browser speaker settings and console for warnings.

### Slow rendering on large displays

Reduce `num_continuous_points` in code or use a lower resolution preset scenario.

## Contact & Support

- **Issues:** [GitHub Issues](https://github.com/Boussetta/NyquistNavigator/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Boussetta/NyquistNavigator/discussions)
- **Email:** wissem.boussetta@outlook.com

---

**Made with ❤️ for signal processing education**

