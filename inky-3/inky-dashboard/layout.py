import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import logging

from colors import COLORS
from modules.background import load_background
from modules.weather import draw_weather
from modules.weather_data import get_weather
from modules.appliances import draw_appliances_and_layers, get_layer_image, get_appliance_state
from modules.calendar_ui import draw_calendar_text, draw_daniel_note
from modules.cooldown import should_show_cooldown, load_cooldown_image
from modules.rain_gauge import draw_rain_gauge
from modules.state_handler import initialize_state_if_missing, save_state
from modules.spotify_display import draw_spotify_screen

# Display configuration
WIDTH, HEIGHT = 1600, 1200
FONT_SIZE = 36
HAND_FONT_SIZE = 32
FONT_PATH = "assets/fonts/GochiHand-Regular.ttf"

def reset_state_if_empty():
    """Reset appliance state to defaults if empty."""
    appliances = get_appliance_state()
    if not appliances:
        logging.info("Appliance state empty - resetting to defaults")
        now = datetime.now()
        default_state = {
            "washing_machine": {"last_run": now - timedelta(hours=3), "is_running": False},
            "vacuum": {"last_run": now - timedelta(hours=3), "is_running": False},
            "dryer": {"last_run": now - timedelta(hours=3), "is_running": False},
            "dishwasher": {"last_run": now - timedelta(hours=3), "is_running": False},
        }
        save_state(default_state)
        return get_appliance_state()
    return appliances

def load_fonts():
    """Load fonts with fallbacks."""
    try:
        font = ImageFont.truetype("arial.ttf", FONT_SIZE)
    except:
        font = ImageFont.load_default()
    
    try:
        hand_font = ImageFont.truetype(FONT_PATH, HAND_FONT_SIZE)
    except:
        hand_font = font
    
    return font, hand_font

def build_display():
    """Build the main display image based on current state."""
    
    # Priority 1: Spotify view
    spotify_img = draw_spotify_screen(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255)))
    if spotify_img is not None:
        logging.info("Showing Spotify screen")
        return spotify_img

    # Priority 2: Cooldown view
    cooldown_mode = should_show_cooldown()
    if cooldown_mode:
        logging.info("Showing cooldown screen")
        image = load_cooldown_image(cooldown_mode)
        return image if image else None

    # Priority 3: Main dashboard
    logging.debug("Building main dashboard")
    image = load_background()
    font, hand_font = load_fonts()
    draw = ImageDraw.Draw(image)

    # Get weather data
    weather_data = get_weather(full_forecast=True)

    # Draw weather section
    draw_weather(draw, image, WIDTH // 2 - 210, 20, weather_data)

    # Apply no-sky overlay
    try:
        no_sky_overlay = Image.open("assets/backgrounds/no_sky.png").convert("RGBA")
        image.paste(no_sky_overlay, (0, 0), no_sky_overlay)
    except Exception:
        logging.warning("Could not load no_sky overlay")

    # Draw appliances
    initialize_state_if_missing()
    appliances = reset_state_if_empty()
    draw_appliances_and_layers(image, appliances)

    # Draw calendar
    draw_calendar_text(draw, hand_font, start_x=50, start_y=680, max_width=475)

    # Apply foreground layer
    sign_2_img = get_layer_image("sign_2")
    if sign_2_img:
        image.paste(sign_2_img, (0, 0), sign_2_img)

    # Draw Daniel's note
    draw_daniel_note(image, hand_font, x=130, y=333)

    # Draw rain gauge
    if "raw" in weather_data:
        try:
            draw_rain_gauge(image, weather_data["raw"])
        except Exception:
            logging.warning("Could not draw rain gauge")

    return image
