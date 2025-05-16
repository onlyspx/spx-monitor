import requests
import time
import os

API_URL = "https://api.0dtespx.com/aggregateData?series=spx,spxExpectedMove&date=live&interval=30"

def get_spx_value():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json() # This is a list of dictionaries
            if data: # Check if the list is not empty
                latest_datapoint = data[-1] # Get the last dictionary in the list
                spx_value_str = latest_datapoint.get("spx")
                if spx_value_str is not None:
                    try:
                        return float(spx_value_str)
                    except ValueError:
                        print(f"Could not convert SPX value to float: {spx_value_str}")
                else:
                    print("SPX key not found in the latest data point.")
            else:
                print("API returned empty data list.")
        else: # Added else for response.status_code != 200
            print(f"Failed to get SPX value from API. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching SPX: {e}")
    return None

def announce_spx():
    value = get_spx_value()
    if value is not None:
        int_value = int(value)
        print_message = f"SPX at {int_value}"
        print(print_message)

        # Prepare message for speech
        str_value = str(int_value)
        if len(str_value) == 4:
            # Split into two pairs for "XX YY" pronunciation, e.g., "59 43"
            speak_value_formatted = f"{str_value[:2]} {str_value[2:]}"
        else:
            # Pronounce normally for other lengths
            speak_value_formatted = str_value
        
        speak_message = f"SPX at {speak_value_formatted}"
        os.system(f'say "{speak_message}"')
    else:
        print("No SPX value to announce.")

if __name__ == "__main__":
    while True:
        announce_spx()
        time.sleep(20)
