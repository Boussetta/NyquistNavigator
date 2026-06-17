import numpy as np
from aliasing_atlas.signals import SignalRegistry

def test_signal_calculation_sine():
    """Verify that the sine wave generation is mathematically correct."""
    # Create 1 second of a 1Hz sine wave at 4Hz sampling
    t = np.array([0, 0.25, 0.5, 0.75])
    f_sig = 1.0
    f_harm = 10.0 # Should be ignored if amplitude is 0
    a_harm = 0.0
    phase = 0.0
    
    y = SignalRegistry.create_signal('Sine', t, f_sig, f_harm, a_harm, phase)
    
    # Expected: sin(0), sin(pi/2), sin(pi), sin(3pi/2) -> [0, 1, 0, -1]
    expected = np.array([0.0, 1.0, 0.0, -1.0])
    np.testing.assert_allclose(y, expected, atol=1e-7)

def test_signal_calculation_triangle():
    """Verify first-harmonic triangle approximation behavior."""
    t = np.array([0, 0.25, 0.5, 0.75, 1.0])
    f_sig = 1.0
    f_harm = 0.0
    a_harm = 0.0
    phase = 0.0
    
    y = SignalRegistry.create_signal('Triangle', t, f_sig, f_harm, a_harm, phase)
    
    # With n_harm=1, the implementation returns the first odd Fourier harmonic only.
    expected = (8 / np.pi**2) * np.sin(2 * np.pi * f_sig * t + phase)
    np.testing.assert_allclose(y, expected, atol=1e-7)

def test_signal_registry_max_freq_for_square():
    """Verify max-frequency prediction for Fourier-based waves."""
    max_freq = SignalRegistry.get_max_freq('Square', f_sig=5.0, f_harm=30.0, a_harm=0.0, n_harm=4)
    assert max_freq == 35.0