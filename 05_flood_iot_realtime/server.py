"""
Real‑Time Flood Monitoring (Humanised)
--------------------------------------
A tiny Flask API that receives water‑level readings and returns a simple
LOW / MEDIUM / HIGH risk status. Use `sensor.py` to simulate a device.
"""
from flask import Flask, request, jsonify, render_template_string
import time

app = Flask(__name__)

latest = {"timestamp": None, "water_level_cm": 0.0}

def risk_level(water_level_cm: float) -> str:
    """Translate water level to a friendly risk label."""
    if water_level_cm > 120:
        return "HIGH"
    if water_level_cm > 80:
        return "MEDIUM"
    return "LOW"

@app.route("/ingest", methods=["POST"])
def ingest():
    """Receive a JSON payload like {"water_level_cm": 92}."""
    payload = request.get_json(silent=True) or {}
    if "water_level_cm" not in payload:
        return jsonify({"error": "Missing 'water_level_cm'"}), 400
    try:
        wl = float(payload["water_level_cm"])
    except ValueError:
        return jsonify({"error": "water_level_cm must be a number"}), 400

    latest["timestamp"] = time.time()
    latest["water_level_cm"] = wl
    return jsonify({"status": "ok"})

@app.route("/status")
def status():
    """Return the most recent reading and the derived risk."""
    wl = latest["water_level_cm"]
    return jsonify({"latest": latest, "risk": risk_level(wl)})

@app.route("/")
def index():
    """Simple web page to view current status."""
    page = """
    <html><head><title>IoT Flood Monitor</title></head>
    <body style="font-family: system-ui; max-width: 760px; margin: 2rem auto">
        <h1>IoT Flood Monitor (Demo)</h1>
        <p>POST JSON to <code>/ingest</code>, e.g. <code>{"water_level_cm": 92}</code>.</p>
        <button onclick="refresh()">Refresh Status</button>
        <pre id="out"></pre>
        <script>
        async function refresh(){
            const res = await fetch('/status');
            const j = await res.json();
            document.getElementById('out').textContent = JSON.stringify(j, null, 2);
        }
        refresh();
        setInterval(refresh, 2000);
        </script>
    </body></html>
    """
    return render_template_string(page)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
