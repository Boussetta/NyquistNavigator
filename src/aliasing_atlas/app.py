"""
AliasingAtlas: A pedagogical tool for visualizing signal sampling and aliasing.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, Button
from typing import Optional
try:
    from scipy import signal as sp_signal
except ImportError:
    sp_signal = None
from .signals import SignalRegistry

# Optional import for audio playback in Jupyter/Colab environments
try:
    from IPython.display import Audio, display
except ImportError:
    Audio, display = None, None # Fallback for non-IPython environments

# Optional import for local desktop audio playback
try:
    import sounddevice as sd
except ImportError:
    sd = None

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
        plt.subplots_adjust(bottom=0.35, hspace=0.4, wspace=0.25)

        self.ax_time = self.fig.add_subplot(2, 2, 1)
        self.ax_time.set_title("AliasingAtlas: Time Domain", fontweight='bold')
        self.ax_time.grid(True, linestyle=':', alpha=0.6)

        self.ax_freq = self.fig.add_subplot(2, 2, 2)
        self.ax_freq.set_title("Frequency Domain: Magnitude Spectrum", fontweight='bold')
        self.ax_freq.grid(True, linestyle=':', alpha=0.6)
        self.ax_freq.set_ylabel("Magnitude")
        self.ax_freq.set_xlim(0, self.f_samp_max / 2 + 100)
        self.ax_freq.set_ylim(0, 1.5)

        self.ax_phase = self.fig.add_subplot(2, 2, 3)
        self.ax_phase.set_title("Frequency Domain: Phase Spectrum", fontweight='bold')
        self.ax_phase.grid(True, linestyle=':', alpha=0.6)
        self.ax_phase.set_ylabel("Phase (rad)")
        self.ax_phase.set_ylim(-np.pi - 0.5, np.pi + 0.5)

        self.ax_quant = self.fig.add_subplot(2, 2, 4)
        self.ax_quant.set_title("Quantization Error (e = y_quant - y_ideal)", fontweight='bold')
        self.ax_quant.grid(True, linestyle=':', alpha=0.6)
        self.ax_quant.set_ylabel("Error Amp")

        self.line_cont, = self.ax_time.plot([], [], 'b--', alpha=0.4, label='Ideal Continuous')
        self.line_filt, = self.ax_time.plot([], [], 'y-', alpha=0.7, linewidth=1.5, label='AAF Filtered', zorder=2)
        self.line_step, = self.ax_time.step([], [], where='post', color='crimson', alpha=0.6, label='Zero-Order Hold')
        self.line_fft, = self.ax_time.plot([], [], 'g-', linewidth=2, label='FFT Reconstruction')
        self.dots_samp = self.ax_time.scatter([], [], color='darkred', s=20, zorder=3)
        self.line_spec, = self.ax_freq.plot([], [], 'ro-', markersize=4, label='Sampled Peak')
        self.line_phase, = self.ax_phase.plot([], [], 'go-', markersize=4, label='Phase')
        self.nyquist_line = self.ax_freq.axvline(0, color='orange', linestyle='--', label='Nyquist Limit')
        self.true_freq_line = self.ax_freq.axvline(0, color='blue', alpha=0.4, linestyle='--', label='Intended Freq (Ghost)')
        self.alias_indicator = self.ax_freq.axvline(0, color='magenta', alpha=0.6, linestyle=':', label='Predicted Alias')
        self.line_quant, = self.ax_quant.plot([], [], 'm.-', markersize=3, alpha=0.7, label='Error')

        self.ax_time.legend(loc='upper right', fontsize='small')
        self.ax_freq.legend(loc='upper right', fontsize='small')

        slider_color = 'lightsteelblue'

        # Tab Selection Logic
        self.cax_tabs = plt.axes([0.02, 0.05, 0.10, 0.18], facecolor='whitesmoke')
        self.w_tabs = RadioButtons(self.cax_tabs, ('Signal', 'Sampling', 'Audio'))
        self.cax_tabs.set_title("Navigation", fontsize=10, fontweight='bold')

        # --- Persistent Core Controls (Always Visible) ---
        self.cax_f_sig = plt.axes([0.20, 0.25, 0.28, 0.02], facecolor=slider_color)
        self.cax_f_samp = plt.axes([0.58, 0.25, 0.28, 0.02], facecolor=slider_color)
        self.cax_reset = plt.axes([0.88, 0.24, 0.08, 0.04], facecolor=slider_color)

        self.s_f_sig = Slider(self.cax_f_sig, 'Base Freq (Hz)', 1.0, self.f_sig_max, valinit=10.0)
        self.s_f_samp = Slider(self.cax_f_samp, 'Sampling (Hz)', 5.0, self.f_samp_max, valinit=50.0)
        self.btn_reset = Button(self.cax_reset, 'Reset All')

        # --- TAB: Signal ---
        self.cax_sig_box = plt.axes([0.15, 0.05, 0.65, 0.18], facecolor='whitesmoke', alpha=0.5)
        self.cax_sig_box.set_title("Signal Components", fontsize=10, fontweight='bold')
        self.cax_sig_box.set_xticks([]); self.cax_sig_box.set_yticks([])

        self.cax_f_harm = plt.axes([0.25, 0.16, 0.20, 0.015], facecolor=slider_color)
        self.cax_a_harm = plt.axes([0.25, 0.11, 0.20, 0.015], facecolor=slider_color)
        self.cax_s_phase = plt.axes([0.55, 0.16, 0.20, 0.015], facecolor=slider_color)
        self.cax_n_harm = plt.axes([0.55, 0.11, 0.20, 0.015], facecolor=slider_color)
        self.cax_wave = plt.axes([0.82, 0.05, 0.12, 0.18], facecolor=slider_color)

        self.s_f_harm = Slider(self.cax_f_harm, 'Harmonic (Hz)', 1.0, self.f_sig_max * 2, valinit=20.0)
        self.s_f_harm_amp = Slider(self.cax_a_harm, 'Harmonic Amp', 0.0, 1.0, valinit=0.0)
        self.s_phase = Slider(self.cax_s_phase, 'Phase', 0, 2*np.pi, valinit=np.pi/4)
        self.s_n_harm = Slider(self.cax_n_harm, 'Fourier Harm.', 1, 50, valinit=1, valstep=1)
        self.w_wave = RadioButtons(self.cax_wave, tuple(SignalRegistry.get_signal_names()))
        self.cax_wave.set_title("Waveform", fontsize=10)

        self.tab_signal_axes = [self.cax_sig_box, self.cax_f_harm, self.cax_a_harm, self.cax_s_phase, self.cax_n_harm, self.cax_wave]

        # --- TAB: Sampling ---
        self.cax_quant_box = plt.axes([0.15, 0.05, 0.35, 0.18], facecolor='whitesmoke', alpha=0.5)
        self.cax_quant_box.set_title("Quantization", fontsize=10, fontweight='bold')
        self.cax_quant_box.set_xticks([]); self.cax_quant_box.set_yticks([])

        self.cax_bits = plt.axes([0.22, 0.12, 0.25, 0.015], facecolor=slider_color)
        self.cax_window = plt.axes([0.55, 0.05, 0.10, 0.18], facecolor=slider_color)
        self.cax_aaf = plt.axes([0.68, 0.05, 0.10, 0.18], facecolor=slider_color)
        self.cax_db_scale = plt.axes([0.82, 0.05, 0.12, 0.12], facecolor=slider_color)

        self.s_bits = Slider(self.cax_bits, 'Bit Depth', 2, 16, valinit=16, valstep=1)
        self.w_radio = RadioButtons(self.cax_window, ('None', 'Hamming', 'Hann'))
        self.cax_window.set_title("Window", fontsize=10)
        self.w_aaf = RadioButtons(self.cax_aaf, ('None', 'Ideal', 'Butter'))
        self.cax_aaf.set_title("AAF Filter", fontsize=10)
        self.w_db = RadioButtons(self.cax_db_scale, ('Linear', 'dB Scale'))
        self.cax_db_scale.set_title("Scale", fontsize=10)

        self.tab_sampling_axes = [self.cax_quant_box, self.cax_bits, self.cax_window, self.cax_aaf, self.cax_db_scale]

        # --- TAB: Audio ---
        self.cax_audio_box = plt.axes([0.15, 0.05, 0.35, 0.18], facecolor='whitesmoke', alpha=0.5)
        self.cax_audio_box.set_title("Playback Settings", fontsize=10, fontweight='bold')
        self.cax_audio_box.set_xticks([]); self.cax_audio_box.set_yticks([])

        self.cax_vol = plt.axes([0.25, 0.16, 0.20, 0.015], facecolor=slider_color)
        self.cax_dur = plt.axes([0.25, 0.11, 0.20, 0.015], facecolor=slider_color)
        self.cax_audio_src = plt.axes([0.55, 0.05, 0.15, 0.18], facecolor=slider_color)
        self.cax_play_audio = plt.axes([0.75, 0.10, 0.12, 0.08], facecolor=slider_color)

        self.s_vol = Slider(self.cax_vol, 'Audio Vol', 0.0, 1.0, valinit=0.5)
        self.s_dur = Slider(self.cax_dur, 'Audio Dur (s)', 0.5, 3.0, valinit=1.5)
        self.w_audio_src = RadioButtons(self.cax_audio_src, ('Sampled', 'Recon'))
        self.cax_audio_src.set_title("Audio Source", fontsize=10)
        self.btn_play_audio = Button(self.cax_play_audio, 'Play Audio')

        self.tab_audio_axes = [self.cax_audio_box, self.cax_vol, self.cax_dur, self.cax_audio_src, self.cax_play_audio]

        # Grouping for visibility toggling
        self.tab_groups = {
            'Signal': self.tab_signal_axes,
            'Sampling': self.tab_sampling_axes,
            'Audio': self.tab_audio_axes
        }

        # Setup tab callback
        self.w_tabs.on_clicked(self._tab_callback)
        self._update_tab_visibility('Signal')

        # Register callbacks
        self.s_f_sig.on_changed(self.update)
        self.s_f_harm.on_changed(self.update)
        self.s_f_harm_amp.on_changed(self.update)
        self.s_phase.on_changed(self.update)
        self.s_f_samp.on_changed(self.update)
        self.s_bits.on_changed(self.update)
        self.s_n_harm.on_changed(self.update)
        self.s_vol.on_changed(self.update)
        self.s_dur.on_changed(self.update)
        self.w_radio.on_clicked(self.update)
        self.w_wave.on_clicked(self.update)
        self.w_aaf.on_clicked(self.update)
        self.w_db.on_clicked(self.update)
        self.w_audio_src.on_clicked(self.update)
        self.btn_play_audio.on_clicked(self._play_audio_callback)
        self.btn_reset.on_clicked(self._reset_callback)

        self.status_text = self.fig.text(0.5, 0.01, '', ha='center', bbox=dict(facecolor='white', alpha=0.8))
        self.update(None)

    def _tab_callback(self, label: str) -> None:
        """Handles switching between different navigation tabs."""
        self._update_tab_visibility(label)
        self.fig.canvas.draw()
        self.fig.canvas.draw_idle()

    def _update_tab_visibility(self, active_tab: str) -> None:
        """Sets visibility of axes based on the selected tab."""
        for tab_name, axes_list in self.tab_groups.items():
            is_visible = (tab_name == active_tab)
            for ax in axes_list:
                ax.set_visible(is_visible)
                # Explicitly toggle visibility for internal artists (bullets and labels) 
                # to prevent widgets from "ghosting" when the tab is switched.
                for child in ax.get_children():
                    child.set_visible(is_visible)

    def _reset_callback(self, event) -> None:
        """Resets all widgets to their initial values."""
        self.s_f_sig.reset()
        self.s_f_harm.reset()
        self.s_f_harm_amp.reset()
        self.s_phase.reset()
        self.s_f_samp.reset()
        self.s_bits.reset()
        self.s_n_harm.reset()
        self.s_vol.reset()
        self.s_dur.reset()
        # Reset radio buttons (this triggers 'update' automatically)
        self.w_radio.set_active(0)
        self.w_wave.set_active(0)
        self.w_aaf.set_active(0)
        self.w_audio_src.set_active(0)
        self.w_db.set_active(0)

        self.fig.canvas.draw_idle()

    def _play_audio_callback(self, event) -> None:
        """Callback for the Play Audio button."""
        PLAYBACK_FS = 44100
        DURATION = self.s_dur.val
        VOLUME = self.s_vol.val

        # Fetch current parameters
        f_sig = self.s_f_sig.val
        f_harm = self.s_f_harm.val
        a_harm = self.s_f_harm_amp.val
        phase = self.s_phase.val
        f_samp = self.s_f_samp.val
        bits = int(self.s_bits.val)
        n_harm = int(self.s_n_harm.val)
        wave_type = self.w_wave.value_selected
        aaf_type = self.w_aaf.value_selected
        audio_src = self.w_audio_src.value_selected

        if f_samp <= 0:
            self.status_text.set_text("Cannot play audio: Sampling frequency must be greater than 0.")
            self.status_text.get_bbox_patch().set_facecolor('red')
            self.fig.canvas.draw_idle()
            return

        # 1. Generate discrete samples at f_samp
        num_s = int(DURATION * f_samp)
        if num_s < 2: num_s = 2
        t_s = np.linspace(0, (num_s - 1) / f_samp, num_s)
        num_p = int(DURATION * PLAYBACK_FS)
        t_playback = np.linspace(0, DURATION, num_p)
        
        y_full = SignalRegistry.create_signal(wave_type, t_playback, f_sig, f_harm, a_harm, phase, n_harm)

        if aaf_type == 'Ideal':
            yf = np.fft.fft(y_full)
            xf = np.fft.fftfreq(num_p, 1/PLAYBACK_FS)
            yf[np.abs(xf) > f_samp / 2] = 0
            y_audio_base = np.fft.ifft(yf).real
            y_s = np.interp(t_s, t_playback, y_audio_base)
        elif aaf_type == 'Butter':
            if sp_signal is not None:
                nyq_limit = f_samp / 2
                # Design a 5th order Butterworth filter
                b, a = sp_signal.butter(5, nyq_limit, btype='low', fs=PLAYBACK_FS)
                y_audio_base = sp_signal.lfilter(b, a, y_full)
                y_s = np.interp(t_s, t_playback, y_audio_base)
            else:
                y_s = SignalRegistry.create_signal(wave_type, t_s, f_sig, f_harm, a_harm, phase, n_harm)
        else:
            y_s = SignalRegistry.create_signal(wave_type, t_s, f_sig, f_harm, a_harm, phase, n_harm)
        
        # Apply the current bit-depth quantization
        levels = 2**bits
        divisor = (levels - 1) if (levels - 1) > 0 else 1
        y_s_q = np.round((y_s + 1) / 2 * divisor) / divisor * 2 - 1

        # 2. Process according to source
        if audio_src == 'Sampled':
            # Zero-Order Hold (emulates crimson line sound)
            indices = np.floor(t_playback * f_samp).astype(int)
            indices = np.clip(indices, 0, len(y_s_q) - 1)
            audio_data = y_s_q[indices]
        else: # 'Recon'
            # FFT Reconstruction (emulates green line sound)
            Y_s = np.fft.fft(y_s_q)
            Y_p = np.zeros(num_p, dtype=complex)
            half = (num_s + 1) // 2
            Y_p[:half] = Y_s[:half]
            Y_p[num_p - (num_s // 2):] = Y_s[num_s - (num_s // 2):]
            audio_data = np.fft.ifft(Y_p).real * (num_p / num_s)

        max_v = np.max(np.abs(audio_data))
        audio_data = (audio_data / max_v if max_v > 0 else audio_data) * VOLUME

        # 1. Desktop Playback (Highest priority for local use)
        if sd is not None:
            try:
                # sounddevice works locally (desktop/notebook) without HTML serialization issues
                sd.play(audio_data, PLAYBACK_FS)
                self.status_text.set_text(f"Playing {wave_type} ({audio_src}) via sounddevice...")
                self.fig.canvas.draw_idle()
                return
            except Exception as e:
                print(f"Sounddevice failed: {e}")

        # 2. Notebook Playback (Fallback for Colab/Jupyter widgets)
        if Audio is not None and display is not None:
            # Ensure float32 for maximum compatibility across browser audio engines
            audio_data_32 = audio_data.astype(np.float32)
            
            # Debugging prints
            print(f"--- Audio Playback Debug ---")
            print(f"Signal Length: {DURATION}s | Playback Rate: {PLAYBACK_FS} Hz")
            print(f"Emulated Sampling Rate: {f_samp:.1f} Hz")
            print(f"----------------------------")
            
            # In local Jupyter, the player might appear in the log or a separate area
            display(Audio(data=audio_data_32, rate=PLAYBACK_FS, autoplay=True))
            self.status_text.set_text(f"Audio player for {wave_type} ({audio_src}) generated below.")
        else:
            self.status_text.set_text("Audio failed. Install 'sounddevice' (pip install sounddevice).")
            self.status_text.get_bbox_patch().set_facecolor('orange')
        
        self.fig.canvas.draw_idle()

    def _get_params(self):
        f_sig = self.s_f_sig.val
        f_harm = self.s_f_harm.val
        a_harm = self.s_f_harm_amp.val
        phase = self.s_phase.val
        f_samp = self.s_f_samp.val
        bits = int(self.s_bits.val)
        window_type = self.w_radio.value_selected
        wave_type = self.w_wave.value_selected
        aaf_type = self.w_aaf.value_selected
        db_on = self.w_db.value_selected == 'dB Scale'
        n_harm = int(self.s_n_harm.val)
        return f_sig, f_harm, a_harm, phase, f_samp, bits, window_type, wave_type, aaf_type, db_on, n_harm

    def update(self, val: Optional[float]) -> None:
        params = self._get_params()
        f_sig, f_harm, a_harm, phase, f_samp, bits, window_type, wave_type, aaf_type, db_on, n_harm = params
        if f_sig <= 0 or f_samp <= 0: return

        if wave_type in ['AM', 'FM']:
            self.s_f_sig.label.set_text('Carrier Freq (Hz)')
            self.s_f_harm.label.set_text('Message Freq (Hz)')
            self.s_f_harm_amp.label.set_text('Mod Index (β/m)')
        else:
            self.s_f_sig.label.set_text('Base Freq (Hz)')
            self.s_f_harm.label.set_text('Harmonic (Hz)')
            self.s_f_harm_amp.label.set_text('Harmonic Amp')

        max_freq = SignalRegistry.get_max_freq(wave_type, f_sig, f_harm, a_harm, n_harm)
        
        # Dynamic Plot Adjustment: Ensure high resolution for high frequencies
        self.num_continuous_points = max(1000, int(20 * max_freq))

        duration = 3 / f_sig
        t_cont = np.linspace(0, duration, self.num_continuous_points)
        y_cont = SignalRegistry.create_signal(wave_type, t_cont, f_sig, f_harm, a_harm, phase, n_harm)

        if aaf_type == 'Ideal':
            n = len(t_cont)
            dt = t_cont[1] - t_cont[0]
            yf = np.fft.fft(y_cont)
            xf = np.fft.fftfreq(n, dt)
            yf[np.abs(xf) > f_samp / 2] = 0
            y_filt_cont = np.fft.ifft(yf).real
        elif aaf_type == 'Butter':
            if sp_signal is not None:
                nyq_limit = f_samp / 2
                # Adaptive fs for the digital filter design
                b, a = sp_signal.butter(5, nyq_limit, btype='low', fs=1/(t_cont[1]-t_cont[0]))
                y_filt_cont = sp_signal.lfilter(b, a, y_cont)
            else:
                y_filt_cont = y_cont
        else:
            y_filt_cont = y_cont

        num_samples = max(2, int(np.floor(duration * f_samp)))
        if num_samples < 2: num_samples = 2
        t_samp = np.linspace(0, (num_samples - 1) / f_samp, num_samples)

        if aaf_type != 'None':
            # Sample the filtered 'analog' signal
            y_samp_ideal = np.interp(t_samp, t_cont, y_filt_cont)
            self.line_filt.set_visible(True)
        else:
            # Sample the raw signal
            y_samp_ideal = SignalRegistry.create_signal(wave_type, t_samp, f_sig, f_harm, a_harm, phase, n_harm)
            self.line_filt.set_visible(False)

        levels = 2**bits
        y_samp = np.round((y_samp_ideal + 1) / 2 * (levels - 1)) / (levels - 1) * 2 - 1

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
        phases = np.angle(np.fft.rfft(y_samp_fft_input))

        if db_on:
            display_mags = 20 * np.log10(np.maximum(mags, 1e-5))
            self.ax_freq.set_ylabel("Magnitude (dB)")
            self.ax_freq.set_ylim(-105, 10)
        else:
            display_mags = mags
            self.ax_freq.set_ylabel("Magnitude")
            self.ax_freq.set_ylim(0, max(1.5, (1 + a_harm) * 1.2))

        self.line_cont.set_data(t_cont, y_cont)
        self.line_filt.set_data(t_cont, y_filt_cont)
        self.line_step.set_data(t_samp, y_samp)
        self.line_fft.set_data(t_cont, y_recon)
        self.dots_samp.set_offsets(np.c_[t_samp, y_samp])
        self.ax_time.set_xlim(0, duration)
        self.ax_time.set_ylim(-1.4 - a_harm, 1.4 + a_harm)

        # Mask phase noise for low magnitudes to improve pedagogical clarity
        phases[mags < 1e-3] = 0
        self.line_phase.set_data(freqs, phases)
        self.ax_phase.set_xlim(0, max(f_samp/2 + 20, max_freq + 20))

        self.line_quant.set_data(t_samp, quant_error)
        self.ax_quant.set_xlim(0, duration)
        self.ax_quant.set_ylim(-1.5/(levels-1 if levels>1 else 1), 1.5/(levels-1 if levels>1 else 1))
        self.line_spec.set_data(freqs, display_mags)
        self.nyquist_line.set_xdata([f_samp/2, f_samp/2])
        
        is_aliased = f_samp < 2 * max_freq
        self.true_freq_line.set_xdata([max_freq, max_freq])
        
        f_folded = np.abs(max_freq - f_samp * np.round(max_freq / f_samp))
        self.alias_indicator.set_xdata([f_folded, f_folded])
        self.alias_indicator.set_visible(is_aliased)

        self.ax_freq.set_xlim(0, max(f_samp/2 + 20, max_freq + 20))
        
        noise = y_cont - y_recon
        rmse = np.sqrt(np.mean(noise**2))
        signal_power = np.mean(y_cont**2)
        noise_power = np.mean(noise**2)
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 100
        # because of their infinite harmonics, but we focus on the modeled components here.
        
        msg = f"RMSE: {rmse:.4f} | SNR: {snr:.1f} dB | Max Freq: {max_freq:.1f} Hz"
        
        if aaf_type == 'Butter' and sp_signal is None:
            msg = "Butterworth filter requires 'scipy' (pip install scipy)"

        if is_aliased:
            msg += " | WARNING: ALIASING DETECTED"
            self.status_text.get_bbox_patch().set_facecolor('#ffcc80') # Soft Orange
        else:
            self.status_text.get_bbox_patch().set_facecolor('#c8e6c9') # Soft Green
        
        self.status_text.set_text(msg)
        self.fig.canvas.draw_idle()

    def show(self) -> None:
        plt.show()
