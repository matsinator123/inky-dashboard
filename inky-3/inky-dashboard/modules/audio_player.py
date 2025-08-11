"""
Generic audio playback utilities for the dashboard.

- Deterministic backend selection with variants for better Pi compatibility:
  cvlc, mpg123 (PulseAudio), mpg123, mpg321, ffplay, omxplayer
- Async playback with ability to stop
- Short post-start check to detect immediate failures
- Robust logging to aid troubleshooting
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from typing import Optional, List

__all__ = ["play", "stop", "is_playing", "selected_backend"]

# Logger
logger = logging.getLogger(__name__)

# Internal state
_proc: Optional[subprocess.Popen] = None
_backend_cmd: Optional[List[str]] = None

# Backend candidates in priority order
_BACKENDS: List[List[str]] = [
    ["cvlc", "--no-video", "--play-and-exit", "--intf", "dummy", "--quiet"],
    ["mpg123", "-a", "pulse", "-q"],
    ["mpg123", "-q"],
    ["mpg321", "-q"],
    ["ffplay", "-autoexit", "-nodisp", "-v", "quiet"],
    ["omxplayer"],
]


def _detect_backend() -> Optional[List[str]]:
    for cmd in _BACKENDS:
        if shutil.which(cmd[0]):
            logger.info(f"Audio backend selected: {' '.join(cmd)}")
            return cmd
    logger.warning("No audio backend found (looked for cvlc, mpg123, mpg321, ffplay, omxplayer)")
    return None


def selected_backend() -> Optional[str]:
    return " ".join(_backend_cmd) if _backend_cmd else None


def _ensure_backend() -> bool:
    global _backend_cmd
    if _backend_cmd is None:
        _backend_cmd = _detect_backend()
    return _backend_cmd is not None


def _stop_proc_if_running() -> None:
    global _proc
    if _proc and _proc.poll() is None:
        try:
            _proc.terminate()
            try:
                _proc.wait(timeout=1.0)
            except Exception:
                try:
                    _proc.kill()
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Error stopping audio process: {e}")
    _proc = None


def play(file_path: str) -> bool:
    """Play an audio file asynchronously. Returns True if playback started."""
    global _proc

    if not os.path.exists(file_path):
        logger.warning(f"Audio file not found: {file_path}")
        return False

    if not _ensure_backend():
        return False

    # Stop any existing playback
    _stop_proc_if_running()

    cmd = list(_backend_cmd) + [file_path]
    try:
        _proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Playing audio via {_backend_cmd[0]}: {os.path.basename(file_path)}")

        # Detect immediate failure (e.g., device busy). Give it a brief moment.
        time.sleep(0.2)
        if _proc.poll() is not None and _proc.returncode not in (0, None):
            logger.error(f"Audio backend {_backend_cmd[0]} exited immediately with code {_proc.returncode}")
            _proc = None
            return False
        return True
    except Exception as e:
        logger.error(f"Failed to start audio: {e}")
        _proc = None
        return False


def stop() -> None:
    """Stop current playback, if any."""
    _stop_proc_if_running()


def is_playing() -> bool:
    """Return True if an audio backend seems to be playing."""
    return _proc is not None and _proc.poll() is None
