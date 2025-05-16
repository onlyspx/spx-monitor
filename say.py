import requests
import time
import os

API_URL = "https://api.0dtespx.com/aggregateData?series=spx,spxExpectedMove&date=live&interval=30"

def get_spx_value():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            spx_data = data.get("spx", [])
            if spx_data:
                latest = spx_data[-1]  # get the latest data point
                spx_value = latest.get("value")
                return spx_value
        print("Failed to get SPX value from API.")
    except Exception as e:
        print(f"Error fetching SPX: {e}")
    return None

def announce_spx():
    value = get_spx_value()
    if value is not None:
        message = f"The current S P X value is {value:.2f}"
        print(message)
        os.system(f'say "{message}"')
    else:
        print("No SPX value to announce.")

if __name__ == "__main__":
    while True:
        announce_spx()
        time.sleep(60)  # Wait 1 minute
