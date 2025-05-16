import requests
import json

API_URL = "https://api.0dtespx.com/aggregateData?series=spx,spxExpectedMove&date=live&interval=30"

def test_api():
    print(f"Attempting to fetch data from: {API_URL}")
    try:
        response = requests.get(API_URL)
        print(f"Status Code: {response.status_code}")
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        
        print("\nResponse JSON:")
        # Pretty print the JSON response
        print(json.dumps(response.json(), indent=4))
        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    except json.JSONDecodeError:
        print("Failed to decode JSON from response. Raw content:")
        print(response.text)

if __name__ == "__main__":
    test_api()
