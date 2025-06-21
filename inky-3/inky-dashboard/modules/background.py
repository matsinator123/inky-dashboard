"""
Background image loader for the dashboard display.
Currently hardcoded to use spring background.
"""

from PIL import Image
import os

# Display configuration
DISPLAY_SIZE = (1600, 1200)
BACKGROUND_PATH = os.path.join("assets", "backgrounds", "spring.jpg")

def get_season_for_date(today=None):
    """Get the current season. Currently hardcoded to spring."""
    return "spring"

def load_background(season=None):
    """Load and resize the background image for the display."""
    try:
        image = Image.open(BACKGROUND_PATH).convert("RGB")
        return image.resize(DISPLAY_SIZE)
    except Exception:
        # Return white background as fallback
        return Image.new("RGB", DISPLAY_SIZE, "white")

__all__ = ["load_background", "get_season_for_date"]
