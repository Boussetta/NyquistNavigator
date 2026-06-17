"""Export helpers for saving configurations and audio artifacts.

This module provides utilities for exporting simulator state and audio data
in standard formats for:

    - Data Sharing: Save configurations as JSON for reproducibility
    - Audio Analysis: Export audio as standard PCM16 WAV files
    - Version Control: Timestamp-based file organization
    - Long-term Storage: Platform-independent formats (JSON, WAV)

Capabilities:
    - JSON configuration export (all simulator parameters)
    - PCM16 WAV audio export (16-bit mono, configurable sample rate)
    - Automatic export directory creation
    - Timestamp-based file naming for organization
    - Platform-independent pathlib usage

Typical Workflow:
    1. User clicks "Export Config" → save_config_json() creates timestamped JSON
    2. User clicks "Export Audio" → write_wav_mono16() creates timestamped WAV
    3. Files are saved to exports/ directory with descriptive filenames
    4. User can import JSON config to recreate exact simulator state
"""

from __future__ import annotations

import json
import wave
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np


def timestamp_tag(now: Optional[datetime] = None) -> str:
    """Return a compact timestamp string for file naming.
    
    Creates a sortable, human-readable timestamp suitable for filenames.
    Format: YYYYMMDD_HHMMSS (e.g., 20240617_143022)
    
    Args:
        now: Optional datetime object. If None, uses current time.
    
    Returns:
        Compact 15-character timestamp string.
    
    Examples:
        >>> from datetime import datetime
        >>> timestamp_tag(datetime(2024, 6, 17, 14, 30, 22))
        '20240617_143022'
    """
    current = now or datetime.now()
    return current.strftime("%Y%m%d_%H%M%S")


def ensure_export_dir(base_dir: str = "exports") -> Path:
    """Ensure export directory exists and return it as Path object.
    
    Creates the export directory structure if it doesn't exist. Uses pathlib
    for platform-independent path handling (Works on Windows, macOS, Linux).
    
    Args:
        base_dir: Directory name for exports. Default is "exports".
    
    Returns:
        Path object pointing to the export directory.
    
    Examples:
        >>> export_path = ensure_export_dir()
        >>> export_path
        PosixPath('exports')
        >>> export_path.exists()
        True
    """
    out_dir = Path(base_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def save_config_json(path: Path, payload: Dict[str, Any]) -> Path:
    """Save configuration payload as pretty-printed JSON.
    
    Exports simulator state as a structured JSON file with 2-space indentation
    and sorted keys for readability and version control friendliness.
    
    Args:
        path: Target file path (Path object or string).
        payload: Dictionary containing simulator configuration.
                Should include signal params, DSP settings, and metadata.
    
    Returns:
        Path object pointing to the saved file.
    
    Raises:
        IOError: If file cannot be written (permission denied, etc.).
    
    Examples:
        >>> config = {'f_sig': 10.0, 'f_samp': 100.0, 'bits': 16}
        >>> path = Path('exports/config.json')
        >>> save_config_json(path, config)
        PosixPath('exports/config.json')
    
    Notes:
        - JSON is always UTF-8 encoded
        - Pretty-printed with 2-space indentation for readability
        - Keys are sorted alphabetically for reproducibility
    """
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    return path


def write_wav_mono16(path: Path, samples: np.ndarray, sample_rate: int) -> Path:
    """Write mono PCM16 WAV file from floating-point audio samples.
    
    Converts normalized floating-point audio [-1.0, +1.0] to 16-bit signed
    integer PCM format and writes a standard WAVE file. This format is compatible
    with virtually all audio software and devices.
    
    Bit Depth: 16-bit (65,536 levels, standard for CD-quality audio)
    Channels: 1 (mono)
    Byte Order: Little-endian (standard for WAVE format on Intel/ARM)
    
    Args:
        path: Target file path (Path object or string).
        samples: Floating-point audio array, values should be in [-1.0, +1.0].
                Will be clipped if out of range to prevent distortion.
        sample_rate: Playback sample rate in Hz (e.g., 16000, 44100, 48000).
    
    Returns:
        Path object pointing to the created WAV file.
    
    Raises:
        IOError: If file cannot be written.
        OverflowError: If array operations fail (unlikely with proper inputs).
    
    Examples:
        >>> import numpy as np
        >>> t = np.linspace(0, 1, 44100)
        >>> audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine (A note)
        >>> write_wav_mono16(Path('test.wav'), audio, 44100)
        PosixPath('test.wav')
    
    Notes:
        - Audio is automatically clipped to [-1.0, +1.0] to prevent overflow
        - PCM16 range: -32768 to +32767 (maps [-1.0, +1.0] linearly)
        - Typical sample rates: 8000 (telephony), 16000 (speech),
          44100 (CD), 48000 (professional audio)
    """
    x = np.asarray(samples, dtype=np.float64)
    
    # Clip to valid range to prevent integer overflow
    x = np.clip(x, -1.0, 1.0)
    
    # Convert to PCM16 (range: -32768 to +32767)
    pcm = (x * 32767.0).astype(np.int16)

    # Write WAVE file with standard parameters
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)          # Mono
        wf.setsampwidth(2)          # 16-bit = 2 bytes
        wf.setframerate(int(sample_rate))
        wf.writeframes(pcm.tobytes())

    return path
