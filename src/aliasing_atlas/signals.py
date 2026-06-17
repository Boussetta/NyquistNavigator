"""Signal generation logic for AliasingAtlas.

This module provides mathematical models for various waveforms and modulation types
used in digital signal processing education and visualization. All signal generators
use the Fourier series method for non-sinusoidal waves to accurately represent harmonics
and their contribution to aliasing.

Signal Categories:
    1. Basic Waveforms:
       - Sine: Pure single-frequency sinusoid with optional harmonic
       - Square: Odd-harmonic Fourier series (k=1,3,5,...)
       - Sawtooth: All-harmonic Fourier series
       - Triangle: Odd-harmonic Fourier series with squared coefficients

    2. Modulated Signals:
       - AM (Amplitude Modulation): Signal envelope varies with modulation frequency
       - FM (Frequency Modulation): Instantaneous frequency varies (Carson's bandwidth)
       - Chirp: Linear frequency sweep across time range

Design Principles:
    - All signals inherit from abstract base class Signal
    - Signals are registered with SignalRegistry for dynamic creation
    - Bandwidth prediction (get_max_freq) for Nyquist analysis
    - All calculations use NumPy for vectorized operations

Dependencies:
    - NumPy: Array operations and mathematical functions
    - Standard library: abc (abstract base classes), typing
"""

import numpy as np
from typing import Union, List, Dict, Type
from abc import ABC, abstractmethod


class Signal(ABC):
    """Abstract base class for all signal types.
    
    All signal generators must inherit from this class and implement the
    calculate() method. Attributes define both the fundamental signal and
    any modulation or harmonic parameters.
    
    Attributes:
        t: Time vector as numpy array or list of floats.
        f_sig: Fundamental frequency (or carrier frequency for modulated signals) in Hz.
        f_harm: Harmonic or modulation frequency in Hz.
        a_harm: Amplitude of harmonic or modulation index (dimensionless, typically 0-1).
        phase: Initial phase of the fundamental signal in radians.
        n_harm: Number of Fourier harmonics to synthesize (for periodic waveforms).
    """
    
    def __init__(
        self,
        t: Union[np.ndarray, List[float]],
        f_sig: float,
        f_harm: float,
        a_harm: float,
        phase: float,
        n_harm: int = 1,
    ) -> None:
        """Initialize a signal with time vector and parameters.
        
        Args:
            t: Time values at which to evaluate the signal.
            f_sig: Fundamental/carrier frequency in Hz.
            f_harm: Harmonic or modulation frequency in Hz.
            a_harm: Amplitude/index of harmonic or modulation component.
            phase: Initial phase offset in radians.
            n_harm: Number of harmonics to include (default 1, only affects
                    Square, Sawtooth, Triangle waveforms).
        """
        self.t = t
        self.f_sig = f_sig
        self.f_harm = f_harm
        self.a_harm = a_harm
        self.phase = phase
        self.n_harm = n_harm

    @abstractmethod
    def calculate(self) -> np.ndarray:
        """Calculate the signal waveform at time points self.t.
        
        Returns:
            Numpy array of signal values at time points t.
        """
        pass


class SineWave(Signal):
    """Pure sine wave with optional harmonic component.
    
    Generates y(t) = sin(2π*f_sig*t + phase) + a_harm*sin(2π*f_harm*t)
    
    This is the simplest periodic signal, containing only the fundamental frequency
    and optional harmonic. Useful for demonstrating basic sampling and aliasing.
    """

    def calculate(self) -> np.ndarray:
        """Generate sine wave with harmonic.
        
        Returns:
            Combined base sine wave and harmonic component.
        """
        base = np.sin(2 * np.pi * self.f_sig * self.t + self.phase)
        harm = self.a_harm * np.sin(2 * np.pi * self.f_harm * self.t)
        return base + harm


class SquareWave(Signal):
    """Square wave approximated by Fourier series summation.
    
    Implements: y(t) = (4/π) * Σ (1/k)*sin(2π*k*f_sig*t)
                 where k = 1, 3, 5, ... (odd harmonics)
    
    Uses n_harm harmonics for fidelity. More harmonics produce sharper edges
    but extend bandwidth, demonstrating aliasing of higher harmonics.
    """

    def calculate(self) -> np.ndarray:
        """Generate square wave via Fourier series.
        
        Returns:
            Square wave approximation with n_harm odd harmonics included.
        """
        base = np.zeros_like(self.t, dtype=np.float64)
        for i in range(self.n_harm):
            k = 2 * i + 1  # Odd harmonics only
            base += (1.0 / k) * np.sin(2 * np.pi * k * self.f_sig * self.t + self.phase)
        base = (4 / np.pi) * base
        harm = self.a_harm * np.sign(np.sin(2 * np.pi * self.f_harm * self.t))
        return base + harm


