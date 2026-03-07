import requests
import random
import time

API_URL = "http://127.0.0.1:8000/predict"

try:
    while True:
        ph = random.uniform(6, 9)
        tds = random.uniform(100, 600)
        conductivity = random.uniform(200, 800)
        turbidity = random.uniform(1, 10)

        try:
            response = requests.post(API_URL, params={
                "ph": ph,
                "tds": tds,
                "conductivity": conductivity,
                "turbidity": turbidity
            }, timeout=10)
            response.raise_for_status()
            print(response.json())
        except requests.exceptions.ConnectionError:
            print("[ERROR] Could not connect to API. Is the server running?")
        except requests.exceptions.Timeout:
            print("[ERROR] Request timed out.")
        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] HTTP error: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")

        time.sleep(5)
except KeyboardInterrupt:
    print("\nSensor simulator stopped.")

