"""
Weather display for the dashboard.
Draws min, current, and max temperature with a weather icon.
"""

from modules.weather_data import get_weather_icon_path
from PIL import Image, ImageFont
import logging
from colors import COLORS
import os

__all__ = ["draw_weather"]

def draw_weather(draw, image, x, y, weather_data):
    """
    Draw weather info: min temp, current temp, max temp in horizontal layout, plus icon.
    """
    weather = weather_data
    if "error" in weather:
        try:
            error_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except Exception:
            error_font = ImageFont.load_default()
        draw.text((x, y), "Weather Error", fill=COLORS["red"], font=error_font)
        logging.warning("Weather data contained error; displayed error notice")
        return

    # Try to load a big, clear font
    try:
        big_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
    except Exception:
        big_font = ImageFont.load_default()

    # Extract temps
    temp_min = weather.get("temp_min", "--")
    temp = weather.get("temp", "--")
    temp_max = weather.get("temp_max", "--")

    # Colors for each temperature
    color_min = COLORS.get("blue", (0, 100, 200))
    color_now = COLORS.get("orange", (255, 140, 0))
    color_max = COLORS.get("red", (200, 50, 50))

    # Horizontal positions (adjust these to fit your display)
    spacing = 140  # Space between temperatures
    x_min = x
    x_now = x + spacing
    x_max = x + (spacing * 2)
    y_temp = y

    # Draw temperatures
    draw.text((x_min, y_temp), f"{temp_min}-", fill=color_min, font=big_font)
    draw.text((x_now, y_temp), f"{temp}-", fill=color_now, font=big_font)
    draw.text((x_max, y_temp), f"{temp_max} ", fill=color_max, font=big_font)

    # Draw simple separating lines between temps
    line_color = COLORS.get("gray", (128, 128, 128))
    line_y = y_temp + 75  # Position lines below the text
    line_length = 30

    # Line between min and current
    line1_start = x_min + 60
    draw.line((line1_start, line_y, line1_start + line_length, line_y), fill=line_color, width=2)

    # Line between current and max
    line2_start = x_now + 60
    draw.line((line2_start, line_y, line2_start + line_length, line_y), fill=line_color, width=2)

    # Draw weather icon (left of temps)
    icon_path = get_weather_icon_path(weather)
    try:
        if os.path.exists(icon_path):
            icon = Image.open(icon_path).convert("RGBA")
            icon = icon.resize((200, 200))
            image.paste(icon, (x - 200, y - 1), icon)
    except Exception as e:
        logging.warning(f"Failed to paste weather icon {icon_path}: {e}")
