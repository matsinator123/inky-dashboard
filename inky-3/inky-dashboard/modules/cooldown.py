"""
Cooldown mode handler for the dashboard.
Shows special screens during specific time periods.
"""

from datetime import datetime, time
from PIL import Image
from modules.calendar_data import next_daniel_day
import os

__all__ = ["should_show_cooldown", "load_cooldown_image"]

import logging

# Reusable audio player utilities
from modules.audio_player import play as play_audio
from modules.audio_player import stop as stop_audio
from modules.audio_player import selected_backend

__all__ = [
    "should_show_cooldown",
    "load_cooldown_image",
    "play_cooldown_audio",
    "reset_cooldown_audio_state",
]

logger = logging.getLogger(__name__)

# Resolve project root and asset paths robustly regardless of CWD
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_DIR = os.path.join(ROOT_DIR, "assets", "audio")


def is_time_between(start: time, end: time, now: time = None) -> bool:
    """Check if current time is between start and end times."""
    now = now or datetime.now().time()
    if start < end:
        return start <= now < end
    else:  # crosses midnight
        return now >= start or now < end


def should_show_cooldown() -> str | None:
    """Check if we should show a cooldown screen based on current time."""
    now = datetime.now().time()

    # Daniel scene only shown if it's a Daniel-day
    if is_time_between(time(19, 0), time(20, 0), now) and next_daniel_day() == 0:
        return "daniel"
    elif is_time_between(time(22, 0), time(23, 0), now):
        return "evening"
    elif is_time_between(time(23, 0), time(5, 0), now):
        return "night"
    return None


def load_cooldown_image(mode: str) -> Image.Image | None:
    """Load a cooldown image by mode name."""
    filename = f"{mode}.png"
    path = os.path.join("assets", "cooldown", filename)
    try:
        return Image.open(path).convert("RGB")
    except Exception:
        return None


# --- Cooldown-specific audio integration ---
_last_audio_mode: str | None = None


_AUDIO_MAP = {
    "daniel": os.path.join(AUDIO_DIR, "natta_daniel.mp3"),
    "night": os.path.join(AUDIO_DIR, "natta_pappa.mp3"),
}


def play_cooldown_audio(mode: str) -> None:
    """Play the appropriate audio cue for a given cooldown mode once per mode entry."""
    global _last_audio_mode

    file_path = _AUDIO_MAP.get(mode)
    if not file_path:
        return

    # Avoid replaying if we're still in the same mode
    if _last_audio_mode == mode:
        return

    if not os.path.exists(file_path):
        logger.warning(f"Cooldown audio file missing for mode '{mode}': {file_path}")
        _last_audio_mode = mode  # avoid spamming attempts
        return

    # start playback; log backend used for troubleshooting
    try:
        ok = play_audio(file_path)
        backend = selected_backend()
        if not ok:
            logger.warning(f"Failed to play '{file_path}'. Backend={backend}")
        else:
            logger.info(f"Cooldown audio started for mode '{mode}' using backend '{backend}' (file: {file_path})")
    except Exception as e:
        logger.error(f"Exception starting cooldown audio for mode '{mode}': {e}")
    finally:
        _last_audio_mode = mode


def reset_cooldown_audio_state() -> None:
    """Reset audio state so the next time a cooldown mode is entered it can play again."""
    global _last_audio_mode
    _last_audio_mode = None
    try:
        stop_audio()
    except Exception as e:
        logger.debug(f"Error stopping cooldown audio: {e}")
