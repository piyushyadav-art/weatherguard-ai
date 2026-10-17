import time

import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather(latitude: float,longitude: float) -> dict:
    params = {
        "latitude":latitude,
        "longitude":longitude,
        "current":[
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "rain",
            "weather_code",
            "wind_speed_10m",
            "wind_gusts_10m"
        ],
        "hourly":[
            "temperature_2m",
            "precipitation_probability",
            "precipitation",
            "rain",
            "wind_speed_10m",
            "wind_gusts_10m",
            "weather_code"
        ],
        "forecast_days":2,
        "timezone":"auto"
    }

    # Open-Meteo can occasionally return 503 while the service is busy.
    # Retry a few times with a short backoff before surfacing the error.
    for attempt in range(3):
        try:
            response = requests.get(BASE_URL, params=params, timeout=20)
            if response.status_code != 503 or attempt == 2:
                response.raise_for_status()
                return response.json()
        except requests.RequestException:
            if attempt == 2:
                raise

        time.sleep(2 ** attempt)

    raise RuntimeError("Weather service is temporarily unavailable. Please try again later.")

def summarize_weather(data: dict) -> dict:
    current = data["current"]
    hourly = data["hourly"]

    next_24_rain_probability = max(hourly["precipitation_probability"][:24])
    next_24_rain_mm = round(sum(hourly["rain"][:24]),2)
    max_wind_gust = round(max(hourly['wind_gusts_10m'][:24]),2)
    max_temperature = round(max(hourly["temperature_2m"][:24]),2)

    return {
        "current_temperature_c": current["temperature_2m"],
        "feels_like_c": current["apparent_temperature"],
        "humidity_percent": current["relative_humidity_2m"],
        "current_rain_mm": current["rain"],
        "current_wind_kmh": current["wind_speed_10m"],
        "current_gust_kmh": current["wind_gusts_10m"],
        "next_24h_rain_probability": next_24_rain_probability,
        "next_24h_rain_mm": next_24_rain_mm,
        "next_24h_max_gust_kmh": max_wind_gust,
        "next_24h_max_temp_c": max_temperature
        }

