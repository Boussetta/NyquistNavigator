"""Simulated mouse interaction: no RuntimeError from overlapping or stale widgets (#27)."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from matplotlib.backend_bases import MouseEvent

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture
def toolbox():
    from aliasing_atlas.app import AliasingToolbox

    tb = AliasingToolbox()
    tb.fig.canvas.draw()
    yield tb
    plt.close(tb.fig)


def _event(tb, name, ax, fx=0.5):
    canvas = tb.fig.canvas
    bb = ax.get_window_extent()
    x, y = bb.x0 + fx * (bb.x1 - bb.x0), (bb.y0 + bb.y1) / 2
    canvas.callbacks.process(name, MouseEvent(name, canvas, x, y, button=1))


def _click(tb, ax, fx=0.5):
    _event(tb, "button_press_event", ax, fx)
    _event(tb, "button_release_event", ax, fx)


@pytest.mark.parametrize("tab", ["Signal", "Sampling", "Audio"])
def test_every_control_on_every_tab_is_clickable(toolbox, tab, tmp_path, monkeypatch):
    from aliasing_atlas import app as app_module

    monkeypatch.chdir(tmp_path)  # Export buttons write files
    monkeypatch.setattr(app_module, "sd", None)  # Play Audio must not use the real sound card
    monkeypatch.setattr(app_module, "display", None)
    toolbox._update_tab_visibility(tab)
    for ax in [*toolbox.tab_groups[tab], toolbox.cax_f_sig, toolbox.cax_f_samp, toolbox.cax_preset]:
        _click(toolbox, ax, 0.3)
    assert toolbox.fig.canvas.mouse_grabber is None


def test_hidden_tab_sliders_do_not_move(toolbox):
    volume, duration = toolbox.s_vol.val, toolbox.s_dur.val
    _click(toolbox, toolbox.cax_f_harm, 0.9)  # Audio Vol sits at the same spot on the hidden tab
    _click(toolbox, toolbox.cax_a_harm, 0.9)  # ... and Audio Dur
    assert (toolbox.s_vol.val, toolbox.s_dur.val) == (volume, duration)
    assert toolbox.s_f_harm_amp.val > 0.5


def test_lost_mouse_release_does_not_block_other_sliders(toolbox):
    _event(toolbox, "button_press_event", toolbox.cax_f_harm)  # drag starts, mouse-up never arrives
    _click(toolbox, toolbox.cax_f_sig, 0.8)
    assert toolbox.fig.canvas.mouse_grabber is None
    assert toolbox.s_f_sig.val > 30


def test_leaving_the_figure_ends_drags(toolbox):
    _event(toolbox, "button_press_event", toolbox.cax_f_samp)
    toolbox._end_active_drags()  # bound to figure_leave_event
    assert toolbox.fig.canvas.mouse_grabber is None
    assert not toolbox.s_f_samp.drag_active
