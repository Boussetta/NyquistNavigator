# AliasingAtlas

AliasingAtlas is an interactive educational tool designed to visualize the fundamental principles of the Nyquist-Shannon sampling theorem. By simulating the sampling and reconstruction of continuous sine waves, it provides an intuitive platform for exploring signal fidelity, zero-order hold distortion, and FFT-based (sinc) interpolation.

## Live Interactive Notebook

You can also run this project as a Jupyter Notebook: [`AliasingAtlas.ipynb`](AliasingAtlas.ipynb). This is ideal for interactive exploration in environments like MyBinder.

## Features

-   **Interactive Input:** Easily specify signal frequency and sampling rate.
-   **Dynamic Plotting:** The plot automatically adjusts its time duration to always show 3 full cycles of the signal, ensuring clear visualization regardless of the frequency.
-   **Zero-Order Hold Visualization:** Clearly demonstrates how discrete samples are held to reconstruct a continuous signal, forming a square-wave approximation.
-   **Nyquist Warning:** Alerts the user when the sampling rate is insufficient to accurately represent the signal, highlighting the concept of aliasing.
-   **FFT-based Reconstruction:** Demonstrates how a bandlimited interpolation using FFT can reconstruct a smoother signal from discrete samples, offering a comparison to zero-order hold.
-   **Portability:** Built with standard Python libraries (`numpy`, `matplotlib`), making it easy to run on Windows, Linux, or macOS.

## Prerequisites

Before running the tool, ensure you have Python installed (version 3.6 or higher is recommended).

You will also need the following Python libraries:

-   `numpy`
-   `matplotlib`

You can install these libraries using `pip`:

```bash
pip install numpy matplotlib
```

## How to Run

1.  **Save the script:** Save the provided Python code as `sinewave-ampling.py` (or any other `.py` filename) in a directory of your choice.

2.  **Open a terminal:** Navigate to the directory where you saved the script.

3.  **Execute the script:**

    ```bash
    python sinewave-ampling.py
    ```

4.  **Enter Frequencies:** The tool will prompt you to enter the signal frequency (in Hz) and the sampling rate (in Hz).

    ```text
    --- Sine Wave Sampling Visualizer ---
    Enter signal frequency (Hz): 35
    Enter sampling rate (Hz): 700
    ```

5.  **View the Plot:** A `matplotlib` window will appear, displaying the comparison plot.

6.  **Analyze Another Signal:** After closing the plot, the tool will ask if you want to analyze another signal. Enter `y` to continue or `n` to exit.

## Understanding the Plot

-   **Ideal Continuous Wave (Blue Dashed Line):** Represents the original, un-sampled sine wave.
-   **Zero-Order Hold (Square) (Crimson Line):** Shows how the sampled values are held constant until the next sample point, creating a staircase-like approximation of the original signal.
-   **Sample Points (Dark Red Dots):** Indicate the exact moments in time when the signal's amplitude was measured.
-   **Nyquist Warning:** If the sampling rate is less than twice the signal frequency, a warning message will appear at the bottom of the plot, indicating that aliasing may occur.
-   **FFT-based Reconstruction (Green Line):** Shows a smoother reconstruction of the signal achieved by performing an Inverse Fast Fourier Transform (IFFT) on the zero-padded spectrum of the sampled signal. This method aims to recover the original continuous signal more accurately than zero-order hold, especially when the Nyquist criterion is met.

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