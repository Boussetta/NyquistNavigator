import numpy as np
from typing import Union, List, Dict, Type
from abc import ABC, abstractmethod

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
        base = 2 * (self.f_sig * self.t + self.phase/(2*np.pi) - np.floor(0.5 + self.f_sig * self.t + self.phase/(2*np.pi)))
        harm = self.a_harm * 2 * (self.f_harm * self.t - np.floor(0.5 + self.f_harm * self.t))
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
    def create_signal(cls, wave_type: str, t: Union[np.ndarray, List[float]], f_sig: float, f_harm: float, a_harm: float, phase: float) -> np.ndarray:
        signal_class = cls._signals.get(wave_type)
        if signal_class:
            return signal_class(t, f_sig, f_harm, a_harm, phase).calculate()
        else:
            return np.zeros_like(t)

    @classmethod
    def get_signal_names(cls) -> List[str]:
        return list(cls._signals.keys())

    @classmethod
    def get_max_freq(cls, wave_type: str, f_sig: float, f_harm: float, a_harm: float) -> float:
        """Predicts the highest frequency component for Nyquist analysis."""
        if wave_type == 'AM':
            return f_sig + f_harm if a_harm > 0 else f_sig
        if wave_type == 'FM':
            return f_sig + (a_harm + 1) * f_harm if a_harm > 0 else f_sig
        return max(f_sig, f_harm if a_harm > 0 else 0)

SignalRegistry.register_signal('Sine', SineWave)
SignalRegistry.register_signal('Square', SquareWave)
SignalRegistry.register_signal('Sawtooth', SawtoothWave)
SignalRegistry.register_signal('AM', AMWave)
SignalRegistry.register_signal('FM', FMWave)