import requests
from math import radians,sin,cos,sqrt,atan2

USGS_FEED = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

def harvesine_distance_km(lat1,lon1,lat2,lon2):
    earth_radius_km = 6371
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)

    a = (
        sin(d_lat /2)**2 
        + cos(radians(lat1))
        *cos(radians(lat2))
        *sin(d_lon / 2)**2
    )
    c = 2*atan2(sqrt(a), sqrt(1-a))
    return earth_radius_km * c

def get_nearby_earthquakes(latitude: float,longitude:float,radius_km=500):
    response = requests.get(USGS_FEED,timeout=20)
    response.raise_for_status()

    features = response.json()["features"]
    nearby = []
    for feature in features:
        props = feature["properties"]
        quake_lon,quake_lat,depth_km = feature["geometry"]["coordinates"]

        distance_km = harvesine_distance_km(
            latitude,
            longitude,
            quake_lat,
            quake_lon
        )
        if distance_km <= radius_km:
            nearby.append({
                "place":props["place"],
                "magnitude":props["mag"],
                "time_ms":props["time"],
                "distance_km":round(distance_km,2),
                "depth_km":depth_km,
                "latitude": quake_lat,
                "longitude": quake_lon,
                "url":props["url"]
            })
    return sorted(nearby, key=lambda item: item["magnitude"],reverse=True)

def earthquake_alerts(earthquakes: list[dict]) -> list[dict]:
    alerts = []
    for quake in earthquakes:
        if quake["magnitude"]>=6:
            alerts.append({
                "level":"HIGH",
                "type":"Earthquake",
                "message":f"M{quake['magnitude']} earthquake detected {quake['distance_km']} km away near {quake['place']}."
            })
        elif quake["magnitude"] >= 4.5:
            alerts.append({
                "level":"MODERATE",
                "type":"Earthquake",
                "message":f"M{quake['magnitude']} earthquake detected {quake['distance_km']} km away near {quake['place']}."
            })
    return alerts
