import sys
from pathlib import Path

# Ensure src-layout imports work without requiring editable install.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aliasing_atlas.presets import get_preset, preset_names


def test_presets_have_expected_scenarios():
    names = preset_names()
    assert "Safe Nyquist" in names
    assert "Near Nyquist" in names
    assert "Aliasing" in names
    assert "AM Sidebands" in names


def test_aliasing_preset_is_below_nyquist():
    p = get_preset("Aliasing")
    assert p.f_samp < 2 * p.f_sig


def test_safe_preset_is_above_nyquist():
    p = get_preset("Safe Nyquist")
    assert p.f_samp >= 2 * p.f_sig
