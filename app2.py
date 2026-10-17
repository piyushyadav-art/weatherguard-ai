from graph import build_graph

app = build_graph()

result = app.invoke({
    "latitude": 26.8467,
    "longitude": 80.9462
})

report = result["final_report"]

print("\nNATURAL RISK REPORT")
print("Overall risk:", report["overall_risk"])

print("\nCurrent weather")
for key, value in report["weather"].items():
    print(f"{key}: {value}")

print("\nAlerts")
for alert in report["alerts"]:
    print(f"[{alert['level']}] {alert['type']}: {alert['message']}")