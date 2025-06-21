"""
Appliance state management for the dashboard.
Handles loading, saving, and updating appliance run states and timers.
"""

import json
from datetime import datetime, timedelta
import os

STATE_FILE = "state.json"

# Default appliance run durations
RUN_DURATIONS = {
    "washing_machine": timedelta(minutes=57),
    "vacuum": timedelta(hours=2),
    "dryer": timedelta(hours=1, minutes=46),
    "dishwasher": timedelta(hours=2),
}

def initialize_state_if_missing():
    """Create default state file if it doesn't exist."""
    if not os.path.exists(STATE_FILE):
        now = datetime.now()
        default_state = {
            "washing_machine": {"last_run": now - timedelta(hours=3), "is_running": False},
            "vacuum": {"last_run": now - timedelta(hours=3), "is_running": False},
            "dryer": {"last_run": now - timedelta(hours=3), "is_running": False},
            "dishwasher": {"last_run": now - timedelta(hours=3), "is_running": False},
        }
        save_state(default_state)

def load_state():
    """Load appliance state from JSON file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                raw = json.load(f)
                for appliance in raw.values():
                    appliance["last_run"] = datetime.fromisoformat(appliance["last_run"])
                return raw
        except Exception:
            pass
    return {}

def save_state(state):
    """Save appliance state to JSON file."""
    try:
        with open(STATE_FILE, "w") as f:
            serializable = {
                name: {"last_run": data["last_run"].isoformat(), "is_running": data["is_running"]}
                for name, data in state.items()
            }
            json.dump(serializable, f, indent=2)
    except Exception:
        pass

def mark_appliance_run(state, name):
    """Mark an appliance as started running."""
    state[name] = {
        "last_run": datetime.now(),
        "is_running": True
    }
    save_state(state)

def update_running_status(state):
    """Update running status based on elapsed time since start."""
    now = datetime.now()
    for name, data in state.items():
        if data.get("is_running"):
            started = data["last_run"]
            duration = RUN_DURATIONS.get(name, timedelta(minutes=60))
            if now - started >= duration:
                data["is_running"] = False
    save_state(state)

def get_appliance_state():
    """Get current appliance state with updated running status."""
    state = load_state()
    update_running_status(state)
    return [
        {"prefix": name, "last_run": data["last_run"], "is_running": data["is_running"]}
        for name, data in state.items()
    ]

__all__ = [
    "get_appliance_state",
    "mark_appliance_run", 
    "load_state",
    "save_state",
    "initialize_state_if_missing"
]
