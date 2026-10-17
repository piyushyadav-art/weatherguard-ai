from graph import build_graph
from llm_explainer import explain_report
from ml_anomaly import detect_weather_anomalies


def main():
    print("\n--- STEP 1: WEATHER + EARTHQUAKE LANGGRAPH WORKFLOW ---")

    app = build_graph()

    result = app.invoke({
        "latitude": 26.8467,
        "longitude": 80.9462
    })

    report = result["final_report"]

    print("\nSTRUCTURED REPORT")
    print(report)

    print("\n--- STEP 2: HISTORICAL WEATHER ANOMALIES ---")

    anomalies = detect_weather_anomalies("lucknow_weather_history.csv")

    recent_anomalies = anomalies[
        [
            "time",
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
            "anomaly_score"
        ]
    ].head(5).to_dict(orient="records")

    report["historical_anomalies"] = recent_anomalies

    print(f"Detected historical anomalies: {len(anomalies)}")

    print("\n--- STEP 3: LLM EXPLANATION ---")

    explanation = explain_report(report)

    print("\nAI WEATHER EXPLANATION\n")
    print(explanation)


if __name__ == "__main__":
    main()