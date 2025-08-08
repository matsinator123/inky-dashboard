from flask import Flask, redirect, request, url_for, render_template_string
import logging
from pathlib import Path

# Spotify
from spotipy.oauth2 import SpotifyOAuth
import json

# Google
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Project paths
BASE_DIR = Path(__file__).parent
AUTH_DIR = BASE_DIR / "auth"
AUTH_DIR.mkdir(exist_ok=True)

# Spotify configuration
SPOTIFY_CREDENTIALS_PATH = AUTH_DIR / "spotify_credentials.json"
SPOTIFY_CACHE_PATH = AUTH_DIR / ".spotify_cache"

# Google configuration
GOOGLE_CREDENTIALS_PATH = AUTH_DIR / "google_credentials.json"
GOOGLE_TOKEN_PATH = AUTH_DIR / "google_token.json"
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

app = Flask(__name__)
app.secret_key = b"inky-dashboard-auth-secret"

INDEX_HTML = """
<!doctype html>
<title>Inky Dashboard Auth</title>
<h1>Inky Dashboard Authentication</h1>
<p>Use these links from your phone to (re)authenticate services on the Pi.</p>
<ul>
  <li><a href="/spotify/start">Spotify: Start authentication</a></li>
  <li><a href="/google/start">Google Calendar: Start authentication</a></li>
  <li><a href="/status">Status</a></li>
  <li><a href="/help">Help</a></li>
  
</ul>
"""


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/status")
def status():
    spotify_ok = SPOTIFY_CACHE_PATH.exists()
    google_ok = GOOGLE_TOKEN_PATH.exists()
    return (
        f"Spotify token: {'OK' if spotify_ok else 'Missing'}<br>"
        f"Google token: {'OK' if google_ok else 'Missing'}"
    )


@app.route("/help")
def help_page():
    return (
        "<p>1) Tap Spotify or Google link to sign in.\n"
        "<br>2) Approve access.\n"
        "<br>3) Return to Status page to verify tokens are saved.</p>"
    )


# ---------- Spotify OAuth ----------

def _load_spotify_credentials():
    if not SPOTIFY_CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"Spotify credentials missing at {SPOTIFY_CREDENTIALS_PATH}."
        )
    with open(SPOTIFY_CREDENTIALS_PATH, "r") as f:
        return json.load(f)


def _create_spotify_oauth():
    creds = _load_spotify_credentials()
    return SpotifyOAuth(
        client_id=creds["CLIENT_ID"],
        client_secret=creds["CLIENT_SECRET"],
        redirect_uri=creds["REDIRECT_URI"],
        scope=creds["SCOPE"],
        cache_path=str(SPOTIFY_CACHE_PATH),
        open_browser=False,
        show_dialog=False,
    )


@app.route("/spotify/start")
def spotify_start():
    try:
        oauth = _create_spotify_oauth()
        url = oauth.get_authorize_url()
        return redirect(url)
    except Exception as e:
        logging.exception("Spotify auth start failed")
        return f"Spotify auth start failed: {e}", 500


@app.route("/spotify/callback")
def spotify_callback():
    try:
        oauth = _create_spotify_oauth()
        code = oauth.parse_response_code(request.url)
        if not code:
            return "Missing authorization code", 400
        token_info = oauth.get_access_token(code)
        if token_info:
            return "Spotify authentication successful! You can close this page.", 200
        return "Spotify authentication failed.", 500
    except Exception as e:
        logging.exception("Spotify auth callback failed")
        return f"Spotify auth callback failed: {e}", 500


# ---------- Google OAuth ----------

def _create_google_flow():
    if not GOOGLE_CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"Google credentials missing at {GOOGLE_CREDENTIALS_PATH}."
        )
    # Redirect URI must match the one set in Google Cloud Console
    # Suggest: http://<pi-ip>:5100/google/callback
    with open(GOOGLE_CREDENTIALS_PATH, "r") as f:
        client_info = json.load(f)

    # Extract redirect URI from installed app config if present, else fallback
    redirect_uri = None
    try:
        redirect_uri = client_info["installed"]["redirect_uris"][0]
    except Exception:
        # Fallback to common local server path; ensure it matches your console setup
        redirect_uri = "http://localhost:5100/google/callback"

    flow = Flow.from_client_secrets_file(
        str(GOOGLE_CREDENTIALS_PATH), scopes=GOOGLE_SCOPES, redirect_uri=redirect_uri
    )
    return flow


@app.route("/google/start")
def google_start():
    try:
        flow = _create_google_flow()
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        # Persist state in a simple file for callback validation
        (AUTH_DIR / "google_oauth_state.txt").write_text(state)
        return redirect(auth_url)
    except Exception as e:
        logging.exception("Google auth start failed")
        return f"Google auth start failed: {e}", 500


@app.route("/google/callback")
def google_callback():
    try:
        saved_state = (AUTH_DIR / "google_oauth_state.txt").read_text().strip()
        flow = _create_google_flow()
        flow.fetch_token(authorization_response=request.url)
        creds: Credentials = flow.credentials

        # Save token for the main app to use
        GOOGLE_TOKEN_PATH.write_text(creds.to_json())
        return "Google authentication successful! You can close this page.", 200
    except Exception as e:
        logging.exception("Google auth callback failed")
        return f"Google auth callback failed: {e}", 500


if __name__ == "__main__":
    logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
    app.run(host="0.0.0.0", port=5100)


