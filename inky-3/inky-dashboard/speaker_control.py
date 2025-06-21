#!/usr/bin/env python3
"""
Bluetooth Speaker Media Key Controller

Listens for media key presses from a Bluetooth speaker and controls Spotify playback.
Requires the speaker to be paired and connected to the Pi.
"""

import evdev
from evdev import InputDevice, categorize, ecodes
import sys
import os
import logging

# Add project directory to path
sys.path.append('/home/pi/inky-dashboard')
from modules.spotify_connect import get_spotify_client

# Configuration
SPEAKER_NAME = "VAPPEBY"
VOLUME_STEP = 10

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def find_speaker_device():
    """Find the Bluetooth speaker device by name."""
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    
    for device in devices:
        logging.debug(f"Found device: {device.path} - {device.name}")
        if SPEAKER_NAME.lower() in device.name.lower():
            logging.info(f"Using device: {device.path} ({device.name})")
            return device
    
    raise Exception(f"Could not find device containing '{SPEAKER_NAME}'")

def handle_media_key(keycode):
    """Handle media key press and control Spotify."""
    try:
        sp = get_spotify_client()
        
        if keycode in ['KEY_PLAYCD', 'KEY_PAUSECD']:
            playback = sp.current_playback()
            if playback and playback.get("is_playing"):
                sp.pause_playback()
                logging.info("Paused")
            else:
                sp.start_playback()
                logging.info("Playing")
        
        elif keycode == 'KEY_NEXTSONG':
            sp.next_track()
            logging.info("Next track")
        
        elif keycode == 'KEY_PREVIOUSSONG':
            sp.previous_track()
            logging.info("Previous track")
        
        elif keycode == 'KEY_VOLUMEUP':
            playback = sp.current_playback()
            if playback:
                volume = playback.get("device", {}).get("volume_percent", 50)
                new_volume = min(100, volume + VOLUME_STEP)
                sp.volume(new_volume)
                logging.info(f"Volume: {volume}% -> {new_volume}%")
        
        elif keycode == 'KEY_VOLUMEDOWN':
            playback = sp.current_playback()
            if playback:
                volume = playback.get("device", {}).get("volume_percent", 50)
                new_volume = max(0, volume - VOLUME_STEP)
                sp.volume(new_volume)
                logging.info(f"Volume: {volume}% -> {new_volume}%")
    
    except Exception as e:
        logging.error(f"Spotify control failed: {e}")

def main():
    """Main media key listener loop."""
    try:
        device = find_speaker_device()
        logging.info(f"Listening for media keys on {device.name}")
        
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                
                # Only respond to key press (not release)
                if getattr(key_event, 'keystate', None) == 1:
                    keycode = getattr(key_event, 'keycode', None)
                    if keycode:
                        logging.debug(f"Key pressed: {keycode}")
                        handle_media_key(keycode)
    
    except KeyboardInterrupt:
        logging.info("Stopped by user")
    except Exception as e:
        logging.error(f"Device access failed: {e}")

if __name__ == "__main__":
    main()
