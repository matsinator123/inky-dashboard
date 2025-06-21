from PIL import Image, ImageDraw, ImageFilter, ImageFont
import requests
import qrcode
from io import BytesIO
from modules.spotify_connect import get_current_track, get_jam_url, clear_jam_url
import os
from datetime import datetime
import socket

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
    print("[DEBUG] Starter Spotify-visning")
    base_image = Image.new("RGB", (1600, 1200), (50, 50, 50))

    track = get_current_track()

    if not track:
        print("[DEBUG] Ingen aktiv sang. Går tilbake til normal visning.")
        clear_jam_url()
        return None  # Viktig: la layout.py håndtere fallback

    try:
        response = requests.get(track["art_url"])
        album_art = Image.open(BytesIO(response.content)).convert("RGB")
        print("[DEBUG] Album art lastet fra Spotify")
    except Exception as e:
        print("[ERROR] Bruker fallback:", e)
        album_art = Image.open("assets/fallback_art.jpg").convert("RGB")

    try:
        blurred = album_art.resize((1600, 1200)).filter(ImageFilter.GaussianBlur(radius=30))
        base_image.paste(blurred, (0, 0))
        print("[DEBUG] Blurry bakgrunn limt inn")
    except Exception as e:
        print("[ERROR] Blur feilet:", e)

    try:
        art_w, art_h = album_art.size
        target_h = 1000
        scale = target_h / art_h
        target_w = int(art_w * scale)
        art = album_art.resize((target_w, target_h))
        x = (1600 - target_w) // 2
        y = (1200 - target_h) // 2
        base_image.paste(art, (x, y))
        print("[DEBUG] Albumart limt inn uten forvrengning")
    except Exception as e:
        print("[ERROR] Albumart plassering feilet:", e)

    jam_url = get_jam_url()
    if jam_url:
        try:
            qr = qrcode.make(jam_url).convert("RGB").resize((200, 200))
            base_image.paste(qr, (1380, 20))
            print("[DEBUG] La til QR-kode for Jam-link i høyre hjørne")
        except Exception as e:
            print("[ERROR] QR-kode feilet:", e)
    else:
        pi_ip = get_local_ip()
        jam_entry_url = f"http://{pi_ip}:5000/"
        try:
            qr = qrcode.make(jam_entry_url).convert("RGB").resize((200, 200))
            base_image.paste(qr, (1380, 20))
            print(f"[DEBUG] La til QR-kode for Jam-innskrivingsside ({jam_entry_url}) i høyre hjørne")
        except Exception as e:
            print("[ERROR] QR-kode for Jam-innskrivingsside feilet:", e)

    return base_image
