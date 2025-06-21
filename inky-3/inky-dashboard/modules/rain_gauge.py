"""
Rain gauge overlay for the dashboard.
Calculates rain level from forecast and overlays the appropriate image.
"""

from PIL import Image
import os

def get_rain_gauge_level_from_forecast(forecast_data):
    """
    Calculate a rain level from 1 to 4 based on the accumulated precipitation
    in the next 6 hours.
    """
    rain_total = 0.0
    steps = forecast_data["properties"]["timeseries"][:6]  # next ~6 hours
    for step in steps:
        details = step["data"].get("next_1_hours", {}).get("details", {})
        rain_total += details.get("precipitation_amount", 0.0)

    if rain_total >= 6:
        return 4  # very rainy
    elif rain_total >= 3:
        return 3  # rainy
    elif rain_total > 0:
        return 2  # light rain
    else:
        return 1  # dry

def draw_rain_gauge(image, forecast_data):
    """
    Overlay the rain gauge image corresponding to the forecasted rain level.
    """
    level = get_rain_gauge_level_from_forecast(forecast_data)
    filename = f"rain_gauge_{level}.png"
    path = os.path.join("assets", "appliances", filename)

    try:
        overlay = Image.open(path).convert("RGBA")
        image.paste(overlay, (0, 0), overlay)
    except Exception:
        pass
