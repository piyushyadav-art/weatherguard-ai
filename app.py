from weather_tools import get_weather, summarize_weather
from alerts import create_weather_alerts

latitude = 26.8467
longitude = 80.9462

weather_data = get_weather(latitude, longitude)
weather_summary = summarize_weather(weather_data)

weather_alerts = create_weather_alerts(weather_summary)

print("\nWEATHER SUMMARY")
print(weather_summary)

print("\nALERTS")
for alert in weather_alerts:
    print(f"[{alert['level']}] {alert['type']}: {alert['message']}")


from anomaly import get_nearby_earthquakes, earthquake_alerts

earthquakes = get_nearby_earthquakes(
    latitude=latitude,
    longitude=longitude,
    radius_km=1000
)

quake_alerts = earthquake_alerts(earthquakes)

print("\nEARTHQUAKE MONITORING")
if not earthquakes:
    print("No nearby earthquake events found in selected radius.")

for quake in earthquakes[:5]:
    print(quake)

for alert in quake_alerts:
    print(f"[{alert['level']}] {alert['type']}: {alert['message']}")