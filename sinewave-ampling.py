import numpy as np
import matplotlib.pyplot as plt
import sys

def run_tool():
    """
    Runs the Sine Wave Sampling Visualizer tool.

    This function prompts the user for a signal frequency and a sampling rate,
    then generates and displays a plot comparing an ideal continuous sine wave
    with its sampled square-wave representation (zero-order hold) and an
    FFT-based reconstruction.
    It also includes a warning if the sampling rate is below the Nyquist rate.

    The plot duration is dynamically calculated to always show 3 cycles of the
    signal frequency for better visualization.

    Raises:
        ValueError: If non-numerical input is provided for frequencies.
    """
    print("--- Sine Wave Sampling Visualizer ---")
    try:
        f_signal = float(input("Enter signal frequency (Hz): "))
        f_sampling = float(input("Enter sampling rate (Hz): "))
        
        if f_signal <= 0 or f_sampling <= 0:
            print("Frequencies must be positive numbers.")
            return
    except ValueError:
        print("Invalid input. Please enter numerical values.")
        return

    # Calculate duration to show exactly 3 cycles of the signal for clear visualization.
    duration = 3 / f_signal
    # Define a fixed phase for the sine wave.
    phase = np.pi / 4

    # Generate time points for the continuous signal (high resolution for smooth curve).
    num_continuous_points = 1000 # Define the number of points for the continuous signal
    t_continuous = np.linspace(0, duration, num_continuous_points)
    # Calculate the amplitude of the continuous sine wave.
    y_continuous = np.sin(2 * np.pi * f_signal * t_continuous + phase)

    # Generate time points for the sampled signal based on the sampling rate.
    # np.arange is used here to get discrete sample points.
    t_sampled = np.arange(0, duration, 1 / f_sampling)
    # Calculate the amplitude of the sine wave at the sampled time points.
    y_sampled = np.sin(2 * np.pi * f_signal * t_sampled + phase)

    # Create the plot figure and axes.
    # --- FFT-based Reconstruction ---
    # Perform FFT on the sampled signal
    Y_sampled_fft = np.fft.fft(y_sampled)
    N_sampled = len(y_sampled)

    # Determine the number of points for the interpolated signal.
    # We aim for a similar resolution as the continuous signal for comparison.
    N_interp = num_continuous_points

    # Create a zero-padded array for the spectrum
    Y_padded = np.zeros(N_interp, dtype=complex)

    # Copy the positive frequency components (including DC)
    Y_padded[0 : (N_sampled + 1) // 2] = Y_sampled_fft[0 : (N_sampled + 1) // 2]
    
    # Copy the negative frequency components
    Y_padded[N_interp - (N_sampled // 2) : N_interp] = Y_sampled_fft[N_sampled - (N_sampled // 2) : N_sampled]

    # Perform Inverse FFT to get the reconstructed signal
    # Scale by N_interp / N_sampled to maintain amplitude
    y_reconstructed_fft = np.fft.ifft(Y_padded) * (N_interp / N_sampled)

    # Create a new time axis for the FFT-reconstructed signal
    t_reconstructed_fft = np.linspace(0, duration, N_interp, endpoint=False)

    fig, ax = plt.subplots(figsize=(14, 7)) # Increased figure size for better visibility

    # 1. Plot the ideal continuous sine wave
    ax.plot(t_continuous, y_continuous, label='Ideal Continuous Wave (Brute Oversampling)', color='blue', alpha=0.7, linestyle='--')

    # 2. Plot the sampled signal using a 'step' function to represent zero-order hold.
    # 'where='post'' ensures the step changes *after* the sample point, creating a square wave.
    ax.step(t_sampled, y_sampled, where='post', label='Zero-Order Hold', color='crimson', linewidth=2, alpha=0.8)

    # 3. Plot the FFT-based reconstructed signal
    ax.plot(t_reconstructed_fft, y_reconstructed_fft.real, label='FFT-based Reconstruction', color='green', linewidth=1.5, alpha=0.9)

    # 4. Overlay individual sample points to clearly show where the signal was sampled.
    ax.scatter(t_sampled, y_sampled, color='darkred', zorder=3, s=30, label='Sample Points')

    # Set the title and labels for the plot.
    ax.set_title(f'{f_signal} Hz Signal sampled at {f_sampling} Hz (with FFT Reconstruction)')
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Amplitude')
    # Add a grid for better readability.
    ax.grid(True, linestyle=':', alpha=0.6)
    # Display the legend to identify the different plot elements.
    ax.legend(loc='upper right')

    # Check for Nyquist criterion and display a warning if the sampling rate is insufficient.
    if f_sampling < 2 * f_signal:
        # The Nyquist-Shannon sampling theorem states that to accurately reconstruct a signal,
        # the sampling rate must be at least twice the highest frequency component of the signal.
        # If f_sampling < 2 * f_signal, aliasing will occur, meaning higher frequencies
        # will appear as lower frequencies in the sampled signal, leading to distortion.
        plt.figtext(0.5, 0.01, "Warning: Sampling rate is below Nyquist rate (Aliasing will occur)", 
                    ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.5, "pad":5})

    # Adjust plot to prevent labels from overlapping.
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    while True:
        run_tool()
        if input("\nAnalyze another signal? (y/n): ").lower() != 'y':
            break