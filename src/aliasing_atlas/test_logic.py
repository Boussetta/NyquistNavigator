import numpy as np
import pytest
from aliasing_atlas.app import SignalRegistry, AliasingToolbox

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

def test_aliasing_detection_logic():
    """Simple check for frequency limits."""
    app = AliasingToolbox()
    assert app.f_sig_max == 50.0
    assert app.f_samp_max == 1500.0