# AliasingAtlas

AliasingAtlas is an interactive educational tool designed to visualize the fundamental principles of the Nyquist-Shannon sampling theorem. By simulating the sampling and reconstruction of continuous sine waves, it provides an intuitive platform for exploring signal fidelity, zero-order hold distortion, and FFT-based (sinc) interpolation.

## Workspace Structure

This project follows the industry-standard `src` layout:

```text
.
├── src/
│   └── aliasing_atlas/    # Principal package source
│       ├── __init__.py    # Versioning
│       ├── __main__.py    # CLI Entry point
│       └── app.py         # Main GUI and Logic
├── tests/                 # Unit tests (pytest)
├── pyproject.toml         # Build system and dependencies
├── sinewave-ampling.py    # Legacy entry point shim
└── README.md
```

## Installation

Professional installation using `pip` ensures all dependencies are met:

```bash
# Install in editable mode for development
pip install -e .
```

## Usage

After installation, you can launch the tool in three ways:

1.  **Command Line:** Simply type `aliasing-atlas` in your terminal.
2.  **Python Module:** Run `python -m aliasing_atlas`.
3.  **Notebook:** Open `AliasingAtlas.ipynb` for an interactive Jupyter experience.

## Development & Testing

To run the automated test suite, ensure `pytest` is installed:

```bash
pip install pytest
pytest
```

## Understanding the Plot

-   **Ideal Continuous Wave (Blue Dashed Line):** Represents the original, un-sampled sine wave.
-   **Zero-Order Hold (Square) (Crimson Line):** Shows how the sampled values are held constant until the next sample point, creating a staircase-like approximation of the original signal.
-   **Sample Points (Dark Red Dots):** Indicate the exact moments in time when the signal's amplitude was measured.
-   **Aliasing Warning:** If the sampling rate is insufficient, the status bar turns orange to warn of potential aliasing.
-   **FFT-based Reconstruction (Green Line):** Shows a smoother reconstruction of the signal achieved by performing an Inverse Fast Fourier Transform (IFFT) on the zero-padded spectrum of the sampled signal. This method aims to recover the original continuous signal more accurately than zero-order hold, especially when the Nyquist criterion is met.

## Features

-   **Interactive Input:** Easily specify signal frequency and sampling rate via sliders.
-   **Dynamic Plotting:** The plot automatically adjusts its time duration to always show 3 full cycles of the signal.
-   **Zero-Order Hold Visualization:** Clearly demonstrates discrete samples held as constant steps.
-   **Bit-Depth Quantization:** Explore the effects of reduced bit-depth on signal fidelity.
-   **Windowing:** Compare Hamming and Hann windows for spectral analysis.

## Example Usage

Try these inputs to see different effects:

-   **Good Sampling:**
    -   Signal Frequency: `10` Hz
    -   Sampling Rate: `100` Hz (10x Nyquist)
-   **Nyquist Rate:**
    -   Signal Frequency: `10` Hz
    -   Sampling Rate: `20` Hz (Exactly Nyquist)
-   **Aliasing (Below Nyquist):**
    -   Signal Frequency: `10` Hz
    -   Sampling Rate: `15` Hz

This documentation should make your tool much easier for others (and your future self!) to understand and use.