"""
Initialize appliance state to default values (all appliances at level 3).
Run this script to reset the appliance state.
"""

from datetime import datetime, timedelta
from modules.state_handler import save_state

# Initial appliance state: all appliances set to level 3 ("a little unclean")
INITIAL_STATE = {
    "washing_machine": {
        "last_run": datetime.now() - timedelta(days=2),
        "is_running": False
    },
    "vacuum": {
        "last_run": datetime.now() - timedelta(days=2),
        "is_running": False
    },
    "dryer": {
        "last_run": datetime.now() - timedelta(days=2),
        "is_running": False
    },
    "dishwasher": {
        "last_run": datetime.now() - timedelta(days=2),
        "is_running": False
    }
}

if __name__ == "__main__":
    save_state(INITIAL_STATE)
