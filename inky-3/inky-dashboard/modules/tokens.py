"""
Enhanced token management for external API authentication.
Handles loading and saving of authentication tokens with proper error handling.
"""

import json
import pickle
from pathlib import Path
from datetime import datetime

# Define the auth directory
AUTH_DIR = Path(__file__).parent / "auth"
AUTH_DIR.mkdir(exist_ok=True)

# Token file paths
GOOGLE_TOKEN_JSON = AUTH_DIR / "google_token.json"
GOOGLE_CREDENTIALS = AUTH_DIR / "google_credentials.json"
SPOTIFY_CREDENTIALS = AUTH_DIR / "spotify_credentials.json"
SPOTIFY_CACHE = AUTH_DIR / ".spotify_cache"

def load_google_token():
    """Load Google token from JSON file."""
    if GOOGLE_TOKEN_JSON.exists():
        try:
            with open(GOOGLE_TOKEN_JSON, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load Google token: {e}")
    return None

def save_google_token(token_data):
    """Save Google token to JSON file."""
    try:
        with open(GOOGLE_TOKEN_JSON, 'w') as f:
            json.dump(token_data, f, indent=2)
        print("[INFO] Google token saved successfully")
    except Exception as e:
        print(f"[ERROR] Failed to save Google token: {e}")

def google_token_exists():
    """Check if Google token exists and is valid."""
    if not GOOGLE_TOKEN_JSON.exists():
        return False
    
    try:
        token_data = load_google_token()
        if not token_data:
            return False
        
        # Check if token has expiry info
        if 'expiry' in token_data:
            expiry = datetime.fromisoformat(token_data['expiry'].replace('Z', '+00:00'))
            if expiry <= datetime.now(expiry.tzinfo):
                print("[INFO] Google token expired")
                return False
        
        return True
    except Exception:
        return False

def load_spotify_credentials():
    """Load Spotify credentials from JSON file."""
    if SPOTIFY_CREDENTIALS.exists():
        try:
            with open(SPOTIFY_CREDENTIALS, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load Spotify credentials: {e}")
    return None

def spotify_cache_exists():
    """Check if Spotify cache exists."""
    return SPOTIFY_CACHE.exists()

def clear_all_tokens():
    """Clear all stored tokens (useful for debugging)."""
    files_to_clear = [GOOGLE_TOKEN_JSON, SPOTIFY_CACHE]
    
    for file_path in files_to_clear:
        try:
            if file_path.exists():
                file_path.unlink()
                print(f"[INFO] Cleared {file_path.name}")
        except Exception as e:
            print(f"[ERROR] Failed to clear {file_path.name}: {e}")

def get_auth_status():
    """Get authentication status for all services."""
    return {
        "google": {
            "credentials_exist": GOOGLE_CREDENTIALS.exists(),
            "token_exists": google_token_exists(),
        },
        "spotify": {
            "credentials_exist": SPOTIFY_CREDENTIALS.exists(),
            "cache_exists": spotify_cache_exists(),
        }
    }

__all__ = [
    "load_google_token",
    "save_google_token", 
    "google_token_exists",
    "load_spotify_credentials",
    "spotify_cache_exists",
    "clear_all_tokens",
    "get_auth_status"
]
