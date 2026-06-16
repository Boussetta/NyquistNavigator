"""
AliasingAtlas: A pedagogical tool for visualizing signal sampling and aliasing.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
from typing import Union, Optional, List, Dict, Type
from abc import ABC, abstractmethod


# --- Signal Generation Classes ---
class Signal(ABC):
    """Abstract base class for all signal types."""
    def __init__(self, t: Union[np.ndarray, List[float]], f_sig: float, f_harm: float, a_harm: float, phase: float):
        self.t = t
        self.f_sig = f_sig
        self.f_harm = f_harm
        self.a_harm = a_harm
        self.phase = phase

    @abstractmethod
    def calculate(self) -> np.ndarray:
        """Calculates the signal waveform."""
        pass

class SineWave(Signal):
    def calculate(self) -> np.ndarray:
        base = np.sin(2 * np.pi * self.f_sig * self.t + self.phase)
        harm = self.a_harm * np.sin(2 * np.pi * self.f_harm * self.t)
        return base + harm

class SquareWave(Signal):
    def calculate(self) -> np.ndarray:
        base = np.sign(np.sin(2 * np.pi * self.f_sig * self.t + self.phase))
        harm = self.a_harm * np.sign(np.pi * self.f_harm * self.t) # Corrected to use np.sign(np.sin(...))
        return base + harm

class SawtoothWave(Signal):
    def calculate(self) -> np.ndarray:
        # custom sawtooth: 2 * (t * f + p - floor(0.5 + t * f + p))
        base = 2 * (self.f_sig * self.t + self.phase/(2*np.pi) - np.floor(0.5 + self.f_sig * self.t + self.phase/(2*np.pi)))
        harm = self.a_harm * 2 * (self.f_harm * self.t - np.floor(0.5 + self.f_harm * self.t))
        return base + harm

class AMWave(Signal):
    def calculate(self) -> np.ndarray:
        # f_sig: Carrier, f_harm: Message, a_harm: Modulation Index
        # Note: a_harm here acts as the modulation index.
        base = (1 + self.a_harm * np.sin(2 * np.pi * self.f_harm * self.t)) * np.sin(2 * np.pi * self.f_sig * self.t + self.phase)
        return base

class FMWave(Signal):
    def calculate(self) -> np.ndarray:
        # f_sig: Carrier, f_harm: Message, a_harm: Modulation Index (beta)
        # Note: a_harm here acts as the modulation index (beta).
        base = np.sin(2 * np.pi * self.f_sig * self.t + self.phase + self.a_harm * np.sin(2 * np.pi * self.f_harm * self.t))
        return base

class SignalRegistry:
    """A registry for creating different types of signals."""
    _signals: Dict[str, Type[Signal]] = {}

    @classmethod
    def register_signal(cls, name: str, signal_class: Type[Signal]):
        if not issubclass(signal_class, Signal):
            raise ValueError("Registered class must inherit from Signal")
        cls._signals[name] = signal_class

    @classmethod
    def create_signal(cls, wave_type: str, t: Union[np.ndarray, List[float]], f_sig: float, f_harm: float, a_harm: float, phase: float) -> np.ndarray:
        signal_class = cls._signals.get(wave_type)
        if signal_class:
            return signal_class(t, f_sig, f_harm, a_harm, phase).calculate()
        else:
            # For unknown types, return a zero signal or raise an error
            return np.zeros_like(t)

# Register the signal types
SignalRegistry.register_signal('Sine', SineWave)
SignalRegistry.register_signal('Square', SquareWave)
SignalRegistry.register_signal('Sawtooth', SawtoothWave)
SignalRegistry.register_signal('AM', AMWave)
SignalRegistry.register_signal('FM', FMWave)

# --- End Signal Generation Classes ---


class AliasingToolbox:
    """
    An interactive toolbox for visualizing signal sampling and reconstruction.
    """

    def __init__(self) -> None:
        self.f_sig_max = 50.0
        self.f_samp_max = 1500.0
        self.num_continuous_points = 1000
        self.phase = np.pi / 4

        self.fig = plt.figure(figsize=(14, 10))
        plt.subplots_adjust(bottom=0.35, hspace=0.45)

        self.ax_time = self.fig.add_subplot(2, 1, 1)
        self.ax_time.set_title("AliasingAtlas: Time Domain", fontweight='bold')
        self.ax_time.grid(True, linestyle=':', alpha=0.6)

        self.ax_freq = self.fig.add_subplot(2, 1, 2)
        self.ax_freq.set_title("Frequency Domain: Magnitude Spectrum", fontweight='bold')
        self.ax_freq.grid(True, linestyle=':', alpha=0.6)
        self.ax_freq.set_xlim(0, self.f_samp_max / 2 + 100)
        self.ax_freq.set_ylim(0, 1.2)

        self.line_cont, = self.ax_time.plot([], [], 'b--', alpha=0.4, label='Ideal Continuous')
        self.line_step, = self.ax_time.step([], [], where='post', color='crimson', alpha=0.6, label='Zero-Order Hold')
        self.line_fft, = self.ax_time.plot([], [], 'g-', linewidth=2, label='FFT Reconstruction')
        self.dots_samp = self.ax_time.scatter([], [], color='darkred', s=20, zorder=3)
        self.line_spec, = self.ax_freq.plot([], [], 'ro-', markersize=4, label='Sampled Peak')
        self.nyquist_line = self.ax_freq.axvline(0, color='orange', linestyle='--', label='Nyquist Limit')
        self.true_freq_line = self.ax_freq.axvline(0, color='blue', alpha=0.3, label='True Signal Freq')

        self.ax_time.legend(loc='upper right', fontsize='small')
        self.ax_freq.legend(loc='upper right', fontsize='small')

        slider_color = 'lightsteelblue'
        self.ax_f_sig = plt.axes([0.12, 0.26, 0.32, 0.02], facecolor=slider_color)
        self.ax_f_harm = plt.axes([0.12, 0.21, 0.32, 0.02], facecolor=slider_color)
        self.ax_a_harm = plt.axes([0.12, 0.16, 0.32, 0.02], facecolor=slider_color)
        self.ax_phase = plt.axes([0.58, 0.26, 0.32, 0.02], facecolor=slider_color)
        self.ax_f_samp = plt.axes([0.58, 0.21, 0.32, 0.02], facecolor=slider_color)
        self.ax_bits = plt.axes([0.58, 0.16, 0.32, 0.02], facecolor=slider_color)
        self.ax_window = plt.axes([0.12, 0.03, 0.15, 0.08], facecolor=slider_color)
        self.ax_wave = plt.axes([0.35, 0.03, 0.15, 0.08], facecolor=slider_color)

        self.s_f_sig = Slider(self.ax_f_sig, 'Base Freq (Hz)', 1.0, self.f_sig_max, valinit=10.0)
        self.s_f_harm = Slider(self.ax_f_harm, 'Harmonic (Hz)', 1.0, self.f_sig_max * 2, valinit=20.0)
        self.s_f_harm_amp = Slider(self.ax_a_harm, 'Harmonic Amp', 0.0, 1.0, valinit=0.0)
        self.s_phase = Slider(self.ax_phase, 'Phase', 0, 2*np.pi, valinit=np.pi/4)
        self.s_f_samp = Slider(self.ax_f_samp, 'Sampling (Hz)', 5.0, self.f_samp_max, valinit=50.0)
        self.s_bits = Slider(self.ax_bits, 'Bit Depth', 2, 16, valinit=16, valstep=1)

        self.w_radio = RadioButtons(self.ax_window, ('None', 'Hamming', 'Hann'))
        self.ax_window.set_title("Window", fontsize=10)
        self.w_wave = RadioButtons(self.ax_wave, tuple(SignalRegistry._signals.keys()))
        self.ax_wave.set_title("Waveform", fontsize=10)

        self.s_f_sig.on_changed(self.update)
        self.s_f_harm.on_changed(self.update)
        self.s_f_harm_amp.on_changed(self.update)
        self.s_phase.on_changed(self.update)
        self.s_f_samp.on_changed(self.update)
        self.s_bits.on_changed(self.update)
        self.w_radio.on_clicked(self.update)
        self.w_wave.on_clicked(self.update)

        self.status_text = self.fig.text(0.5, 0.01, '', ha='center', bbox=dict(facecolor='white', alpha=0.8))
        self.update(None)

    def update(self, val: Optional[float]) -> None:
        f_sig = self.s_f_sig.val
        f_harm = self.s_f_harm.val
        a_harm = self.s_f_harm_amp.val
        phase = self.s_phase.val
        f_samp = self.s_f_samp.val
        bits = int(self.s_bits.val)
        window_type = self.w_radio.value_selected
        wave_type = self.w_wave.value_selected

        if f_sig <= 0 or f_samp <= 0: return

        # Update slider labels based on wave type for pedagogical clarity
        if wave_type in ['AM', 'FM']:
            self.s_f_sig.label.set_text('Carrier Freq (Hz)')
            self.s_f_harm.label.set_text('Message Freq (Hz)')
            self.s_f_harm_amp.label.set_text('Mod Index (β/m)')
        else:
            self.s_f_sig.label.set_text('Base Freq (Hz)')
            self.s_f_harm.label.set_text('Harmonic (Hz)')
            self.s_f_harm_amp.label.set_text('Harmonic Amp')
        self.fig.canvas.draw_idle()

        duration = 3 / f_sig
        t_cont = np.linspace(0, duration, self.num_continuous_points)
        # Use the SignalRegistry to create and calculate the continuous signal
        y_cont = SignalRegistry.create_signal(wave_type, t_cont, f_sig, f_harm, a_harm, phase)

        num_samples = int(np.floor(duration * f_samp))
        if num_samples < 2: num_samples = 2
        t_samp = np.linspace(0, (num_samples - 1) / f_samp, num_samples)
        # Use the SignalRegistry to create and calculate the sampled signal
        y_samp = SignalRegistry.create_signal(wave_type, t_samp, f_sig, f_harm, a_harm, phase)

        levels = 2**bits
        y_samp = np.round((y_samp + 1) / 2 * (levels - 1)) / (levels - 1) * 2 - 1

        N_samp = len(y_samp)
        if window_type == 'Hamming': window = np.hamming(N_samp)
        elif window_type == 'Hann': window = np.hanning(N_samp)
        else: window = np.ones(N_samp)
        
        y_samp_fft_input = y_samp * window

        Y_fft = np.fft.fft(y_samp_fft_input)
        Y_padded = np.zeros(self.num_continuous_points, dtype=complex)
        half = (N_samp + 1) // 2
        Y_padded[:half] = Y_fft[:half]
        Y_padded[self.num_continuous_points - (N_samp // 2):] = Y_fft[N_samp - (N_samp // 2):]
        y_recon = np.fft.ifft(Y_padded).real * (self.num_continuous_points / N_samp)

        freqs = np.fft.rfftfreq(N_samp, 1/f_samp)
        mags = np.abs(np.fft.rfft(y_samp_fft_input)) / N_samp

        self.line_cont.set_data(t_cont, y_cont)
        self.line_step.set_data(t_samp, y_samp)
        self.line_fft.set_data(t_cont, y_recon)
        self.dots_samp.set_offsets(np.c_[t_samp, y_samp])
        self.ax_time.set_xlim(0, duration)
        self.ax_time.set_ylim(-1.3 - a_harm, 1.3 + a_harm)

        self.line_spec.set_data(freqs, mags)
        self.nyquist_line.set_xdata([f_samp/2, f_samp/2])
        
        # Determine the maximum frequency component for aliasing detection and indicator
        if wave_type == 'AM':
            max_freq = f_sig + f_harm if a_harm > 0 else f_sig
        elif wave_type == 'FM':
            # Carson's Rule approximation for significant bandwidth: BW = 2 * (beta + 1) * fm
            # Significant frequency edge is f_carrier + (beta + 1) * f_message
            max_freq = f_sig + (a_harm + 1) * f_harm if a_harm > 0 else f_sig
        else:
            max_freq = max(f_sig, f_harm if a_harm > 0 else 0)
            
        self.true_freq_line.set_xdata([max_freq, max_freq])

        noise = y_cont - y_recon
        rmse = np.sqrt(np.mean(noise**2))
        signal_power = np.mean(y_cont**2)
        noise_power = np.mean(noise**2)
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 100

        # Refined aliasing check: Nyquist requires f_samp > 2 * max_freq
        is_aliased = f_samp < 2 * max_freq
        
        # Special pedagogical note: Square/Sawtooth waves technically alias at any sampling rate 
        # because of their infinite harmonics, but we focus on the modeled components here.
        
        msg = f"RMSE: {rmse:.4f} | SNR: {snr:.1f} dB | Max Freq: {max_freq:.1f} Hz"
        if is_aliased:
            msg += " | WARNING: ALIASING DETECTED"
            self.status_text.get_bbox_patch().set_facecolor('orange')
        else:
            self.status_text.get_bbox_patch().set_facecolor('lightgreen')
        
        self.status_text.set_text(msg)
        self.fig.canvas.draw_idle()

    def show(self) -> None:
        plt.show()
