"""
Mock Sensor (Humanised)
-----------------------
Sends a random water level to the Flask server every ~1.5 seconds.
"""
import time, requests, random

URL = "http://127.0.0.1:5000/ingest"

if __name__ == "__main__":
    while True:
        water_level_cm = max(0, random.gauss(70, 30))
        try:
            r = requests.post(URL, json={"water_level_cm": water_level_cm}, timeout=2)
            print("Sent:", round(water_level_cm,1), "cm ->", r.status_code)
        except Exception as e:
            print("Error sending to server:", e)
        time.sleep(1.5)
