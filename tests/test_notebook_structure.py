import json
from pathlib import Path


NOTEBOOK = Path(__file__).parents[1] / "AliasingAtlas.ipynb"


def test_notebook_is_valid_json_with_executable_cells():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))

    assert notebook["cells"]
    assert all(cell.get("cell_type") in {"markdown", "code", "raw"} for cell in notebook["cells"])
    assert any(cell.get("cell_type") == "code" for cell in notebook["cells"])


def test_notebook_setup_mentions_both_supported_environments():
    text = NOTEBOOK.read_text(encoding="utf-8")

    assert "google.colab" in text
    assert "aliasing_atlas.app" in text
    assert "src" in text
