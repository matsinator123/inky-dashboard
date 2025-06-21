from datetime import datetime, timedelta
from PIL import Image
import os
from modules.state_handler import get_appliance_state as state_handler_get

# Order in which appliance layers are drawn
APPLIANCE_LAYER_ORDER = [
    "washing_machine", "vacuum", "sean_building_1", "sean_building_2",
    "dryer", "sean_building_3", "sign", "dishwasher", "sean_building_4"
]

# How long each appliance stays in "running" mode
APPLIANCE_RUNNING_TIMERS = {
    "washing_machine": timedelta(minutes=57),
    "vacuum": timedelta(hours=2),
    "dryer": timedelta(hours=1, minutes=46),
    "dishwasher": timedelta(hours=2),
}

def get_status_image_name(last_run: datetime, is_running: bool, prefix: str) -> str:
    """Return the correct image name for an appliance based on last run and running state."""
    now = datetime.now()
    elapsed = now - last_run

    if is_running:
        run_time = APPLIANCE_RUNNING_TIMERS.get(prefix, timedelta(hours=1))
        return f"{prefix}_2" if elapsed < run_time else f"{prefix}_1"

    if elapsed.days >= 7:
        return f"{prefix}_5"
    elif elapsed.days >= 3:
        return f"{prefix}_4"
    elif elapsed.days >= 1:
        return f"{prefix}_3"
    else:
        return f"{prefix}_1"

def get_layer_image(name: str):
    """Load a PNG layer image by name from the appliances folder."""
    path = os.path.join("assets", "appliances", f"{name}.png")
    try:
        return Image.open(path).convert("RGBA")
    except Exception:
        return None

def get_appliance_state():
    """Get the current appliance state from the state handler."""
    return state_handler_get()

def draw_appliances_and_layers(image: Image.Image, appliance_data: list[dict]) -> None:
    """Draw all appliance and building layers onto the given image."""
    for name in APPLIANCE_LAYER_ORDER:
        img = None
        if name.startswith("sean_building") or name == "sign":
            img = get_layer_image(name)
        else:
            appliance = next((a for a in appliance_data if a["prefix"] == name), None)
            if appliance:
                image_name = get_status_image_name(appliance["last_run"], appliance["is_running"], name)
                img = get_layer_image(image_name)
        if img:
            image.paste(img, (0, 0), img)

__all__ = [
    "draw_appliances_and_layers",
    "get_layer_image",
    "get_appliance_state"
]
