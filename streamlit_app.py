import streamlit as st
import pandas as pd
import json
from pathlib import Path

from graph import build_graph
from llm_explainer import explain_report
from ml_anomaly import detect_weather_anomalies


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="WeatherGuard AI",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0B3D91;
        margin-bottom: 0;
    }

    .subtitle {
        color: #5B6472;
        font-size: 1.05rem;
        margin-bottom: 1rem;
    }

    .risk-card {
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        color: white;
        margin-bottom: 15px;
    }

    .low-risk {
        background-color: #198754;
    }

    .moderate-risk {
        background-color: #F0AD4E;
    }

    .high-risk {
        background-color: #DC3545;
    }

    .info-box {
        background-color: #F3F7FF;
        border-left: 5px solid #0B3D91;
        padding: 14px;
        border-radius: 8px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- CACHED FUNCTIONS ----------------
@st.cache_resource
def get_graph_app():
    return build_graph()


@st.cache_data(ttl=900)
def run_weather_workflow(latitude: float, longitude: float):
    graph_app = get_graph_app()

    result = graph_app.invoke({
        "latitude": latitude,
        "longitude": longitude
    })

    return result["final_report"]


@st.cache_data
def load_anomalies(csv_file: str):
    anomalies = detect_weather_anomalies(csv_file)
    return anomalies


def get_risk_class(risk_level: str):
    risk_level = risk_level.upper()

    if risk_level == "HIGH":
        return "high-risk"

    if risk_level == "MODERATE":
        return "moderate-risk"

    return "low-risk"


def format_alert(alert: dict):
    level = alert.get("level", "LOW")
    alert_type = alert.get("type", "Unknown")
    message = alert.get("message", "No message available.")

    if level == "HIGH":
        icon = "🔴"
    elif level == "MODERATE":
        icon = "🟠"
    else:
        icon = "🟢"

    return f"{icon} **{level} — {alert_type}**  \n{message}"


# ---------------- SESSION STATE ----------------
if "report" not in st.session_state:
    st.session_state.report = None

if "explanation" not in st.session_state:
    st.session_state.explanation = None

if "explanation_error" not in st.session_state:
    st.session_state.explanation_error = None

if "anomalies_df" not in st.session_state:
    st.session_state.anomalies_df = None


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("Location Settings")

    city_name = st.text_input(
        "Location name",
        value="Lucknow",
        help="This is currently a display name. Coordinates control API data."
    )

    latitude = st.number_input(
        "Latitude",
        value=26.8467,
        format="%.4f"
    )

    longitude = st.number_input(
        "Longitude",
        value=80.9462,
        format="%.4f"
    )

    st.divider()

    st.header("Historical Dataset")

    csv_path = st.text_input(
        "CSV file path",
        value="lucknow_weather_history.csv"
    )

    st.caption(
        "The CSV needs temperature_2m, relative_humidity_2m, "
        "precipitation, and wind_speed_10m columns."
    )

    st.divider()

    run_button = st.button(
        "Run Weather Analysis",
        type="primary",
        width="stretch"
    )

    clear_button = st.button(
        "Clear Results",
        width="stretch"
    )


# ---------------- CLEAR RESULTS ----------------
if clear_button:
    st.session_state.report = None
    st.session_state.explanation = None
    st.session_state.explanation_error = None
    st.session_state.anomalies_df = None
    st.cache_data.clear()
    st.rerun()


# ---------------- HEADER ----------------
st.markdown('<p class="main-title">WeatherGuard AI</p>', unsafe_allow_html=True)

st.markdown(
    '<p class="subtitle">'
    'Current weather forecasting, extreme-weather alerts, earthquake monitoring, '
    'and historical anomaly detection.'
    '</p>',
    unsafe_allow_html=True
)


# ---------------- RUN WORKFLOW ----------------
if run_button:
    if not Path(csv_path).exists():
        st.error(
            f"Historical CSV file not found: `{csv_path}`. "
            "Run `collect_history.py` first or enter the correct path."
        )
    else:
        try:
            with st.spinner("Fetching weather, earthquake, and anomaly data..."):
                report = run_weather_workflow(latitude, longitude)

                anomalies_df = load_anomalies(csv_path)

                anomaly_columns = [
                    "time",
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "wind_speed_10m",
                    "anomaly_score"
                ]

                recent_anomalies = anomalies_df[
                    anomaly_columns
                ].head(5).to_dict(orient="records")

                report["historical_anomalies"] = recent_anomalies
                report["total_historical_anomalies"] = len(anomalies_df)

                # Keep the weather and anomaly results even if Gemini is unavailable.
                st.session_state.report = report
                st.session_state.anomalies_df = anomalies_df
                st.session_state.explanation = None
                st.session_state.explanation_error = None

            st.success("Analysis completed successfully.")

        except Exception as error:
            st.error("The analysis could not be completed.")
            st.exception(error)

        else:
            try:
                with st.spinner("Generating AI safety explanation with Gemini..."):
                    st.session_state.explanation = explain_report(report)
            except Exception as error:
                st.session_state.explanation_error = error


# ---------------- DISPLAY RESULTS ----------------
if st.session_state.report:
    report = st.session_state.report
    weather = report.get("weather", {})
    alerts = report.get("alerts", [])
    earthquakes = report.get("nearby_earthquakes", [])
    risk = report.get("overall_risk", "LOW")

    st.markdown(
        f'<div class="risk-card {get_risk_class(risk)}">'
        f'Overall Risk Level: {risk}'
        f'</div>',
        unsafe_allow_html=True
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Weather Overview",
        "Alerts",
        "Anomalies",
        "Earthquakes",
        "AI Explanation"
    ])

    # -------- WEATHER TAB --------
    with tab1:
        st.subheader(f"Current Conditions — {city_name}")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Temperature",
            f"{weather.get('current_temperature_c', 'N/A')} °C"
        )

        col2.metric(
            "Feels Like",
            f"{weather.get('feels_like_c', 'N/A')} °C"
        )

        col3.metric(
            "Humidity",
            f"{weather.get('humidity_percent', 'N/A')} %"
        )

        col4.metric(
            "Current Wind",
            f"{weather.get('current_wind_kmh', 'N/A')} km/h"
        )

        st.divider()

        st.subheader("Next 24-Hour Forecast Risk")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Rain Probability",
            f"{weather.get('next_24h_rain_probability', 'N/A')} %"
        )

        col2.metric(
            "Expected Rainfall",
            f"{weather.get('next_24h_rain_mm', 'N/A')} mm"
        )

        col3.metric(
            "Maximum Wind Gust",
            f"{weather.get('next_24h_max_gust_kmh', 'N/A')} km/h"
        )

        col4.metric(
            "Maximum Temperature",
            f"{weather.get('next_24h_max_temp_c', 'N/A')} °C"
        )

        with st.expander("View Raw Weather Data"):
            st.json(weather)

    # -------- ALERT TAB --------
    with tab2:
        st.subheader("Detected Weather and Disaster Alerts")

        if alerts:
            for alert in alerts:
                st.markdown(format_alert(alert))
                st.divider()
        else:
            st.info("No alerts were generated.")

        st.warning(
            "This is a student decision-support project, not an official emergency-warning service. "
            "Follow IMD, NDMA, local administration, and disaster-management authorities during emergencies."
        )

    # -------- ANOMALY TAB --------
    with tab3:
        st.subheader("Historical Weather Anomalies")

        anomalies_df = st.session_state.anomalies_df

        if anomalies_df is not None and not anomalies_df.empty:
            st.metric(
                "Detected Historical Anomalies",
                report.get("total_historical_anomalies", len(anomalies_df))
            )

            display_columns = [
                "time",
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m",
                "anomaly_score"
            ]

            available_columns = [
                col for col in display_columns
                if col in anomalies_df.columns
            ]

            st.dataframe(
                anomalies_df[available_columns],
                width="stretch",
                hide_index=True
            )

            st.download_button(
                label="Download Anomaly Results as CSV",
                data=anomalies_df.to_csv(index=False).encode("utf-8"),
                file_name="weather_anomalies.csv",
                mime="text/csv",
                width="stretch"
            )

        else:
            st.info(
                "No anomalies are available. Check the CSV file and run the analysis again."
            )

    # -------- EARTHQUAKE TAB --------
    with tab4:
        st.subheader("Nearby Earthquake Monitoring")

        if earthquakes:
            quake_df = pd.DataFrame(earthquakes)

            wanted_columns = [
                "place",
                "magnitude",
                "distance_km",
                "depth_km",
                "url"
            ]

            available_columns = [
                col for col in wanted_columns
                if col in quake_df.columns
            ]

            st.dataframe(
                quake_df[available_columns],
                width="stretch",
                hide_index=True
            )

            st.map(
                pd.DataFrame({
                    "lat": [
                        quake.get("latitude")
                        for quake in earthquakes
                        if quake.get("latitude") is not None
                    ],
                    "lon": [
                        quake.get("longitude")
                        for quake in earthquakes
                        if quake.get("longitude") is not None
                    ]
                })
            )

        else:
            st.info("No nearby earthquake events were found for the selected radius.")

    # -------- AI TAB --------
    with tab5:
        st.subheader("AI-Generated Safety Explanation")

        if st.session_state.explanation:
            st.markdown(st.session_state.explanation)
        elif st.session_state.explanation_error:
            st.error(
                "Weather analysis completed, but Gemini could not generate the AI explanation. "
                "Check that GOOGLE_API_KEY in your .env file is valid and try again."
            )
            with st.expander("Show Gemini error details"):
                st.exception(st.session_state.explanation_error)
        else:
            st.info("Click **Run Weather Analysis** to generate an explanation.")

        with st.expander("View Complete Structured Report"):
            st.json(report)

        st.download_button(
            label="Download Full Report as JSON",
            data=json.dumps(report, indent=4, default=str),
            file_name="weatherguard_report.json",
            mime="application/json",
            width="stretch"
        )

else:
    st.info(
        "Enter coordinates in the sidebar, ensure your historical CSV exists, "
        "then click **Run Weather Analysis**."
    )
