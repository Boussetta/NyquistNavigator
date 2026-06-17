"""Contextual hint generation for guided learning mode.

This module provides pedagogically-targeted hints that adapt to the current
simulator state. Hints guide users toward understanding key DSP concepts by
highlighting active phenomena:

    - Aliasing: When fs < 2*f_max, explains the issue and remedies
    - Quantization: When bit depth is insufficient, explains SNR loss
    - Anti-Aliasing: When sampling near Nyquist without filtering
    - Reconstruction: Comparing reconstruction methods
    - Modulation: Understanding bandwidth expansion

The hints are context-aware, non-intrusive, and encourage experimental learning
by suggesting the most relevant concept for the current parameter state.

Design Philosophy:
    - One hint per update cycle (prioritized by educational value)
    - Hints reference specific parameters from the current state
    - Language is encouraging, not prescriptive
    - Hints progress from basic concepts to advanced topics
"""


def build_learning_hint(
    wave_type: str,
    aliased: bool,
    max_freq: float,
    f_samp: float,
    recon_type: str,
    aaf_type: str,
    bits: int,
) -> str:
    """Generate context-aware pedagogical hint based on simulator state.
    
    Implements a priority-based system that selects the most relevant hint
    for the current parameter configuration. Priority order:
    
        1. Critical: Aliasing is active
        2. High: Quantization is severely limited
        3. Medium: Sampling near Nyquist without filter
        4. Low: Informational (reconstruction methods, modulation effects)
    
    Args:
        wave_type: Current signal type (Sine, Square, AM, FM, Chirp, etc.).
        aliased: Boolean indicating if aliasing is active.
        max_freq: Highest frequency component in Hz.
        f_samp: Sampling frequency in Hz.
        recon_type: Active reconstruction method (FFT or FOH).
        aaf_type: Active anti-alias filter type (None, Ideal, Butter).
        bits: Quantization bit depth.
    
    Returns:
        A human-readable hint string (max ~150 characters for UI display).
    
    Examples:
        >>> build_learning_hint('Sine', True, 50.0, 60.0, 'FFT', 'None', 16)
        'Learning: Aliasing is active because fs=60.0 Hz is below 2*fmax=100.0 Hz...'
    """
    nyquist = 2 * max_freq

    # Priority 1: Aliasing detection
    if aliased:
        return (
            f"Learning: Aliasing is active because fs={f_samp:.1f} Hz is below 2*fmax={nyquist:.1f} Hz. "
            "Increase sampling or lower bandwidth to recover the intended signal."
        )

    # Priority 2: Severe quantization
    if bits <= 4:
        return (
            "Learning: Nyquist is satisfied, but quantization is coarse. "
            "Increase bit depth to reduce staircase noise and improve SNR."
        )

    # Priority 3: Operating near Nyquist without protection
    if aaf_type == "None" and f_samp <= nyquist * 1.2:
        return (
            "Learning: You are near Nyquist. Enable an anti-alias filter to suppress out-of-band components "
            "before sampling."
        )

    # Priority 4: Reconstruction method explanation
    if recon_type == "FOH":
        return (
            "Learning: FOH improves over ZOH by linearly connecting samples. "
            "Compare with FFT reconstruction to inspect spectral fidelity."
        )

    # Priority 5: Modulation bandwidth
    if wave_type in ("AM", "FM", "Chirp"):
        return (
            "Learning: Modulated/swept signals occupy wider bandwidth than a single tone. "
            "Track fmax and keep fs comfortably above Nyquist."
        )

    # Default: Stable region
    return "Learning: Stable sampling regime. Try reducing fs toward Nyquist to observe the transition boundary."