class SawtoothWave(Signal):
    """Sawtooth wave approximated by Fourier series summation.
    
    Implements: y(t) = (2/π) * Σ ((-1)^(k+1)/k)*sin(2π*k*f_sig*t)
                 where k = 1, 2, 3, ... (all harmonics)
    
    Sawtooth contains all harmonics and has the richest spectrum, making it
    ideal for demonstrating wideband aliasing effects.
    """

    def calculate(self) -> np.ndarray:
        """Generate sawtooth wave via Fourier series.
        
        Returns:
            Sawtooth wave approximation with n_harm harmonics.
        """
        base = np.zeros_like(self.t, dtype=np.float64)
        for k in range(1, self.n_harm + 1):
            base += ((-1) ** (k + 1) / k) * np.sin(2 * np.pi * k * self.f_sig * self.t + self.phase)
        base = (2 / np.pi) * base
        harm = self.a_harm * 2 * (self.f_harm * self.t - np.floor(0.5 + self.f_harm * self.t))
        return base + harm


class TriangleWave(Signal):
    """Triangle wave approximated by Fourier series summation.
    
    Implements: y(t) = (8/π²) * Σ ((-1)^i/(k²))*sin(2π*k*f_sig*t)
                 where k = 1, 3, 5, ... (odd harmonics, squared denominator)
    
    Triangle wave has faster harmonic decay than square wave, producing
    smoother transitions and lower high-frequency content.
    """

    def calculate(self) -> np.ndarray:
        """Generate triangle wave via Fourier series.
        
        Returns:
            Triangle wave approximation with n_harm odd harmonics.
        """
        base = np.zeros_like(self.t, dtype=np.float64)
        for i in range(self.n_harm):
            k = 2 * i + 1  # Odd harmonics only
            sign = (-1) ** i
            base += (sign / (k ** 2)) * np.sin(2 * np.pi * k * self.f_sig * self.t + self.phase)
        base = (8 / np.pi ** 2) * base
        harm = self.a_harm * (2 * np.abs(2 * (self.f_harm * self.t - np.floor(self.f_harm * self.t + 0.5))) - 1)
        return base + harm


class AMWave(Signal):
    """Amplitude Modulated signal.
    
    Implements: y(t) = (1 + a_harm*sin(2π*f_harm*t)) * sin(2π*f_sig*t + phase)
    
    Generates two sidebands at frequencies f_sig ± f_harm. When f_harm > 0 and
    a_harm > 0, demonstrates modulation bandwidth expansion and multi-component
    aliasing scenarios.
    
    Note:
        a_harm is typically 0 to 1 (modulation depth). Values > 1 cause
        over-modulation with phase reversals.
    """

    def calculate(self) -> np.ndarray:
        """Generate amplitude-modulated signal.
        
        Returns:
            AM signal with carrier at f_sig and modulation at f_harm.
        """
        base = (1 + self.a_harm * np.sin(2 * np.pi * self.f_harm * self.t)) * np.sin(
            2 * np.pi * self.f_sig * self.t + self.phase
        )
        return base


class FMWave(Signal):
    """Frequency Modulated signal.
    
    Implements: y(t) = sin(2π*f_sig*t + a_harm*sin(2π*f_harm*t) + phase)
    
    Modulation index a_harm (usually 0 to 10) determines bandwidth via Carson's rule:
    BW ≈ 2 * f_harm * (a_harm + 1). Higher indices create wider bandwidth and more
    aliasing artifacts.
    """

    def calculate(self) -> np.ndarray:
        """Generate frequency-modulated signal.
        
        Returns:
            FM signal with instantaneous frequency modulated by a_harm and f_harm.
        """
        base = np.sin(
            2 * np.pi * self.f_sig * self.t
            + self.phase
            + self.a_harm * np.sin(2 * np.pi * self.f_harm * self.t)
        )
        return base


class ChirpWave(Signal):
    """Linear frequency chirp (swept sine).
    
    Generates a signal that linearly sweeps from f_sig to f_harm over the
    duration of the time vector. Instantaneous frequency:
    
        f(t) = f_sig + k*t, where k = (f_harm - f_sig) / T
    
    Demonstrates how aliasing transitions occur as the instantaneous frequency
    approaches the Nyquist limit.
    """

    def calculate(self) -> np.ndarray:
        """Generate linear chirp signal.
        
        Returns:
            Signal with linearly varying instantaneous frequency.
        """
        t = np.asarray(self.t)
        if t.size < 2:
            return np.sin(2 * np.pi * self.f_sig * t + self.phase)

        # Relative time from start
        tau = t - t[0]
        duration = max(float(tau[-1]), 1e-9)
        
        # Chirp parameters
        f0 = max(float(self.f_sig), 0.0)  # Start frequency
        f1 = max(float(self.f_harm), f0)  # End frequency
        k = (f1 - f0) / duration  # Chirp rate
        
        # Instantaneous phase: φ(t) = 2π(f₀τ + ½kτ²) + phase_offset
        phase = 2 * np.pi * (f0 * tau + 0.5 * k * tau ** 2) + self.phase
        return np.sin(phase)


