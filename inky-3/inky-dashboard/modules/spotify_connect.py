"""
Improved Spotify API client with proper token management.
Handles automatic token refresh and secure credential storage.
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

class SpotifyClient:
    def __init__(self):
        self.auth_dir = Path(__file__).parent.parent / "auth"
        self.auth_dir.mkdir(exist_ok=True)
        
        self.credentials_path = self.auth_dir / "spotify_credentials.json"
        self.cache_path = self.auth_dir / ".spotify_cache"
        
        self._client = None
        self._auth_manager = None
        self._credentials = None
        
        self._load_credentials()
    
    def _load_credentials(self):
        """Load Spotify credentials from JSON file."""
        try:
            with open(self.credentials_path, 'r') as f:
                self._credentials = json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[ERROR] Failed to load Spotify credentials: {e}")
            return False
    
    def _create_auth_manager(self):
        """Create Spotify OAuth manager with proper settings."""
        if not self._credentials:
            raise Exception("Spotify credentials not loaded")
        
        self._auth_manager = SpotifyOAuth(
            client_id=self._credentials["CLIENT_ID"],
            client_secret=self._credentials["CLIENT_SECRET"],
            redirect_uri=self._credentials["REDIRECT_URI"],
            scope=self._credentials["SCOPE"],
            cache_path=str(self.cache_path),
            open_browser=False,
            show_dialog=False  # Don't show auth dialog every time
        )
        return self._auth_manager
    
    def _ensure_authenticated(self):
        """Ensure we have a valid Spotify client."""
        if not self._auth_manager:
            self._create_auth_manager()
        
        # Check if we have a valid token
        token_info = self._auth_manager.get_cached_token()
        
        if not token_info:
            print("[INFO] No cached Spotify token found, need to authenticate")
            return False
        
        # Check if token is expired
        if self._auth_manager.is_token_expired(token_info):
            print("[INFO] Spotify token expired, refreshing...")
            try:
                token_info = self._auth_manager.refresh_access_token(
                    token_info['refresh_token']
                )
                print("[INFO] Spotify token refreshed successfully")
            except Exception as e:
                print(f"[ERROR] Failed to refresh Spotify token: {e}")
                return False
        
        return True
    
    def get_client(self):
        """Get authenticated Spotify client."""
        if not self._client:
            if not self._ensure_authenticated():
                raise Exception(
                    "Spotify authentication required. Please run the initial setup."
                )
            
            self._client = spotipy.Spotify(auth_manager=self._auth_manager)
        
        return self._client
    
    def authenticate_initial(self):
        """Perform initial authentication (run this once manually)."""
        if not self._credentials:
            raise Exception("Spotify credentials not loaded")
        
        auth_manager = self._create_auth_manager()
        
        # Get authorization URL
        auth_url = auth_manager.get_authorize_url()
        print(f"Please visit this URL to authorize the application: {auth_url}")
        
        # Get the authorization code from user
        response = input("Enter the URL you were redirected to: ")
        
        # Extract code and get token
        code = auth_manager.parse_response_code(response)
        token_info = auth_manager.get_access_token(code)
        
        if token_info:
            print("[INFO] Spotify authentication successful!")
            self._client = spotipy.Spotify(auth_manager=auth_manager)
            return True
        else:
            print("[ERROR] Spotify authentication failed")
            return False
    
    def get_current_track(self):
        """Get currently playing track information with error handling."""
        try:
            client = self.get_client()
            playback = client.current_playback()
            
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
                "is_playing": playback.get("is_playing", False),
                "progress_ms": playback.get("progress_ms", 0),
                "duration_ms": item.get("duration_ms", 0)
            }
            
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 401:
                print("[WARNING] Spotify token expired, attempting refresh...")
                self._client = None  # Force re-authentication
                return self.get_current_track()  # Retry once
            else:
                print(f"[ERROR] Spotify API error: {e}")
                return None
        except Exception as e:
            print(f"[ERROR] Failed to get current track: {e}")
            return None

# Global client instance
_spotify_client = None

def get_spotify_client():
    """Get singleton Spotify client."""
    global _spotify_client
    if _spotify_client is None:
        _spotify_client = SpotifyClient()
    return _spotify_client

def get_current_track():
    """Get currently playing track (backward compatibility)."""
    return get_spotify_client().get_current_track()

# Jam URL handling (keeping your existing functionality)
JAM_PATH = Path(__file__).parent.parent / "jam_url.txt"

def get_jam_url():
    """Get the current Spotify Jam URL if available."""
    try:
        if JAM_PATH.exists():
            with open(JAM_PATH, "r") as f:
                return f.read().strip() or None
    except Exception:
        pass
    return None

def clear_jam_url():
    """Clear the stored Jam URL."""
    try:
        JAM_PATH.write_text("")
        logging.info("Jam URL cleared")
    except Exception:
        pass

def set_jam_url(url):
    """Set the Spotify Jam URL."""
    try:
        JAM_PATH.write_text(url)
        logging.info(f"Jam URL set: {url}")
    except Exception as e:
        logging.error(f"Failed to set Jam URL: {e}")

__all__ = [
    "get_current_track", 
    "get_jam_url", 
    "clear_jam_url", 
    "set_jam_url",
    "get_spotify_client"
]
