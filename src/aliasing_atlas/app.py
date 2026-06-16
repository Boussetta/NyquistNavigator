"""
AliasingAtlas: A pedagogical tool for visualizing signal sampling and aliasing.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, CheckButtons, Button
from typing import Union, Optional, List, Dict, Type
from abc import ABC, abstractmethod

# Optional import for audio playback in Jupyter/Colab environments
try:
    from IPython.display import Audio, display
except ImportError:
    Audio, display = None, None # Fallback for non-IPython environments


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
        harm = self.a_harm * np.sign(np.sin(2 * np.pi * self.f_harm * self.t))
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

        self.last_y_samp: Optional[np.ndarray] = None
        self.last_f_samp: Optional[float] = None

        self.fig = plt.figure(figsize=(14, 10))
        plt.subplots_adjust(bottom=0.28, hspace=0.7)

        self.ax_time = self.fig.add_subplot(3, 1, 1)
        self.ax_time.set_title("AliasingAtlas: Time Domain", fontweight='bold')
        self.ax_time.grid(True, linestyle=':', alpha=0.6)

        self.ax_freq = self.fig.add_subplot(3, 1, 2)
        self.ax_freq.set_title("Frequency Domain: Magnitude Spectrum", fontweight='bold')
        self.ax_freq.grid(True, linestyle=':', alpha=0.6)
        self.ax_freq.set_ylabel("Magnitude")
        self.ax_freq.set_xlim(0, self.f_samp_max / 2 + 100)
        self.ax_freq.set_ylim(0, 1.5)

        self.ax_quant = self.fig.add_subplot(3, 1, 3)
        self.ax_quant.set_title("Quantization Error (e = y_quant - y_ideal)", fontweight='bold')
        self.ax_quant.grid(True, linestyle=':', alpha=0.6)
        self.ax_quant.set_ylabel("Error")

        self.line_cont, = self.ax_time.plot([], [], 'b--', alpha=0.4, label='Ideal Continuous')
        self.line_filt, = self.ax_time.plot([], [], 'y-', alpha=0.7, linewidth=1.5, label='AAF Filtered', zorder=2)
        self.line_step, = self.ax_time.step([], [], where='post', color='crimson', alpha=0.6, label='Zero-Order Hold')
        self.line_fft, = self.ax_time.plot([], [], 'g-', linewidth=2, label='FFT Reconstruction')
        self.dots_samp = self.ax_time.scatter([], [], color='darkred', s=20, zorder=3)
        self.line_spec, = self.ax_freq.plot([], [], 'ro-', markersize=4, label='Sampled Peak')
        self.nyquist_line = self.ax_freq.axvline(0, color='orange', linestyle='--', label='Nyquist Limit')
        self.true_freq_line = self.ax_freq.axvline(0, color='blue', alpha=0.4, linestyle='--', label='Intended Freq (Ghost)')
        self.alias_indicator = self.ax_freq.axvline(0, color='magenta', alpha=0.6, linestyle=':', label='Predicted Alias')
        self.line_quant, = self.ax_quant.plot([], [], 'm.-', markersize=3, alpha=0.7, label='Error')

        self.ax_time.legend(loc='upper right', fontsize='small')
        self.ax_freq.legend(loc='upper right', fontsize='small')

        slider_color = 'lightsteelblue'
        self.ax_f_sig = plt.axes([0.12, 0.18, 0.32, 0.015], facecolor=slider_color)
        self.ax_f_harm = plt.axes([0.12, 0.14, 0.32, 0.015], facecolor=slider_color)
        self.ax_a_harm = plt.axes([0.12, 0.10, 0.32, 0.015], facecolor=slider_color)
        self.ax_phase = plt.axes([0.58, 0.18, 0.32, 0.015], facecolor=slider_color)
        self.ax_f_samp = plt.axes([0.58, 0.14, 0.32, 0.015], facecolor=slider_color)
        self.ax_bits = plt.axes([0.58, 0.10, 0.32, 0.015], facecolor=slider_color)
        self.ax_window = plt.axes([0.10, 0.02, 0.12, 0.06], facecolor=slider_color)
        self.ax_wave = plt.axes([0.25, 0.02, 0.12, 0.06], facecolor=slider_color)
        self.ax_aaf = plt.axes([0.40, 0.02, 0.08, 0.06], facecolor=slider_color)
        self.ax_db_scale = plt.axes([0.50, 0.02, 0.08, 0.06], facecolor=slider_color)
        self.ax_play_audio = plt.axes([0.60, 0.02, 0.08, 0.06], facecolor=slider_color)

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
        self.w_aaf = CheckButtons(self.ax_aaf, ('AAF On',), [False])
        self.w_db = CheckButtons(self.ax_db_scale, ('dB Scale',), [False])
        self.btn_play_audio = Button(self.ax_play_audio, 'Play Audio')

        self.s_f_sig.on_changed(self.update)
        self.s_f_harm.on_changed(self.update)
        self.s_f_harm_amp.on_changed(self.update)
        self.s_phase.on_changed(self.update)
        self.s_f_samp.on_changed(self.update)
        self.s_bits.on_changed(self.update)
        self.w_radio.on_clicked(self.update)
        self.w_wave.on_clicked(self.update)
        self.w_aaf.on_clicked(self.update)
        self.w_db.on_clicked(self.update)
        self.btn_play_audio.on_clicked(self._play_audio_callback)

        self.status_text = self.fig.text(0.5, 0.01, '', ha='center', bbox=dict(facecolor='white', alpha=0.8))
        self.update(None)

    def _play_audio_callback(self, event) -> None:
        """Callback for the Play Audio button."""
        if Audio is None or display is None: # Check if IPython.display is available
            self.status_text.set_text("Audio playback requires IPython (Notebook environment).")
            self.status_text.get_bbox_patch().set_facecolor('orange')
            self.fig.canvas.draw_idle()
            return

        # Pedagogical improvement: Fetch current parameters to generate 
        # a longer audio sample (1.5s) so the progress bar is visible and useful.
        # Fetch current slider values
        f_sig = self.s_f_sig.val
        f_harm = self.s_f_harm.val
        a_harm = self.s_f_harm_amp.val
        phase = self.s_phase.val
        f_samp = self.s_f_samp.val
        bits = int(self.s_bits.val)
        wave_type = self.w_wave.value_selected

        # Ensure f_samp is not zero or too small for audio generation
        if f_samp <= 0:
            self.status_text.set_text("Cannot play audio: Sampling frequency must be greater than 0.")
            self.status_text.get_bbox_patch().set_facecolor('red')
            self.fig.canvas.draw_idle()
            return

        # Generate 1.5 seconds of the signal for audio playback
        # Ensure at least 2 samples for linspace to work correctly and produce sound
        num_audio_samples = max(2, int(1.5 * f_samp)) 
        t_audio = np.linspace(0, 1.5, num_audio_samples)
        
        if len(t_audio) == 0:
            self.status_text.set_text("Cannot generate audio: insufficient samples for given sampling rate.")
            self.status_text.get_bbox_patch().set_facecolor('red')
            self.fig.canvas.draw_idle()
            return

        # Generate 1.5 seconds of the signal
        y_audio_ideal = SignalRegistry.create_signal(wave_type, t_audio, f_sig, f_harm, a_harm, phase)
        
        # Apply the current bit-depth quantization
        levels = 2**bits
        # Ensure levels-1 is not zero to avoid division by zero if bits=1 (though slider min is 2)
        divisor = (levels - 1) if (levels - 1) > 0 else 1
        y_audio_quant = np.round((y_audio_ideal + 1) / 2 * divisor) / divisor * 2 - 1
        
        # Normalize to prevent clipping
        max_v = np.max(np.abs(y_audio_quant))
        audio_data = y_audio_quant / max_v if max_v > 0 else y_audio_quant

        if len(audio_data) == 0:
            self.status_text.set_text("Cannot play audio: generated signal is empty.")
            self.status_text.get_bbox_patch().set_facecolor('red')
            self.fig.canvas.draw_idle()
            return

        # Debugging prints to confirm data before playback
        print(f"--- Audio Playback Debug ---")
        print(f"Audio data length: {len(audio_data)}")
        print(f"Audio sampling rate: {int(f_samp)}")
        print(f"Max absolute value in audio data: {max_v}")
        print(f"----------------------------")

        # This renders the HTML5 player with a progress bar in the Colab output area
        display(Audio(data=audio_data, rate=int(f_samp), autoplay=True))
        
        self.status_text.set_text(f"Audio player for {wave_type} generated below. Playing...")
        self.fig.canvas.draw_idle()

    def update(self, val: Optional[float]) -> None:
        f_sig = self.s_f_sig.val
        f_harm = self.s_f_harm.val
        a_harm = self.s_f_harm_amp.val
        phase = self.s_phase.val
        f_samp = self.s_f_samp.val
        bits = int(self.s_bits.val)
        window_type = self.w_radio.value_selected
        wave_type = self.w_wave.value_selected
        aaf_on = self.w_aaf.get_status()[0]
        db_on = self.w_db.get_status()[0]

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

        # Apply Ideal Anti-Aliasing Filter (Brick Wall at Fs/2)
        if aaf_on:
            # Pedagogical Step: Filter the 'analog' signal before sampling
            n = len(t_cont)
            dt = t_cont[1] - t_cont[0]
            yf = np.fft.fft(y_cont)
            xf = np.fft.fftfreq(n, dt)
            
            # Zero out frequencies above Nyquist limit
            yf[np.abs(xf) > f_samp / 2] = 0
            y_filt_cont = np.fft.ifft(yf).real
        else:
            y_filt_cont = y_cont

        num_samples = int(np.floor(duration * f_samp))
        if num_samples < 2: num_samples = 2
        t_samp = np.linspace(0, (num_samples - 1) / f_samp, num_samples)

        if aaf_on:
            # Sample the filtered 'analog' signal
            y_samp_ideal = np.interp(t_samp, t_cont, y_filt_cont)
            self.line_filt.set_visible(True)
        else:
            # Sample the raw signal
            y_samp_ideal = SignalRegistry.create_signal(wave_type, t_samp, f_sig, f_harm, a_harm, phase)
            self.line_filt.set_visible(False)

        levels = 2**bits
        y_samp = np.round((y_samp_ideal + 1) / 2 * (levels - 1)) / (levels - 1) * 2 - 1
        
        # Store for audio playback
        self.last_y_samp = y_samp
        self.last_f_samp = f_samp

        # Quantization Error: Difference between quantized and ideal samples
        quant_error = y_samp - y_samp_ideal

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

        if db_on:
            # Convert to dB, using a floor of 1e-5 (-100dB) to avoid log(0)
            display_mags = 20 * np.log10(np.maximum(mags, 1e-5))
            self.ax_freq.set_ylabel("Magnitude (dB)")
            self.ax_freq.set_ylim(-105, 10)
        else:
            display_mags = mags
            self.ax_freq.set_ylabel("Magnitude")
            self.ax_freq.set_ylim(0, 1.5)

        self.line_cont.set_data(t_cont, y_cont)
        self.line_filt.set_data(t_cont, y_filt_cont)
        self.line_step.set_data(t_samp, y_samp)
        self.line_fft.set_data(t_cont, y_recon)
        self.dots_samp.set_offsets(np.c_[t_samp, y_samp])
        self.ax_time.set_xlim(0, duration)
        self.ax_time.set_ylim(-1.3 - a_harm, 1.3 + a_harm)

        # Update Quantization Plot
        self.line_quant.set_data(t_samp, quant_error)
        self.ax_quant.set_xlim(0, duration)
        self.ax_quant.set_ylim(-1.5/(levels-1 if levels>1 else 1), 1.5/(levels-1 if levels>1 else 1))

        self.line_spec.set_data(freqs, display_mags)
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
            
        # Refined aliasing check: Nyquist requires f_samp > 2 * max_freq
        is_aliased = f_samp < 2 * max_freq

        # Update ghost indicators for folding effect visualization
        self.true_freq_line.set_xdata([max_freq, max_freq])
        
        # The "folded" frequency math: f_alias = | f_true - f_samp * round(f_true / f_samp) |
        f_folded = np.abs(max_freq - f_samp * np.round(max_freq / f_samp))
        self.alias_indicator.set_xdata([f_folded, f_folded])
        self.alias_indicator.set_visible(is_aliased)

        # Dynamic X-axis to visualize the frequency folding from "outside" the Nyquist limit
        self.ax_freq.set_xlim(0, max(f_samp/2 + 20, max_freq + 20))

        noise = y_cont - y_recon
        rmse = np.sqrt(np.mean(noise**2))
        signal_power = np.mean(y_cont**2)
        noise_power = np.mean(noise**2)
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 100
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
