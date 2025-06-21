"""
Flask web endpoint for triggering display refreshes.
Provides a simple HTTP endpoint to force a display update.
"""

from flask import Flask
from layout import build_display
from modules.inky_loader import get_auto
import logging

app = Flask(__name__)
display = get_auto()()

@app.route("/refresh", methods=["POST"])
def refresh():
    """Force a display refresh via HTTP POST."""
    image = build_display()
    if image:
        image.save("simulated_output.png")
        display.set_image(image)
        display.show()
        logging.info("Display refresh triggered")
        return "OK", 200
    else:
        logging.error("Failed to build display image")
        return "Error", 500

def run_flask():
    """Start the Flask server."""
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logging.info("Starting display refresh server on port 5050")
    run_flask()
