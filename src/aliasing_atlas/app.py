"""AliasingAtlas: a pedagogical tool for visualizing sampling and aliasing."""

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, RadioButtons, Slider

from .dsp import (
    apply_anti_alias_filter,
    apply_window,
    compute_continuous_points,
    compute_duration,
    compute_spectrum,
    folded_alias_frequency,
    is_aliased,
    quantize_signal,
    reconstruct_fft,
    reconstruct_foh,
    reconstruction_metrics,
    sample_signal,
)
from .signals import SignalRegistry
from .presets import get_preset, preset_names

try:
    from scipy import signal as sp_signal
except ImportError:
    sp_signal = None

# Optional import for notebook audio playback.
try:
    from IPython.display import Audio, display
except ImportError:
    Audio, display = None, None

# Optional import for local desktop audio playback.
try:
    import sounddevice as sd
except ImportError:
    sd = None


class AliasingToolbox:
    """Interactive UI for signal sampling, aliasing, and reconstruction."""

    def __init__(self) -> None:
        self.f_sig_max = 50.0
        self.f_samp_max = 1500.0
        self.num_continuous_points = 1000
        self._suspend_updates = False

        self.fig = plt.figure(figsize=(14, 10))
        plt.subplots_adjust(bottom=0.35, hspace=0.4, wspace=0.25)

        self.ax_time = self.fig.add_subplot(2, 2, 1)
        self.ax_time.set_title("AliasingAtlas: Time Domain", fontweight="bold")
        self.ax_time.grid(True, linestyle=":", alpha=0.6)

        self.ax_freq = self.fig.add_subplot(2, 2, 2)
        self.ax_freq.set_title("Frequency Domain: Magnitude Spectrum", fontweight="bold")
        self.ax_freq.grid(True, linestyle=":", alpha=0.6)
        self.ax_freq.set_ylabel("Magnitude")
        self.ax_freq.set_xlim(0, self.f_samp_max / 2 + 100)
        self.ax_freq.set_ylim(0, 1.5)

        self.ax_phase = self.fig.add_subplot(2, 2, 3)
        self.ax_phase.set_title("Frequency Domain: Phase Spectrum", fontweight="bold")
        self.ax_phase.grid(True, linestyle=":", alpha=0.6)
        self.ax_phase.set_ylabel("Phase (rad)")
        self.ax_phase.set_ylim(-np.pi - 0.5, np.pi + 0.5)

        self.ax_quant = self.fig.add_subplot(2, 2, 4)
        self.ax_quant.set_title("Quantization Error (e = y_quant - y_ideal)", fontweight="bold")
        self.ax_quant.grid(True, linestyle=":", alpha=0.6)
        self.ax_quant.set_ylabel("Error Amp")

        self.line_cont, = self.ax_time.plot([], [], "b--", alpha=0.4, label="Ideal Continuous")
        self.line_filt, = self.ax_time.plot([], [], "y-", alpha=0.7, linewidth=1.5, label="AAF Filtered", zorder=2)
        self.line_foh, = self.ax_time.plot([], [], "c-", alpha=0.8, linewidth=1.5, label="FOH Reconstruction")
        self.line_step, = self.ax_time.step([], [], where="post", color="crimson", alpha=0.6, label="Zero-Order Hold")
        self.line_fft, = self.ax_time.plot([], [], "g-", linewidth=2, label="FFT Reconstruction")
        self.dots_samp = self.ax_time.scatter([], [], color="darkred", s=20, zorder=3)

        self.line_spec, = self.ax_freq.plot([], [], "ro-", markersize=4, label="Sampled Peak")
        self.line_phase, = self.ax_phase.plot([], [], "go-", markersize=4, label="Phase")
        self.nyquist_line = self.ax_freq.axvline(0, color="orange", linestyle="--", label="Nyquist Limit")
        self.true_freq_line = self.ax_freq.axvline(0, color="blue", alpha=0.4, linestyle="--", label="Intended Freq")
        self.aaf_filter_response, = self.ax_freq.plot([], [], "k--", alpha=0.5, label="AAF Response")
        self.alias_indicator = self.ax_freq.axvline(0, color="magenta", alpha=0.6, linestyle=":", label="Predicted Alias")
        self.line_quant, = self.ax_quant.plot([], [], "m.-", markersize=3, alpha=0.7, label="Error")

        self.ax_time.legend(loc="upper right", fontsize="small")
        self.ax_freq.legend(loc="upper right", fontsize="small")

        slider_color = "lightsteelblue"

        self.cax_tabs = plt.axes([0.02, 0.05, 0.10, 0.18], facecolor="whitesmoke")
        self.w_tabs = RadioButtons(self.cax_tabs, ("Signal", "Sampling", "Audio"))
        self.cax_tabs.set_title("Navigation", fontsize=10, fontweight="bold")

        self.cax_f_sig = plt.axes([0.20, 0.25, 0.28, 0.02], facecolor=slider_color)
        self.cax_f_samp = plt.axes([0.58, 0.25, 0.28, 0.02], facecolor=slider_color)
        self.cax_preset = plt.axes([0.88, 0.18, 0.10, 0.16], facecolor=slider_color)
        self.cax_reset = plt.axes([0.88, 0.24, 0.08, 0.04], facecolor=slider_color)

        self.s_f_sig = Slider(self.cax_f_sig, "Base Freq (Hz)", 1.0, self.f_sig_max, valinit=10.0)
        self.s_f_samp = Slider(self.cax_f_samp, "Sampling (Hz)", 5.0, self.f_samp_max, valinit=50.0)
        self.btn_reset = Button(self.cax_reset, "Reset All")
        self.w_preset = RadioButtons(self.cax_preset, tuple(preset_names()))
        self.cax_preset.set_title("Presets", fontsize=10)

        self.cax_sig_box = plt.axes([0.15, 0.05, 0.65, 0.18], facecolor="whitesmoke", alpha=0.5)
        self.cax_sig_box.set_title("Signal Components", fontsize=10, fontweight="bold")
        self.cax_sig_box.set_xticks([])
        self.cax_sig_box.set_yticks([])

        self.cax_f_harm = plt.axes([0.25, 0.16, 0.20, 0.015], facecolor=slider_color)
        self.cax_a_harm = plt.axes([0.25, 0.11, 0.20, 0.015], facecolor=slider_color)
        self.cax_s_phase = plt.axes([0.55, 0.16, 0.20, 0.015], facecolor=slider_color)
        self.cax_n_harm = plt.axes([0.55, 0.11, 0.20, 0.015], facecolor=slider_color)
        self.cax_wave = plt.axes([0.82, 0.05, 0.12, 0.18], facecolor=slider_color)

        self.s_f_harm = Slider(self.cax_f_harm, "Harmonic (Hz)", 1.0, self.f_sig_max * 2, valinit=20.0)
        self.s_f_harm_amp = Slider(self.cax_a_harm, "Harmonic Amp", 0.0, 1.0, valinit=0.0)
        self.s_phase = Slider(self.cax_s_phase, "Phase", 0, 2 * np.pi, valinit=np.pi / 4)
        self.s_n_harm = Slider(self.cax_n_harm, "Fourier Harm.", 1, 50, valinit=1, valstep=1)
        self.w_wave = RadioButtons(self.cax_wave, tuple(SignalRegistry.get_signal_names()))
        self.cax_wave.set_title("Waveform", fontsize=10)

        self.tab_signal_axes = [
            self.cax_sig_box,
            self.cax_f_harm,
            self.cax_a_harm,
            self.cax_s_phase,
            self.cax_n_harm,
            self.cax_wave,
        ]

        self.cax_quant_box = plt.axes([0.15, 0.05, 0.35, 0.18], facecolor="whitesmoke", alpha=0.5)
        self.cax_quant_box.set_title("Quantization", fontsize=10, fontweight="bold")
        self.cax_quant_box.set_xticks([])
        self.cax_quant_box.set_yticks([])

        self.cax_bits = plt.axes([0.22, 0.12, 0.25, 0.015], facecolor=slider_color)
        self.cax_window = plt.axes([0.55, 0.05, 0.10, 0.18], facecolor=slider_color)
        self.cax_aaf = plt.axes([0.68, 0.05, 0.10, 0.18], facecolor=slider_color)
        self.cax_recon = plt.axes([0.82, 0.18, 0.12, 0.05], facecolor=slider_color)
        self.cax_db_scale = plt.axes([0.82, 0.05, 0.12, 0.12], facecolor=slider_color)

        self.s_bits = Slider(self.cax_bits, "Bit Depth", 2, 16, valinit=16, valstep=1)
        self.w_radio = RadioButtons(self.cax_window, ("None", "Hamming", "Hann"))
        self.cax_window.set_title("Window", fontsize=10)
        self.w_aaf = RadioButtons(self.cax_aaf, ("None", "Ideal", "Butter"))
        self.cax_aaf.set_title("AAF", fontsize=10)
        self.w_recon = RadioButtons(self.cax_recon, ("FFT", "FOH"))
        self.cax_recon.set_title("Recon", fontsize=10)
        self.w_db = RadioButtons(self.cax_db_scale, ("Linear", "dB Scale"))
        self.cax_db_scale.set_title("Scale", fontsize=10)

        self.tab_sampling_axes = [
            self.cax_quant_box,
            self.cax_bits,
            self.cax_window,
            self.cax_aaf,
            self.cax_recon,
            self.cax_db_scale,
        ]

        self.cax_audio_box = plt.axes([0.15, 0.05, 0.35, 0.18], facecolor="whitesmoke", alpha=0.5)
        self.cax_audio_box.set_title("Playback Settings", fontsize=10, fontweight="bold")
        self.cax_audio_box.set_xticks([])
        self.cax_audio_box.set_yticks([])

        self.cax_vol = plt.axes([0.25, 0.16, 0.20, 0.015], facecolor=slider_color)
        self.cax_dur = plt.axes([0.25, 0.11, 0.20, 0.015], facecolor=slider_color)
        self.cax_audio_src = plt.axes([0.55, 0.05, 0.15, 0.18], facecolor=slider_color)
        self.cax_play_audio = plt.axes([0.75, 0.10, 0.12, 0.08], facecolor=slider_color)

        self.s_vol = Slider(self.cax_vol, "Audio Vol", 0.0, 1.0, valinit=0.5)
        self.s_dur = Slider(self.cax_dur, "Audio Dur (s)", 0.5, 3.0, valinit=1.5)
        self.w_audio_src = RadioButtons(self.cax_audio_src, ("Sampled", "Recon"))
        self.cax_audio_src.set_title("Audio Source", fontsize=10)
        self.btn_play_audio = Button(self.cax_play_audio, "Play Audio")

        self.tab_audio_axes = [self.cax_audio_box, self.cax_vol, self.cax_dur, self.cax_audio_src, self.cax_play_audio]

        self.tab_groups = {
            "Signal": self.tab_signal_axes,
            "Sampling": self.tab_sampling_axes,
            "Audio": self.tab_audio_axes,
        }

        self.w_tabs.on_clicked(self._tab_callback)
        self._update_tab_visibility("Signal")

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
        self.w_recon.on_clicked(self.update)
        self.w_db.on_clicked(self.update)
        self.w_audio_src.on_clicked(self.update)
        self.w_preset.on_clicked(self._preset_callback)
        self.btn_play_audio.on_clicked(self._play_audio_callback)
        self.btn_reset.on_clicked(self._reset_callback)

        self.status_text = self.fig.text(0.5, 0.01, "", ha="center", bbox=dict(facecolor="white", alpha=0.8))
        self.update(None)

    def _tab_callback(self, label: str) -> None:
        self._update_tab_visibility(label)
        self.fig.canvas.draw_idle()

    def _update_tab_visibility(self, active_tab: str) -> None:
        for tab_name, axes_list in self.tab_groups.items():
            is_visible = tab_name == active_tab
            for ax in axes_list:
                ax.set_visible(is_visible)
                for child in ax.get_children():
                    child.set_visible(is_visible)

    def _reset_callback(self, event) -> None:
        self.s_f_sig.reset()
        self.s_f_harm.reset()
        self.s_f_harm_amp.reset()
        self.s_phase.reset()
        self.s_f_samp.reset()
        self.s_bits.reset()
        self.s_n_harm.reset()
        self.s_vol.reset()
        self.s_dur.reset()
        self.w_radio.set_active(0)
        self.w_wave.set_active(0)
        self.w_aaf.set_active(0)
        self.w_recon.set_active(0)
        self.w_audio_src.set_active(0)
        self.w_db.set_active(0)
        self.fig.canvas.draw_idle()

    def _set_radio_value(self, widget: RadioButtons, target_label: str) -> None:
        labels = [txt.get_text() for txt in widget.labels]
        if target_label in labels:
            widget.set_active(labels.index(target_label))

    def _preset_callback(self, label: str) -> None:
        preset = get_preset(label)

        self._suspend_updates = True
        self.s_f_sig.set_val(preset.f_sig)
        self.s_f_samp.set_val(preset.f_samp)
        self.s_f_harm.set_val(preset.f_harm)
        self.s_f_harm_amp.set_val(preset.a_harm)
        self.s_phase.set_val(preset.phase)
        self.s_n_harm.set_val(preset.n_harm)
        self.s_bits.set_val(preset.bits)
        self._set_radio_value(self.w_wave, preset.wave_type)
        self._set_radio_value(self.w_aaf, preset.aaf_type)
        self._set_radio_value(self.w_recon, preset.recon_type)
        self._set_radio_value(self.w_radio, preset.window_type)
        self._suspend_updates = False

        self.update(None)

    def _get_params(self):
        return (
            self.s_f_sig.val,
            self.s_f_harm.val,
            self.s_f_harm_amp.val,
            self.s_phase.val,
            self.s_f_samp.val,
            int(self.s_bits.val),
            self.w_radio.value_selected,
            self.w_wave.value_selected,
            self.w_aaf.value_selected,
            self.w_recon.value_selected,
            self.w_db.value_selected == "dB Scale",
            int(self.s_n_harm.val),
        )

    def _update_signal_labels(self, wave_type: str) -> None:
        if wave_type in ["AM", "FM"]:
            self.s_f_sig.label.set_text("Carrier Freq (Hz)")
            self.s_f_harm.label.set_text("Message Freq (Hz)")
            self.s_f_harm_amp.label.set_text("Mod Index (beta/m)")
        else:
            self.s_f_sig.label.set_text("Base Freq (Hz)")
            self.s_f_harm.label.set_text("Harmonic (Hz)")
            self.s_f_harm_amp.label.set_text("Harmonic Amp")

    def _build_signal_data(
        self,
        f_sig: float,
        f_harm: float,
        a_harm: float,
        phase: float,
        f_samp: float,
        bits: int,
        window_type: str,
        wave_type: str,
        aaf_type: str,
        n_harm: int,
    ):
        max_freq = SignalRegistry.get_max_freq(wave_type, f_sig, f_harm, a_harm, n_harm)
        self.num_continuous_points = compute_continuous_points(max_freq)

        duration = compute_duration(f_sig, cycles=3.0)
        t_cont = np.linspace(0.0, duration, self.num_continuous_points)
        y_cont = SignalRegistry.create_signal(wave_type, t_cont, f_sig, f_harm, a_harm, phase, n_harm)

        y_filt_cont, b, a, fs_cont = apply_anti_alias_filter(
            y_cont,
            t_cont,
            f_samp,
            aaf_type,
            scipy_signal=sp_signal,
        )

        sample_source = y_filt_cont if aaf_type != "None" else y_cont
        t_samp, y_samp_ideal = sample_signal(t_cont, sample_source, f_samp, duration)
        y_samp = quantize_signal(y_samp_ideal, bits)
        quant_error = y_samp - y_samp_ideal

        y_fft_input = apply_window(y_samp, window_type)
        y_recon_fft = reconstruct_fft(y_fft_input, self.num_continuous_points)
        y_recon_foh = reconstruct_foh(t_cont, t_samp, y_samp)

        freqs, mags, phases = compute_spectrum(y_fft_input, f_samp)
        phases[mags < 1e-3] = 0

        return {
            "max_freq": max_freq,
            "duration": duration,
            "t_cont": t_cont,
            "y_cont": y_cont,
            "y_filt_cont": y_filt_cont,
            "t_samp": t_samp,
            "y_samp": y_samp,
            "quant_error": quant_error,
            "y_recon_fft": y_recon_fft,
            "y_recon_foh": y_recon_foh,
            "freqs": freqs,
            "mags": mags,
            "phases": phases,
            "aaf_b": b,
            "aaf_a": a,
            "aaf_fs_cont": fs_cont,
        }

    def _compute_display_magnitudes(self, mags: np.ndarray, db_on: bool, a_harm: float) -> np.ndarray:
        if db_on:
            display_mags = 20 * np.log10(np.maximum(mags, 1e-5))
            self.ax_freq.set_ylabel("Magnitude (dB)")
            self.ax_freq.set_ylim(-105, 10)
            return display_mags

        self.ax_freq.set_ylabel("Magnitude")
        self.ax_freq.set_ylim(0, max(1.5, (1 + a_harm) * 1.2))
        return mags

    def _update_time_domain_plots(
        self,
        t_cont: np.ndarray,
        y_cont: np.ndarray,
        y_filt_cont: np.ndarray,
        t_samp: np.ndarray,
        y_samp: np.ndarray,
        y_recon_fft: np.ndarray,
        y_recon_foh: np.ndarray,
        recon_type: str,
        duration: float,
        a_harm: float,
        aaf_type: str,
    ) -> None:
        self.line_cont.set_data(t_cont, y_cont)
        self.line_filt.set_data(t_cont, y_filt_cont)
        self.line_filt.set_visible(aaf_type != "None")

        self.line_step.set_data(t_samp, y_samp)
        self.dots_samp.set_offsets(np.c_[t_samp, y_samp])

        self.line_fft.set_data(t_cont, y_recon_fft)
        self.line_foh.set_data(t_cont, y_recon_foh)
        self.line_fft.set_visible(recon_type == "FFT")
        self.line_foh.set_visible(recon_type == "FOH")

        self.ax_time.set_xlim(0, duration)
        self.ax_time.set_ylim(-1.4 - a_harm, 1.4 + a_harm)

    def _update_frequency_domain_plots(
        self,
        freqs: np.ndarray,
        phases: np.ndarray,
        display_mags: np.ndarray,
        f_samp: float,
        max_freq: float,
        aliased: bool,
        f_folded: float,
    ) -> None:
        self.line_spec.set_data(freqs, display_mags)
        self.line_phase.set_data(freqs, phases)
        self.nyquist_line.set_xdata([f_samp / 2, f_samp / 2])
        self.true_freq_line.set_xdata([max_freq, max_freq])
        self.alias_indicator.set_xdata([f_folded, f_folded])
        self.alias_indicator.set_visible(aliased)

        x_max = max(f_samp / 2 + 20, max_freq + 20)
        self.ax_freq.set_xlim(0, x_max)
        self.ax_phase.set_xlim(0, x_max)

    def _update_quantization_plot(self, t_samp: np.ndarray, quant_error: np.ndarray, duration: float, bits: int) -> None:
        levels = max(2, 2 ** bits)
        self.line_quant.set_data(t_samp, quant_error)
        self.ax_quant.set_xlim(0, duration)
        self.ax_quant.set_ylim(-1.5 / (levels - 1), 1.5 / (levels - 1))

    def _update_status(self, y_cont: np.ndarray, y_recon: np.ndarray, max_freq: float, aaf_type: str, aliased: bool) -> None:
        rmse, snr = reconstruction_metrics(y_cont, y_recon)
        msg = f"RMSE: {rmse:.4f} | SNR: {snr:.1f} dB | Max Freq: {max_freq:.1f} Hz"

        if aaf_type == "Butter" and sp_signal is None:
            msg = "Butterworth filter requires scipy (pip install scipy)."

        if aliased:
            msg += " | WARNING: ALIASING DETECTED"
            self.status_text.get_bbox_patch().set_facecolor("#ffcc80")
        else:
            self.status_text.get_bbox_patch().set_facecolor("#c8e6c9")

        self.status_text.set_text(msg)

    def _update_aaf_response(self, aaf_type: str, b, a, fs_cont: Optional[float], f_samp: float, db_on: bool) -> None:
        if aaf_type == "Butter" and sp_signal is not None and b is not None and a is not None and fs_cont is not None:
            f_resp, h_resp = sp_signal.freqz(b, a, worN=512, fs=fs_cont)
            if db_on:
                mag = 20 * np.log10(np.maximum(np.abs(h_resp), 1e-5))
            else:
                mag = np.abs(h_resp)
            self.aaf_filter_response.set_data(f_resp, mag)
            self.aaf_filter_response.set_visible(True)
            return

        if aaf_type == "Ideal":
            x = np.array([0, f_samp / 2, f_samp / 2, self.f_samp_max])
            if db_on:
                y = np.array([0.0, 0.0, -100.0, -100.0])
            else:
                y = np.array([1.0, 1.0, 0.0, 0.0])
            self.aaf_filter_response.set_data(x, y)
            self.aaf_filter_response.set_visible(True)
            return

        self.aaf_filter_response.set_visible(False)

    def _play_audio_callback(self, event) -> None:
        playback_fs = 44100
        duration = self.s_dur.val
        volume = self.s_vol.val

        f_sig, f_harm, a_harm, phase, f_samp, bits, _, wave_type, aaf_type, recon_type, _, n_harm = self._get_params()

        if f_samp <= 0:
            self.status_text.set_text("Cannot play audio: sampling frequency must be greater than 0.")
            self.status_text.get_bbox_patch().set_facecolor("red")
            self.fig.canvas.draw_idle()
            return

        num_playback = max(2, int(duration * playback_fs))
        t_playback = np.linspace(0.0, duration, num_playback, endpoint=False)
        y_full = SignalRegistry.create_signal(wave_type, t_playback, f_sig, f_harm, a_harm, phase, n_harm)

        y_filtered, _, _, _ = apply_anti_alias_filter(
            y_full,
            t_playback,
            f_samp,
            aaf_type,
            scipy_signal=sp_signal,
        )

        t_samp, y_samp = sample_signal(t_playback, y_filtered, f_samp, duration)
        y_samp_q = quantize_signal(y_samp, bits)

        if self.w_audio_src.value_selected == "Sampled":
            indices = np.floor(t_playback * f_samp).astype(int)
            indices = np.clip(indices, 0, len(y_samp_q) - 1)
            audio_data = y_samp_q[indices]
        elif recon_type == "FOH":
            audio_data = reconstruct_foh(t_playback, t_samp, y_samp_q)
        else:
            audio_data = reconstruct_fft(y_samp_q, len(t_playback))

        max_v = np.max(np.abs(audio_data))
        audio_data = (audio_data / max_v if max_v > 0 else audio_data) * volume

        if sd is not None:
            try:
                sd.play(audio_data, playback_fs)
                self.status_text.set_text(f"Playing {wave_type} via sounddevice...")
                self.fig.canvas.draw_idle()
                return
            except Exception:
                pass

        if Audio is not None and display is not None:
            display(Audio(data=audio_data.astype(np.float32), rate=playback_fs, autoplay=True))
            self.status_text.set_text(f"Audio player for {wave_type} generated below.")
        else:
            self.status_text.set_text("Audio failed. Install 'sounddevice' for desktop playback.")
            self.status_text.get_bbox_patch().set_facecolor("orange")

        self.fig.canvas.draw_idle()

    def update(self, val: Optional[float]) -> None:
        if self._suspend_updates:
            return

        (
            f_sig,
            f_harm,
            a_harm,
            phase,
            f_samp,
            bits,
            window_type,
            wave_type,
            aaf_type,
            recon_type,
            db_on,
            n_harm,
        ) = self._get_params()

        if f_sig <= 0 or f_samp <= 0:
            self.status_text.set_text("Signal and sampling frequencies must be greater than 0.")
            self.status_text.get_bbox_patch().set_facecolor("red")
            self.fig.canvas.draw_idle()
            return

        self._update_signal_labels(wave_type)
        signal_data = self._build_signal_data(
            f_sig,
            f_harm,
            a_harm,
            phase,
            f_samp,
            bits,
            window_type,
            wave_type,
            aaf_type,
            n_harm,
        )

        max_freq = signal_data["max_freq"]
        duration = signal_data["duration"]
        t_cont = signal_data["t_cont"]
        y_cont = signal_data["y_cont"]
        y_filt_cont = signal_data["y_filt_cont"]
        t_samp = signal_data["t_samp"]
        y_samp = signal_data["y_samp"]
        quant_error = signal_data["quant_error"]
        y_recon_fft = signal_data["y_recon_fft"]
        y_recon_foh = signal_data["y_recon_foh"]
        freqs = signal_data["freqs"]
        mags = signal_data["mags"]
        phases = signal_data["phases"]
        b = signal_data["aaf_b"]
        a = signal_data["aaf_a"]
        fs_cont = signal_data["aaf_fs_cont"]

        y_recon = y_recon_foh if recon_type == "FOH" else y_recon_fft

        aliased = is_aliased(max_freq, f_samp)
        f_folded = folded_alias_frequency(max_freq, f_samp)

        display_mags = self._compute_display_magnitudes(mags, db_on, a_harm)
        self._update_time_domain_plots(
            t_cont,
            y_cont,
            y_filt_cont,
            t_samp,
            y_samp,
            y_recon_fft,
            y_recon_foh,
            recon_type,
            duration,
            a_harm,
            aaf_type,
        )
        self._update_frequency_domain_plots(freqs, phases, display_mags, f_samp, max_freq, aliased, f_folded)

        self._update_aaf_response(aaf_type, b, a, fs_cont, f_samp, db_on)
        self._update_quantization_plot(t_samp, quant_error, duration, bits)
        self._update_status(y_cont, y_recon, max_freq, aaf_type, aliased)
        self.fig.canvas.draw_idle()

    def show(self) -> None:
        plt.show()
