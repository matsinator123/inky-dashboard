"""
Token management for external API authentication.
Handles loading and saving of authentication tokens in the auth/ directory.
"""

import pickle
from pathlib import Path

# Define the auth directory
AUTH_DIR = Path(__file__).parent / "auth"
AUTH_DIR.mkdir(exist_ok=True)

# Token file paths
GOOGLE_CALENDAR_TOKEN = AUTH_DIR / "google_calendar_token.pickle"

def load_google_calendar_token():
    """Load Google Calendar token if it exists."""
    if GOOGLE_CALENDAR_TOKEN.exists():
        try:
            with open(GOOGLE_CALENDAR_TOKEN, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass
    return None

def save_google_calendar_token(creds):
    """Save Google Calendar token."""
    try:
        with open(GOOGLE_CALENDAR_TOKEN, 'wb') as f:
            pickle.dump(creds, f)
    except Exception:
        pass

def google_calendar_token_exists():
    """Check if Google Calendar token exists."""
    return GOOGLE_CALENDAR_TOKEN.exists()

__all__ = [
    "load_google_calendar_token",
    "save_google_calendar_token", 
    "google_calendar_token_exists"
]
