"""
Cooldown mode handler for the dashboard.
Shows special screens during specific time periods.
"""

from datetime import datetime, time
from PIL import Image
from modules.calendar_data import next_daniel_day
import os

__all__ = ["should_show_cooldown", "load_cooldown_image"]

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
