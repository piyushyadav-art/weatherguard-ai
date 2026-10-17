import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_weather_anomalies(csv_path: str):
    df = pd.read_csv(csv_path)

    features = [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m"
    ]

    clean_df = df.dropna(subset=features).copy()

    model = IsolationForest(
        contamination=0.03,
        random_state=42
    )

    clean_df["anomaly_label"] = model.fit_predict(clean_df[features])
    clean_df["anomaly_score"] = model.decision_function(clean_df[features])

    anomalies = clean_df[
        clean_df["anomaly_label"] == -1
    ].sort_values("anomaly_score")

    return anomalies


if __name__ == "__main__":
    anomalies = detect_weather_anomalies("lucknow_weather_history.csv")

    print("\nTOTAL ANOMALIES:", len(anomalies))
    print("\nMOST UNUSUAL WEATHER RECORDS:\n")

    print(
        anomalies[
            [
                "time",
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m",
                "anomaly_score"
            ]
        ].head(15).to_string(index=False)
    )

    anomalies.to_csv("detected_anomalies.csv", index=False)
    print("\nSaved results to detected_anomalies.csv")