"""
Inky display loader with mock fallback.
Attempts to load the real Inky library, falls back to mock for development.
"""

import importlib.util
import importlib

def get_auto():
    """Get the Inky auto display function, with mock fallback for development."""
    if importlib.util.find_spec("inky") is not None:
        try:
            inky_auto = importlib.import_module("inky.auto")
            return inky_auto.auto
        except Exception:
            pass

    # Fallback to mock display
    from modules.inky_mock import auto
    return auto
