from PIL import Image, ImageDraw, ImageFilter, ImageFont
import requests
import qrcode
from io import BytesIO
from modules.spotify_connect import get_current_track, get_jam_url, clear_jam_url
import os
from datetime import datetime
import socket
import logging

# Simple in-process cache for album art to reduce network calls while the same track plays
_ALBUM_ART_CACHE = {
    "track_id": None,
    "image": None,
}

def get_local_ip():
    """Returns the local IP address of the Pi."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def draw_spotify_screen(base_image: Image.Image):
    logging.debug("Starting Spotify view rendering")
    base_image = Image.new("RGB", (1600, 1200), (50, 50, 50))

    track = get_current_track()

    if not track:
        logging.debug("No active song. Falling back to normal dashboard view.")
        clear_jam_url()
        return None  # Viktig: la layout.py håndtere fallback

    # Fetch or reuse album art with caching per track id
    album_art = None
    try:
        if _ALBUM_ART_CACHE["track_id"] == track.get("id") and _ALBUM_ART_CACHE["image"] is not None:
            album_art = _ALBUM_ART_CACHE["image"]
            logging.debug("Reusing cached album art for current track")
        else:
            response = requests.get(track["art_url"], timeout=5)
            response.raise_for_status()
            album_art = Image.open(BytesIO(response.content)).convert("RGB")
            _ALBUM_ART_CACHE["track_id"] = track.get("id")
            _ALBUM_ART_CACHE["image"] = album_art
            logging.debug("Downloaded album art from Spotify")
    except Exception as e:
        logging.error(f"Album art download failed, using fallback: {e}")
        album_art = Image.open("assets/fallback_art.jpg").convert("RGB")

    try:
        blurred = album_art.resize((1600, 1200)).filter(ImageFilter.GaussianBlur(radius=30))
        base_image.paste(blurred, (0, 0))
        logging.debug("Applied blurred album art background")
    except Exception as e:
        logging.error(f"Background blur failed: {e}")

    try:
        art_w, art_h = album_art.size
        target_h = 1000
        scale = target_h / art_h
        target_w = int(art_w * scale)
        art = album_art.resize((target_w, target_h))
        x = (1600 - target_w) // 2
        y = (1200 - target_h) // 2
        base_image.paste(art, (x, y))
        logging.debug("Pasted centered album art without distortion")
    except Exception as e:
        logging.error(f"Album art placement failed: {e}")

    jam_url = get_jam_url()
    if jam_url:
        try:
            qr = qrcode.make(jam_url).convert("RGB").resize((200, 200))
            base_image.paste(qr, (1380, 20))
            logging.debug("Added QR code for Jam link in top-right corner")
        except Exception as e:
            logging.error(f"QR code render failed: {e}")
    else:
        pi_ip = get_local_ip()
        # No timeout for QR availability as requested; page is always available for manual Jam URL entry
        jam_entry_url = f"http://{pi_ip}:5000/"
        try:
            qr = qrcode.make(jam_entry_url).convert("RGB").resize((200, 200))
            base_image.paste(qr, (1380, 20))
            logging.debug(f"Added QR for Jam entry page {jam_entry_url} in top-right corner")
        except Exception as e:
            logging.error(f"QR code for Jam entry page failed: {e}")

    return base_image
