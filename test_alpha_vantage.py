import requests
import json
from datetime import datetime

# Alpha Vantage API key
API_KEY = "5C36SA6HEI01HACN"

def test_alpha_vantage():
    """Test Alpha Vantage API for SPX data"""
    
    # Test 1: Real-time quote (try SPY first as it's more common)
    print("🔍 Testing Alpha Vantage Real-time Quote...")
    quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey={API_KEY}"
    
    try:
        response = requests.get(quote_url, timeout=10)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Response: {json.dumps(data, indent=2)}")
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                print(f"✅ SPX Price: ${quote.get('05. price', 'N/A')}")
                print(f"✅ Change: {quote.get('09. change', 'N/A')}")
                print(f"✅ Change %: {quote.get('10. change percent', 'N/A')}")
            else:
                print("❌ No Global Quote data found")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Intraday data (1-minute intervals)
    print("🔍 Testing Alpha Vantage Intraday Data...")
    intraday_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=1min&apikey={API_KEY}"
    
    try:
        response = requests.get(intraday_url, timeout=10)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'Time Series (1min)' in data:
                time_series = data['Time Series (1min)']
                print(f"✅ Got {len(time_series)} data points")
                
                # Get the latest 5 data points
                latest_times = sorted(time_series.keys(), reverse=True)[:5]
                print("\n📈 Latest 5 data points:")
                for time in latest_times:
                    price_data = time_series[time]
                    print(f"  {time}: Open={price_data['1. open']}, High={price_data['2. high']}, Low={price_data['3. low']}, Close={price_data['4. close']}, Volume={price_data['5. volume']}")
                    
            elif 'Error Message' in data:
                print(f"❌ API Error: {data['Error Message']}")
            elif 'Note' in data:
                print(f"⚠️ API Note: {data['Note']}")
            else:
                print(f"❌ Unexpected response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_alpha_vantage()
