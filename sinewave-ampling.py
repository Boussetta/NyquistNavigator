"""
AliasingAtlas: A pedagogical tool for visualizing signal sampling and aliasing.

This module provides an interactive graphical interface to explore the 
Nyquist-Shannon sampling theorem using base signals and harmonics.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
from typing import Union, Optional, List

class AliasingToolbox:
    """An interactive toolbox for visualizing signal sampling and reconstruction.

    Attributes:
        f_sig_max (float): Maximum allowed frequency for the base signal.
        f_samp_max (float): Maximum allowed sampling frequency.
        num_continuous_points (int): Number of points for the ideal continuous signal.
        phase (float): Phase offset for the base signal.
    """

    def __init__(self) -> None:
        """Initializes the toolbox, sets up the plot layout and interactive sliders."""
        # 1. Initialize core state
        self.f_sig_max = 50.0
        self.f_samp_max = 1500.0
        self.num_continuous_points = 1000
        self.phase = np.pi / 4

        # 2. Setup Figure and Axes
        self.fig = plt.figure(figsize=(14, 10))
        plt.subplots_adjust(bottom=0.35, hspace=0.4)

        # Time Domain Subplot
        self.ax_time = self.fig.add_subplot(2, 1, 1)
        self.ax_time.set_title("AliasingAtlas: Time Domain", fontweight='bold')
        self.ax_time.grid(True, linestyle=':', alpha=0.6)

        # Frequency Domain Subplot
        self.ax_freq = self.fig.add_subplot(2, 1, 2)
        self.ax_freq.set_title("Frequency Domain: Magnitude Spectrum", fontweight='bold')
        self.ax_freq.grid(True, linestyle=':', alpha=0.6)
        # Fix the frequency axis to prevent flashing/warping
        self.ax_freq.set_xlim(0, self.f_samp_max / 2 + 100)
        self.ax_freq.set_ylim(0, 1.2)

        # 3. Initialize Plot Elements
        self.line_cont, = self.ax_time.plot([], [], 'b--', alpha=0.4, label='Ideal Continuous')
        self.line_step, = self.ax_time.step([], [], where='post', color='crimson', alpha=0.6, label='Zero-Order Hold')
        self.line_fft, = self.ax_time.plot([], [], 'g-', linewidth=2, label='FFT Reconstruction')
        self.dots_samp = self.ax_time.scatter([], [], color='darkred', s=20, zorder=3)
        self.line_spec, = self.ax_freq.plot([], [], 'ro-', markersize=4, label='Sampled Peak')
        self.nyquist_line = self.ax_freq.axvline(0, color='orange', linestyle='--', label='Nyquist Limit')
        self.true_freq_line = self.ax_freq.axvline(0, color='blue', alpha=0.3, label='True Signal Freq')

        self.ax_time.legend(loc='upper right', fontsize='small')
        self.ax_freq.legend(loc='upper right', fontsize='small')

        # 4. Create Sliders
        slider_color = 'lightsteelblue'
        self.ax_f_sig = plt.axes([0.2, 0.26, 0.6, 0.02], facecolor=slider_color)
        self.ax_f_harm = plt.axes([0.2, 0.22, 0.6, 0.02], facecolor=slider_color)
        self.ax_a_harm = plt.axes([0.2, 0.18, 0.6, 0.02], facecolor=slider_color)
        self.ax_f_samp = plt.axes([0.2, 0.14, 0.6, 0.02], facecolor=slider_color)
        self.ax_bits = plt.axes([0.2, 0.10, 0.6, 0.02], facecolor=slider_color)
        self.ax_window = plt.axes([0.85, 0.05, 0.1, 0.1], facecolor=slider_color)

        self.s_f_sig = Slider(self.ax_f_sig, 'Base Freq (Hz)', 1.0, self.f_sig_max, valinit=10.0)
        self.s_f_harm = Slider(self.ax_f_harm, 'Harmonic (Hz)', 1.0, self.f_sig_max * 2, valinit=20.0)
        self.s_f_harm_amp = Slider(self.ax_a_harm, 'Harmonic Amp', 0.0, 1.0, valinit=0.0)
        self.s_f_samp = Slider(self.ax_f_samp, 'Sampling (Hz)', 5.0, self.f_samp_max, valinit=50.0)
        self.s_bits = Slider(self.ax_bits, 'Bit Depth', 2, 16, valinit=16, valstep=1)
        self.w_radio = RadioButtons(self.ax_window, ('None', 'Hamming', 'Hann'))

        # 5. Connect Callbacks
        self.s_f_sig.on_changed(self.update)
        self.s_f_harm.on_changed(self.update)
        self.s_f_harm_amp.on_changed(self.update)
        self.s_f_samp.on_changed(self.update)
        self.s_bits.on_changed(self.update)
        self.w_radio.on_clicked(self.update)

        self.status_text = self.fig.text(0.5, 0.01, '', ha='center', bbox=dict(facecolor='white', alpha=0.8))
        self.update(None)

    def calculate_signal(self, t: Union[np.ndarray, List[float]], f_sig: float, f_harm: float, a_harm: float) -> np.ndarray:
        """Calculates a multi-tone signal consisting of a base frequency and a harmonic.

        Args:
            t (Union[np.ndarray, List[float]]): Array of time points.
            f_sig (float): Frequency of the base signal in Hz.
            f_harm (float): Frequency of the harmonic component in Hz.
            a_harm (float): Amplitude of the harmonic component (relative to base).

        Returns:
            np.ndarray: The combined signal values.

        Raises:
            TypeError: If input types are not numeric or array-like.
            ValueError: If frequencies are not positive or amplitude is negative.
        """
        # Input Validation
        if not isinstance(t, (np.ndarray, list)):
            raise TypeError("Time array 't' must be a numpy array or list.")
        
        params = {'f_sig': f_sig, 'f_harm': f_harm, 'a_harm': a_harm}
        for name, value in params.items():
            if not isinstance(value, (int, float, np.number)):
                raise TypeError(f"Parameter '{name}' must be numeric.")
        
        if f_sig <= 0 or f_harm <= 0:
            raise ValueError("Frequencies must be positive values.")
        if a_harm < 0:
            raise ValueError("Harmonic amplitude cannot be negative.")

        # Multi-tone mixing: Base + Harmonic
        base = np.sin(2 * np.pi * f_sig * t + self.phase)
        harm = a_harm * np.sin(2 * np.pi * f_harm * t)
        return base + harm

    def update(self, val: Optional[float]) -> None:
        """Updates all plot layers and status indicators based on current slider values.

        Args:
            val (Optional[float]): Value from the slider that triggered the update.
                This is passed by Matplotlib's callback mechanism.
        """
        f_sig = self.s_f_sig.val
        f_harm = self.s_f_harm.val
        a_harm = self.s_f_harm_amp.val
        f_samp = self.s_f_samp.val
        bits = int(self.s_bits.val)
        window_type = self.w_radio.value_selected

        # Validation for runtime safety
        if f_sig <= 0 or f_samp <= 0:
            return

        # 1. Setup Time
        duration = 3 / f_sig
        t_cont = np.linspace(0, duration, self.num_continuous_points)
        y_cont = self.calculate_signal(t_cont, f_sig, f_harm, a_harm)

        # 2. Sampled Signal
        num_samples = int(np.floor(duration * f_samp))
        if num_samples < 2: num_samples = 2
        t_samp = np.linspace(0, (num_samples - 1) / f_samp, num_samples)
        y_samp = self.calculate_signal(t_samp, f_sig, f_harm, a_harm)

        # 3. Bit-Depth Quantization
        levels = 2**bits
        y_samp = np.round((y_samp + 1) / 2 * (levels - 1)) / (levels - 1) * 2 - 1

        # 4. Windowing
        N_samp = len(y_samp)
        if window_type == 'Hamming':
            window = np.hamming(N_samp)
        elif window_type == 'Hann':
            window = np.hanning(N_samp)
        else:
            window = np.ones(N_samp)
        
        y_samp_fft_input = y_samp * window

        # 5. FFT Reconstruction
        Y_fft = np.fft.fft(y_samp_fft_input)
        Y_padded = np.zeros(self.num_continuous_points, dtype=complex)
        half = (N_samp + 1) // 2
        Y_padded[:half] = Y_fft[:half]
        Y_padded[self.num_continuous_points - (N_samp // 2):] = Y_fft[N_samp - (N_samp // 2):]
        y_recon = np.fft.ifft(Y_padded).real * (self.num_continuous_points / N_samp)

        # 6. Spectrum Visualization
        freqs = np.fft.rfftfreq(N_samp, 1/f_samp)
        mags = np.abs(np.fft.rfft(y_samp_fft_input)) / N_samp

        # Update Elements
        self.line_cont.set_data(t_cont, y_cont)
        self.line_step.set_data(t_samp, y_samp)
        self.line_fft.set_data(t_cont, y_recon)
        self.dots_samp.set_offsets(np.c_[t_samp, y_samp])
        self.ax_time.set_xlim(0, duration)
        self.ax_time.set_ylim(-1.3 - a_harm, 1.3 + a_harm)

        self.line_spec.set_data(freqs, mags)
        self.nyquist_line.set_xdata([f_samp/2, f_samp/2])
        self.true_freq_line.set_xdata([f_sig, f_sig])

        # 5. Status and Warnings
        rmse = np.sqrt(np.mean((y_cont - y_recon)**2))
        is_aliased = f_samp < 2 * max(f_sig, f_harm if a_harm > 0 else 0)
        
        msg = f"RMSE: {rmse:.4f}"
        if is_aliased:
            msg += " | WARNING: ALIASING DETECTED"
            self.status_text.get_bbox_patch().set_facecolor('orange')
        else:
            self.status_text.get_bbox_patch().set_facecolor('lightgreen')
        
        self.status_text.set_text(msg)
        self.fig.canvas.draw_idle()

    def show(self) -> None:
        """Displays the interactive plot window."""
        plt.show()

if __name__ == "__main__":
    app = AliasingToolbox()
    app.show()