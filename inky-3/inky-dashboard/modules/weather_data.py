"""
Weather data fetcher using MET Norway API.
Provides current weather conditions and temperature forecasts.
"""

import requests
from datetime import datetime
import os

# Coordinates for Kristiansand (change if needed)
LAT, LON = 58.1624, 7.9983

# User-Agent as required by MET Norway's terms
HEADERS = {
    "User-Agent": "InkyDisplayProject/1.0 (smule12@gmail.com)"
}

# Maps MET symbol codes to icon filenames
SYMBOL_ICON_MAP = {
    "clearsky_day": "clear_day.png",
    "clearsky_night": "clear_night.png",
    "cloudy": "cloudy.png",
    "fair_day": "partly_cloudy.png",
    "fair_night": "partly_cloudy.png",
    "fog": "cloudy.png",
    "heavyrain": "rain.png",
    "heavyrainandthunder": "thunder.png",
    "heavyrainshowers_day": "rain.png",
    "heavysnow": "snow.png",
    "heavysnowshowers_day": "snow.png",
    "lightrain": "sleet.png",
    "lightrainshowers_day": "sleet.png",
    "lightssnow": "snow.png",
    "partlycloudy_day": "partly_cloudy.png",
    "partlycloudy_night": "partly_cloudy.png",
    "rain": "rain.png",
    "rainshowers_day": "rain.png",
    "sleet": "sleet.png",
    "snow": "snow.png",
    "snowshowers_day": "snow.png",
    "thunderstorm": "thunder.png"
}

def get_weather_icon_path(weather_data):
    """Get the file path for the weather icon based on symbol code."""
    symbol = weather_data.get("symbol_code", "clearsky_day")
    filename = SYMBOL_ICON_MAP.get(symbol, "clear_day.png")
    return os.path.join("assets", "weather", filename)

def get_weather(full_forecast=False):
    """Fetch weather data from MET Norway API."""
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={LAT}&lon={LON}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return {"error": "API failure"}

    timeseries = data["properties"]["timeseries"]
    current = timeseries[0]
    instant = current["data"]["instant"]["details"]
    next_hour = current["data"].get("next_1_hours", {})
    summary = next_hour.get("summary", {})
    rain_amount = next_hour.get("details", {}).get("precipitation_amount", 0.0)

    # Get current temperature
    temp = instant.get("air_temperature", 0)
    
    # Find min/max temperatures from the next 24 hours
    temp_min = temp
    temp_max = temp
    
    # Look through the next 24 hours for min/max
    for slot in timeseries[:24]:
        slot_temp = slot["data"]["instant"]["details"].get("air_temperature")
        if slot_temp is not None:
            if slot_temp < temp_min:
                temp_min = slot_temp
            if slot_temp > temp_max:
                temp_max = slot_temp

    # If we still don't have different values, try next_6_hours data
    if temp_min == temp_max:
        for slot in timeseries[:4]:
            next_6h = slot["data"].get("next_6_hours", {}).get("details", {})
            if "air_temperature_min" in next_6h:
                temp_min = next_6h["air_temperature_min"]
            if "air_temperature_max" in next_6h:
                temp_max = next_6h["air_temperature_max"]
            if temp_min != temp_max:
                break

    weather = {
        "temp": round(temp),
        "condition": summary.get("symbol_code", "clearsky_day"),
        "description": summary.get("symbol_code", ""),
        "icon_code": summary.get("symbol_code", ""),
        "rain_probability": None,
        "rain_amount": rain_amount,
        "wind": round(instant.get("wind_speed", 0)),
        "cloud": round(instant.get("cloud_area_fraction", 0)),
        "symbol_code": summary.get("symbol_code", ""),
        "temp_min": int(round(temp_min)),
        "temp_max": int(round(temp_max)),
    }

    if full_forecast:
        weather["raw"] = data

    return weather

if __name__ == '__main__':
    # Test the weather function
    weather_data = get_weather(full_forecast=True)
    print("Weather data:")
    for key, value in weather_data.items():
        if key != "raw":  # Don't print the raw data, it's huge
            print(f"  {key}: {value}")
    
    # Test icon path
    icon_path = get_weather_icon_path(weather_data)
    print(f"\nIcon path: {icon_path}")
    print(f"Icon exists: {os.path.exists(icon_path)}")
