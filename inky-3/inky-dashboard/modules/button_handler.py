"""
Physical button handler for the Inky dashboard.
Handles 4 buttons with different actions based on current mode (default/spotify).
"""

import gpiod
import gpiodevice
from gpiod.line import Bias, Direction, Edge
import time
import logging
from modules.state_handler import mark_appliance_run, load_state
from modules.spotify_connect import get_spotify_client

# GPIO configuration
BUTTONS = [5, 6, 25, 24]  # BCM GPIO numbers
LABELS = ["A", "B", "C", "D"]
VOLUME_STEP = 10
DEBOUNCE_DELAY = 0.1

# Button actions per mode
BUTTON_ACTIONS = {
    "default": {
        "A": "washing_machine",
        "B": "dryer", 
        "C": "dishwasher",
        "D": "vacuum",
    },
    "spotify": {
        "A": "volume_up",
        "B": "volume_down",
        "C": "next_track",
        "D": "previous_track"
    }
}

# GPIO setup for Pi 5
INPUT = gpiod.LineSettings(direction=Direction.INPUT, bias=Bias.PULL_UP, edge_detection=Edge.FALLING)
chip = gpiodevice.find_chip_by_platform()
OFFSETS = [chip.line_offset_from_id(id) for id in BUTTONS]
line_config = dict.fromkeys(OFFSETS, INPUT)
request = chip.request_lines(consumer="inky-dashboard-buttons", config=line_config)

def is_spotify_mode():
    """Check if Spotify is actively playing music."""
    try:
        sp = get_spotify_client()
        playback = sp.current_playback()
        return playback is not None and playback.get("is_playing", False)
    except Exception:
        return False

def change_volume(delta):
    """Change Spotify volume by delta amount."""
    try:
        sp = get_spotify_client()
        playback = sp.current_playback()
        current_volume = playback.get("device", {}).get("volume_percent")
        if current_volume is None:
            return
        new_volume = max(0, min(100, current_volume + delta))
        sp.volume(new_volume)
        logging.info(f"Volume: {current_volume}% -> {new_volume}%")
    except Exception as e:
        logging.error(f"Volume change failed: {e}")

def handle_button_press(label):
    """Handle button press based on current mode."""
    mode = "spotify" if is_spotify_mode() else "default"
    action = BUTTON_ACTIONS[mode].get(label)
    
    if mode == "default":
        try:
            mark_appliance_run(load_state(), action)
            logging.info(f"Marked {action} as run")
        except Exception as e:
            logging.error(f"Failed to mark appliance '{action}': {e}")
    
    elif mode == "spotify":
        try:
            sp = get_spotify_client()
            
            if action == "volume_up":
                change_volume(VOLUME_STEP)
            elif action == "volume_down":
                change_volume(-VOLUME_STEP)
            elif action == "next_track":
                sp.next_track()
                logging.info("Next track")
            elif action == "previous_track":
                sp.previous_track()
                logging.info("Previous track")
        except Exception as e:
            logging.error(f"Spotify action '{action}' failed: {e}")

def handle_button(event):
    """Handle button press events from gpiod."""
    index = OFFSETS.index(event.line_offset)
    label = LABELS[index]
    logging.info(f"Button {label} pressed")
    handle_button_press(label)

def setup_buttons():
    """GPIO setup is handled at module level."""
    logging.info("Button handler ready")

def listen_for_presses():
    """Main button listening loop."""
    logging.info("Listening for button presses...")
    try:
        while True:
            for event in request.read_edge_events():
                handle_button(event)
                time.sleep(DEBOUNCE_DELAY)
            time.sleep(0.01)
    except KeyboardInterrupt:
        logging.info("Button listener stopped")
    except Exception as e:
        logging.error(f"Button listener failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    setup_buttons()
    listen_for_presses()
