"""Contextual hint generation for guided learning mode."""


def build_learning_hint(
    wave_type: str,
    aliased: bool,
    max_freq: float,
    f_samp: float,
    recon_type: str,
    aaf_type: str,
    bits: int,
) -> str:
    nyquist = 2 * max_freq

    if aliased:
        return (
            f"Learning: Aliasing is active because fs={f_samp:.1f} Hz is below 2*fmax={nyquist:.1f} Hz. "
            "Increase sampling or lower bandwidth to recover the intended signal."
        )

    if bits <= 4:
        return (
            "Learning: Nyquist is satisfied, but quantization is coarse. "
            "Increase bit depth to reduce staircase noise and improve SNR."
        )

    if aaf_type == "None" and f_samp <= nyquist * 1.2:
        return (
            "Learning: You are near Nyquist. Enable an anti-alias filter to suppress out-of-band components "
            "before sampling."
        )

    if recon_type == "FOH":
        return (
            "Learning: FOH improves over ZOH by linearly connecting samples. "
            "Compare with FFT reconstruction to inspect spectral fidelity."
        )

    if wave_type in ("AM", "FM", "Chirp"):
        return (
            "Learning: Modulated/swept signals occupy wider bandwidth than a single tone. "
            "Track fmax and keep fs comfortably above Nyquist."
        )

    return "Learning: Stable sampling regime. Try reducing fs toward Nyquist to observe the transition boundary."
