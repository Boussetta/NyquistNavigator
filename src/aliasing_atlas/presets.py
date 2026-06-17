"""Curated pedagogical presets for AliasingAtlas."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Preset:
    name: str
    f_sig: float
    f_samp: float
    f_harm: float
    a_harm: float
    phase: float
    n_harm: int
    bits: int
    wave_type: str
    aaf_type: str
    recon_type: str
    window_type: str


PRESETS: Dict[str, Preset] = {
    "Safe Nyquist": Preset(
        name="Safe Nyquist",
        f_sig=10.0,
        f_samp=100.0,
        f_harm=20.0,
        a_harm=0.0,
        phase=0.0,
        n_harm=1,
        bits=16,
        wave_type="Sine",
        aaf_type="None",
        recon_type="FFT",
        window_type="None",
    ),
    "Near Nyquist": Preset(
        name="Near Nyquist",
        f_sig=10.0,
        f_samp=22.0,
        f_harm=20.0,
        a_harm=0.0,
        phase=0.0,
        n_harm=1,
        bits=16,
        wave_type="Sine",
        aaf_type="None",
        recon_type="FFT",
        window_type="None",
    ),
    "Aliasing": Preset(
        name="Aliasing",
        f_sig=10.0,
        f_samp=15.0,
        f_harm=20.0,
        a_harm=0.0,
        phase=0.0,
        n_harm=1,
        bits=16,
        wave_type="Sine",
        aaf_type="None",
        recon_type="FFT",
        window_type="None",
    ),
    "AM Sidebands": Preset(
        name="AM Sidebands",
        f_sig=25.0,
        f_samp=180.0,
        f_harm=3.0,
        a_harm=0.7,
        phase=0.0,
        n_harm=1,
        bits=12,
        wave_type="AM",
        aaf_type="Ideal",
        recon_type="FFT",
        window_type="Hann",
    ),
}


def preset_names() -> List[str]:
    return list(PRESETS.keys())


def get_preset(name: str) -> Preset:
    return PRESETS[name]
