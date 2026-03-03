import requests
import json

API_KEY = "AQ.Ab8RN6LXohl3NkSlg9iRW5GxRb3agJ92Qk9eUmfbXE3__NVg7w"
SERVER_URL = "https://stitch.googleapis.com/mcp"
PROJECT_ID = "7525374144072335233"
SCREEN_ID = "116054161f19447a9ef432bf5ca45d09"

def call_mcp(method, params):
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY
    }
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    try:
        response = requests.post(SERVER_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

print("\nTrying get_screen_code...")
res = call_mcp("get_screen_code", {
    "projectId": PROJECT_ID,
    "screenId": SCREEN_ID
})
print(json.dumps(res, indent=2))
