"""
AliasingAtlas Legacy Entry Point.

This script is kept for backward compatibility and as a quick entry point.
The core logic has been moved to the 'aliasing_atlas' package in the src/ directory.
"""

import sys
import os
import warnings

# Professional touch: add src/ to path so this works even without pip install
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from aliasing_atlas.app import AliasingToolbox
except ImportError:
    print("Error: Could not find 'aliasing_atlas'. Ensure you are running from the project root.")
    sys.exit(1)

if __name__ == "__main__":
    warnings.warn(
        "sinewave-ampling.py is deprecated. Use 'python -m aliasing_atlas' "
        "or the 'aliasing-atlas' command after installation.",
        DeprecationWarning
    )
    app = AliasingToolbox()
    app.show()