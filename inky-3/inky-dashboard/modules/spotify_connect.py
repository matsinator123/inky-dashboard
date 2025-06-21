"""
Spotify API client and track information handler.
Manages authentication and provides current track data.
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json
import logging

def load_spotify_credentials():
    """Load Spotify credentials from JSON file."""
    try:
        credentials_path = os.path.join(os.path.dirname(__file__), '..', 'auth', 'spotify_credentials.json')
        with open(credentials_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

# Load credentials
credentials = load_spotify_credentials()
if not credentials:
    raise Exception("Failed to load Spotify credentials")

CLIENT_ID = credentials["CLIENT_ID"]
CLIENT_SECRET = credentials["CLIENT_SECRET"]
REDIRECT_URI = credentials["REDIRECT_URI"]
USERNAME = credentials["USERNAME"]
SCOPE = credentials["SCOPE"]

_spotify_client = None
JAM_PATH = "jam_url.txt"

def get_spotify_client():
    """Get authenticated Spotify client (singleton)."""
    global _spotify_client
    if _spotify_client is None:
        auth_manager = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            username=USERNAME,
            cache_path=".spotify_cache",
            open_browser=False
        )
        _spotify_client = spotipy.Spotify(auth_manager=auth_manager)
    return _spotify_client

def get_current_track():
    """Get currently playing track information."""
    try:
        sp = get_spotify_client()
        playback = sp.current_playback()
        if not playback or not playback.get("is_playing"):
            return None
        item = playback.get("item")
        if not item:
            return None
        return {
            "id": item["id"],
            "title": item["name"],
            "artist": ", ".join([a["name"] for a in item["artists"]]),
            "album": item["album"]["name"],
            "art_url": item["album"]["images"][0]["url"] if item["album"]["images"] else None,
            "is_playing": playback.get("is_playing", False)
        }
    except Exception:
        return None

def get_jam_url():
    """Get the current Spotify Jam URL if available."""
    try:
        if os.path.exists(JAM_PATH):
            with open(JAM_PATH, "r") as f:
                return f.read().strip() or None
    except Exception:
        pass
    return None

def clear_jam_url():
    """Clear the stored Jam URL."""
    try:
        open(JAM_PATH, "w").close()
        logging.info("Jam URL cleared")
    except Exception:
        pass

if __name__ == "__main__":
    track = get_current_track()
    if track:
        print(f"🎵 {track['title']} - {track['artist']} ({track['album']})")
        print(f"🖼  Album art: {track['art_url']}")
        print(f"  Jam: {get_jam_url()}")
    else:
        print("No song is currently playing.")
