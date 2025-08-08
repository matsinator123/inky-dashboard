import time
import threading
import os
from PIL import Image, ImageChops
import logging

from layout import build_display
from modules.inky_loader import get_auto
from modules.button_handler import setup_buttons, listen_for_presses
from modules.state_handler import initialize_state_if_missing

# Config
DISPLAY_UPDATE_INTERVAL = 5
SIMULATED_OUTPUT_PATH = "simulated_output.png"

# Logging setup
logging.basicConfig(level=os.getenv("INKY_LOG_LEVEL", "INFO"), format="%(asctime)s [%(levelname)s] %(message)s")

# Inky display
inky_display = get_auto()()

def images_are_different(new_image, comparison_path=SIMULATED_OUTPUT_PATH):
    if not os.path.exists(comparison_path): return True
    try:
        previous_image = Image.open(comparison_path)
        diff = ImageChops.difference(new_image.convert("RGB"), previous_image.convert("RGB"))
        return diff.getbbox() is not None
    except Exception: return True

def start_button_listener():
    setup_buttons()
    listen_for_presses()

def main():
    logging.info("Starting dashboard...")
    initialize_state_if_missing()
    threading.Thread(target=start_button_listener, daemon=True).start()
    logging.info("Listeners started...")

    try:
        while True:
            image = build_display()
            if image and images_are_different(image):
                inky_display.set_image(image)
                inky_display.show()
                image.save(SIMULATED_OUTPUT_PATH)
                logging.info("Display updated")
            else:
                logging.debug("No visual change")
            time.sleep(DISPLAY_UPDATE_INTERVAL)
    except KeyboardInterrupt: logging.info("Dashboard stopped")
    except Exception as e: logging.exception("Dashboard crashed")

if __name__ == "__main__":
    main()
