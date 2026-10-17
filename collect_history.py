import requests
import pandas as pd

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": 26.8467,
    "longitude": 80.9462,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m"
    ],
    "timezone": "Asia/Kolkata"
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

hourly = response.json()["hourly"]

df = pd.DataFrame({
    "time": hourly["time"],
    "temperature_2m": hourly["temperature_2m"],
    "relative_humidity_2m": hourly["relative_humidity_2m"],
    "precipitation": hourly["precipitation"],
    "wind_speed_10m": hourly["wind_speed_10m"]
})

df.to_csv("lucknow_weather_history.csv", index=False)

print("Saved rows:", len(df))
print(df.head())