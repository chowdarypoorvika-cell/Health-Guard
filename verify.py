import requests
import time
import requests

try:
    print("Testing /stream endpoint...")
    r = requests.get("http://localhost:8000/stream")
    if r.status_code == 200:
        print("Stream Data:", r.json())
    else:
        print("Stream Error:", r.status_code)

    print("\nTesting /train-fl endpoint (Federated Learning)...")
    r = requests.post("http://localhost:8000/train-fl")
    if r.status_code == 200:
        print("FL Results:", r.json())
    else:
        print("FL Error:", r.status_code)
except Exception as e:
    print("Connection failed:", e)
