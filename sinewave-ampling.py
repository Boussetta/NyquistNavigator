import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def calculate_data(f_signal, f_sampling):
    # 1. Setup Parameters
    duration = 3 / f_signal  # Show 3 cycles
    phase = np.pi / 4
    num_continuous_points = 1000
    
    # 2. Continuous Signal (Reference)
    t_cont = np.linspace(0, duration, num_continuous_points)
    y_cont = np.sin(2 * np.pi * f_signal * t_cont + phase)
    
    # 3. Sampled Signal
    t_samp = np.arange(0, duration, 1 / f_sampling)
    y_samp = np.sin(2 * np.pi * f_signal * t_samp + phase)
    
    # 4. FFT Reconstruction (Sinc Interpolation)
    N_samp = len(y_samp)
    Y_fft = np.fft.fft(y_samp)
    
    Y_padded = np.zeros(num_continuous_points, dtype=complex)
    half = (N_samp + 1) // 2
    Y_padded[:half] = Y_fft[:half]
    Y_padded[num_continuous_points - (N_samp // 2):] = Y_fft[N_samp - (N_samp // 2):]
    
    y_recon = np.fft.ifft(Y_padded).real * (num_continuous_points / N_samp)
    
    # 5. Frequency Domain for visualization
    freqs = np.fft.rfftfreq(N_samp, 1/f_sampling)
    mags = np.abs(np.fft.rfft(y_samp)) / N_samp
    
    # 6. Error Calculation (RMSE)
    rmse_fft = np.sqrt(np.mean((y_cont - y_recon)**2))
    
    return t_cont, y_cont, t_samp, y_samp, y_recon, freqs, mags, rmse_fft

def run_interactive_tool():
    # Initial values
    init_f_sig = 10.0
    init_f_samp = 50.0

    fig = plt.figure(figsize=(14, 9))
    plt.subplots_adjust(bottom=0.25, hspace=0.4)

    # --- Time Domain Plot ---
    ax_time = fig.add_subplot(2, 1, 1)
    t_cont, y_cont, t_samp, y_samp, y_recon, freqs, mags, rmse = calculate_data(init_f_sig, init_f_samp)
    
    line_cont, = ax_time.plot(t_cont, y_cont, 'b--', alpha=0.5, label='Ideal Continuous')
    line_step, = ax_time.step(t_samp, y_samp, where='post', color='crimson', alpha=0.6, label='Zero-Order Hold')
    line_fft, = ax_time.plot(t_cont, y_recon, 'g-', linewidth=2, label='FFT Reconstruction')
    dots_samp = ax_time.scatter(t_samp, y_samp, color='darkred', s=20, zorder=3)
    
    ax_time.set_title("Time Domain: Sampling & Reconstruction", fontweight='bold')
    ax_time.set_xlabel("Time (s)")
    ax_time.set_ylabel("Amplitude")
    ax_time.legend(loc='upper right', fontsize='small')
    ax_time.grid(True, linestyle=':', alpha=0.6)
    
    # --- Frequency Domain Plot ---
    ax_freq = fig.add_subplot(2, 1, 2)
    line_spec, = ax_freq.plot(freqs, mags, 'ro-', markersize=4)
    nyquist_line = ax_freq.axvline(init_f_samp/2, color='orange', linestyle='--', label='Nyquist Limit')
    
    ax_freq.set_title("Frequency Domain: Magnitude Spectrum", fontweight='bold')
    ax_freq.set_xlabel("Frequency (Hz)")
    ax_freq.set_ylabel("Magnitude")
    ax_freq.legend()
    ax_freq.grid(True, linestyle=':', alpha=0.6)

    # Status text for RMSE and Warnings
    status_text = fig.text(0.5, 0.02, '', ha='center', bbox=dict(facecolor='white', alpha=0.8))

    # --- Sliders ---
    ax_f_sig = plt.axes([0.2, 0.12, 0.6, 0.03])
    ax_f_samp = plt.axes([0.2, 0.08, 0.6, 0.03])
    
    s_f_sig = Slider(ax_f_sig, 'Signal (Hz) ', 1.0, 50.0, valinit=init_f_sig)
    s_f_samp = Slider(ax_f_samp, 'Sampling (Hz)', 5.0, 1500.0, valinit=init_f_samp)

    def update(val):
        f_sig = s_f_sig.val
        f_samp = s_f_samp.val
        
        # Recalculate
        tc, yc, ts, ys, yr, fr, mg, err = calculate_data(f_sig, f_samp)
        
        # Update Time Plot
        line_cont.set_data(tc, yc)
        # For step and scatter, we need to update the entire data structures
        line_step.set_data(ts, ys)
        line_fft.set_data(tc, yr)
        dots_samp.set_offsets(np.c_[ts, ys])
        
        ax_time.set_xlim(0, 3/f_sig)
        
        # Update Freq Plot
        line_spec.set_data(fr, mg)
        ax_freq.set_xlim(0, max(f_samp * 0.6, f_sig * 1.5))
        ax_freq.set_ylim(0, max(mg.max() * 1.2, 0.1))
        nyquist_line.set_xdata([f_samp/2, f_samp/2])
        
        # Update Status
        warn = ""
        if f_samp < 2 * f_sig:
            warn = " | WARNING: ALIASING!"
            status_text.get_bbox_patch().set_facecolor('orange')
        else:
            status_text.get_bbox_patch().set_facecolor('lightgreen')
            
        status_text.set_text(f"FFT Reconstruction RMSE: {err:.4f}{warn}")
        
        fig.canvas.draw_idle()

    s_f_sig.on_changed(update)
    s_f_samp.on_changed(update)
    
    update(None) # Initial call
    plt.show()

if __name__ == "__main__":
    run_interactive_tool()