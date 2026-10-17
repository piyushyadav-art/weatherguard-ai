def create_weather_alerts(weather: dict) -> list[dict]:
    alerts = []

    if weather["next_24h_rain_mm"] >= 64:
        alerts.append({
            "level": "HIGH",
            "type": "Heavy rainfall",
            "message": "Heavy rainfall is possible in the next 24 hours. Avoid waterlogged routes and monitor local advisories."
        })
    elif weather["next_24h_rain_mm"] >= 20:
        alerts.append({
            "level": "MODERATE",
            "type": "Rainfall",
            "message": "Moderate rainfall is possible. Carry rain protection and watch for local waterlogging."
        })

    if weather["next_24h_max_gust_kmh"] >= 70:
        alerts.append({
            "level": "HIGH",
            "type": "Strong wind",
            "message": "Potentially dangerous wind gusts are forecast. Secure loose outdoor items and avoid unstable trees."
        })
    elif weather["next_24h_max_gust_kmh"] >= 45:
        alerts.append({
            "level": "MODERATE",
            "type": "Wind",
            "message": "Strong winds are possible. Use caution while travelling outdoors."
        })

    if weather["next_24h_max_temp_c"] >= 45:
        alerts.append({
            "level": "HIGH",
            "type": "Extreme heat",
            "message": "Extreme heat risk. Limit outdoor activity, hydrate, and check official local guidance."
        })
    elif weather["next_24h_max_temp_c"] >= 40:
        alerts.append({
            "level": "MODERATE",
            "type": "Heat",
            "message": "High heat is expected. Prefer shade, hydration, and lighter activity."
        })

    if not alerts:
        alerts.append({
            "level": "LOW",
            "type": "Weather",
            "message": "No rule-based extreme-weather risk detected for the next 24 hours."
        })

    return alerts