from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END

from weather_tools import get_weather, summarize_weather
from alerts import create_weather_alerts
from anomaly import get_nearby_earthquakes, earthquake_alerts


class WeatherState(TypedDict, total=False):
    latitude: float
    longitude: float
    weather: dict[str, Any]
    weather_alerts: list[dict]
    earthquakes: list[dict]
    earthquake_alerts: list[dict]
    final_report: dict[str, Any]


def weather_node(state: WeatherState):
    raw_weather = get_weather(
        state["latitude"],
        state["longitude"]
    )

    summary = summarize_weather(raw_weather)

    return {
        "weather": summary
    }


def weather_risk_node(state: WeatherState):
    alerts = create_weather_alerts(state["weather"])

    return {
        "weather_alerts": alerts
    }


def earthquake_node(state: WeatherState):
    earthquakes = get_nearby_earthquakes(
        state["latitude"],
        state["longitude"],
        radius_km=1000
    )

    return {
        "earthquakes": earthquakes
    }


def earthquake_risk_node(state: WeatherState):
    alerts = earthquake_alerts(state["earthquakes"])

    return {
        "earthquake_alerts": alerts
    }


def report_node(state: WeatherState):
    all_alerts = state["weather_alerts"] + state["earthquake_alerts"]

    priority_order = {"LOW": 1, "MODERATE": 2, "HIGH": 3}

    highest_risk = "LOW"
    for alert in all_alerts:
        if priority_order[alert["level"]] > priority_order[highest_risk]:
            highest_risk = alert["level"]

    return {
        "final_report": {
            "location": {
                "latitude": state["latitude"],
                "longitude": state["longitude"]
            },
            "overall_risk": highest_risk,
            "weather": state["weather"],
            "alerts": all_alerts,
            "nearby_earthquakes": state["earthquakes"][:5]
        }
    }


def build_graph():
    builder = StateGraph(WeatherState)

    builder.add_node("fetch_weather", weather_node)
    builder.add_node("analyze_weather_risk", weather_risk_node)
    builder.add_node("fetch_earthquakes", earthquake_node)
    builder.add_node("analyze_earthquake_risk", earthquake_risk_node)
    builder.add_node("create_report", report_node)

    builder.add_edge(START, "fetch_weather")
    builder.add_edge("fetch_weather", "analyze_weather_risk")
    builder.add_edge("analyze_weather_risk", "fetch_earthquakes")
    builder.add_edge("fetch_earthquakes", "analyze_earthquake_risk")
    builder.add_edge("analyze_earthquake_risk", "create_report")
    builder.add_edge("create_report", END)

    return builder.compile()