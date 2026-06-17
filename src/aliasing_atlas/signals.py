import numpy as np
from typing import Union, List, Dict, Type
from abc import ABC, abstractmethod

class Signal(ABC):
    """Abstract base class for all signal types."""
    def __init__(self, t: Union[np.ndarray, List[float]], f_sig: float, f_harm: float, a_harm: float, phase: float, n_harm: int = 1):
        self.t = t
        self.f_sig = f_sig
        self.f_harm = f_harm
        self.a_harm = a_harm
        self.phase = phase
        self.n_harm = n_harm

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
        # Fourier: Sum of (1/k)*sin(2*pi*k*f*t) for k = 1, 3, 5...
        base = np.zeros_like(self.t)
        for i in range(self.n_harm):
            k = 2 * i + 1
            base += (1.0 / k) * np.sin(2 * np.pi * k * self.f_sig * self.t + self.phase)
        base = (4 / np.pi) * base
        harm = self.a_harm * np.sign(np.sin(2 * np.pi * self.f_harm * self.t))
        return base + harm

class SawtoothWave(Signal):
    def calculate(self) -> np.ndarray:
        # Fourier: Sum of ((-1)^k/k)*sin(2*pi*k*f*t)
        base = np.zeros_like(self.t)
        for k in range(1, self.n_harm + 1):
            base += ((-1)**(k+1) / k) * np.sin(2 * np.pi * k * self.f_sig * self.t + self.phase)
        base = (2 / np.pi) * base
        harm = self.a_harm * 2 * (self.f_harm * self.t - np.floor(0.5 + self.f_harm * self.t))
        return base + harm

class TriangleWave(Signal):
    def calculate(self) -> np.ndarray:
        # Fourier: Sum of ((-1)^k/(2k+1)^2)*sin(2*pi*(2k+1)*f*t)
        base = np.zeros_like(self.t)
        for i in range(self.n_harm):
            k = 2 * i + 1
            sign = (-1)**i
            base += (sign / (k**2)) * np.sin(2 * np.pi * k * self.f_sig * self.t + self.phase)
        base = (8 / np.pi**2) * base
        harm = self.a_harm * (2 * np.abs(2 * (self.f_harm * self.t - np.floor(self.f_harm * self.t + 0.5))) - 1)
        return base + harm

class AMWave(Signal):
    def calculate(self) -> np.ndarray:
        base = (1 + self.a_harm * np.sin(2 * np.pi * self.f_harm * self.t)) * np.sin(2 * np.pi * self.f_sig * self.t + self.phase)
        return base

class FMWave(Signal):
    def calculate(self) -> np.ndarray:
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
    def create_signal(cls, wave_type: str, t: Union[np.ndarray, List[float]], f_sig: float, f_harm: float, a_harm: float, phase: float, n_harm: int = 1) -> np.ndarray:
        signal_class = cls._signals.get(wave_type)
        if signal_class:
            return signal_class(t, f_sig, f_harm, a_harm, phase, n_harm).calculate()
        else:
            return np.zeros_like(t)

    @classmethod
    def get_signal_names(cls) -> List[str]:
        return list(cls._signals.keys())

    @classmethod
    def get_max_freq(cls, wave_type: str, f_sig: float, f_harm: float, a_harm: float, n_harm: int = 1) -> float:
        """Predicts the highest frequency component for Nyquist analysis."""
        if wave_type == 'AM':
            return f_sig + f_harm if a_harm > 0 else f_sig
        if wave_type == 'FM':
            return f_sig + (a_harm + 1) * f_harm if a_harm > 0 else f_sig
        
        # For Fourier-based waves, the max freq is f_sig * highest_harmonic_order
        multiplier = (2 * n_harm - 1) if wave_type in ['Square', 'Triangle'] else n_harm
        base_max = f_sig * multiplier
        return max(base_max, f_harm if a_harm > 0 else 0)

SignalRegistry.register_signal('Sine', SineWave)
SignalRegistry.register_signal('Square', SquareWave)
SignalRegistry.register_signal('Sawtooth', SawtoothWave)
SignalRegistry.register_signal('Triangle', TriangleWave)
SignalRegistry.register_signal('AM', AMWave)
SignalRegistry.register_signal('FM', FMWave)