class SignalRegistry:
    """Registry pattern for creating and managing signal types.
    
    Provides dynamic signal creation, querying available signal types, and
    bandwidth prediction for Nyquist analysis. All signal classes must be
    registered before use.
    
    Example:
        >>> SignalRegistry.create_signal('Sine', t, f_sig=10, f_harm=20, a_harm=0.1, phase=0, n_harm=1)
        array([...])  # sine wave with harmonic
    """

    _signals: Dict[str, Type[Signal]] = {}

    @classmethod
    def register_signal(cls, name: str, signal_class: Type[Signal]) -> None:
        """Register a new signal type.
        
        Args:
            name: Unique identifier for the signal type (e.g., 'Sine', 'Square').
            signal_class: Subclass of Signal that implements calculate().
        
        Raises:
            ValueError: If signal_class does not inherit from Signal.
        """
        if not issubclass(signal_class, Signal):
            raise ValueError("Registered class must inherit from Signal")
        cls._signals[name] = signal_class

    @classmethod
    def create_signal(
        cls,
        wave_type: str,
        t: Union[np.ndarray, List[float]],
        f_sig: float,
        f_harm: float,
        a_harm: float,
        phase: float,
        n_harm: int = 1,
    ) -> np.ndarray:
        """Create and calculate a signal of the specified type.
        
        Args:
            wave_type: Registered signal name (e.g., 'Sine', 'Square').
            t: Time vector for evaluation.
            f_sig: Fundamental/carrier frequency in Hz.
            f_harm: Harmonic/modulation frequency in Hz.
            a_harm: Amplitude/index parameter (typically 0-1).
            phase: Initial phase in radians.
            n_harm: Number of harmonics (for Fourier-based waves).
        
        Returns:
            Signal values as numpy array.
        """
        signal_class = cls._signals.get(wave_type)
        if signal_class:
            return signal_class(t, f_sig, f_harm, a_harm, phase, n_harm).calculate()
        else:
            return np.zeros_like(t)

    @classmethod
    def get_signal_names(cls) -> List[str]:
        """Return list of all registered signal type names.
        
        Returns:
            Sorted list of available signal type identifiers.
        """
        return list(cls._signals.keys())

    @classmethod
    def get_max_freq(
        cls, wave_type: str, f_sig: float, f_harm: float, a_harm: float, n_harm: int = 1
    ) -> float:
        """Predict the highest frequency component for Nyquist analysis.
        
        Critical for determining required sampling rate and detecting aliasing.
        Uses mathematical properties of each signal type to estimate bandwidth.
        
        Args:
            wave_type: Signal type name.
            f_sig: Fundamental or carrier frequency.
            f_harm: Harmonic or modulation frequency.
            a_harm: Amplitude or modulation index.
            n_harm: Number of synthesized harmonics.
        
        Returns:
            Estimated highest frequency component in Hz.
        
        Notes:
            - AM: Sidebands at f_sig ± f_harm
            - FM: Carson's rule: f_sig + (a_harm + 1) * f_harm
            - Chirp: Maximum of start and end frequencies
            - Fourier waves: Fundamental times highest harmonic order
        """
        if wave_type == "AM":
            return f_sig + f_harm if a_harm > 0 else f_sig
        if wave_type == "FM":
            # Carson's Rule for FM bandwidth
            return f_sig + (a_harm + 1) * f_harm if a_harm > 0 else f_sig
        if wave_type == "Chirp":
            return max(f_sig, f_harm)

        # For Fourier-based waves, highest freq = f_sig * highest_harmonic_order
        multiplier = (2 * n_harm - 1) if wave_type in ["Square", "Triangle"] else n_harm
        base_max = f_sig * multiplier
        return max(base_max, f_harm if a_harm > 0 else 0)


# Register all available signal types
SignalRegistry.register_signal("Sine", SineWave)
SignalRegistry.register_signal("Square", SquareWave)
SignalRegistry.register_signal("Sawtooth", SawtoothWave)
SignalRegistry.register_signal("Triangle", TriangleWave)
SignalRegistry.register_signal("AM", AMWave)
SignalRegistry.register_signal("FM", FMWave)
SignalRegistry.register_signal("Chirp", ChirpWave)