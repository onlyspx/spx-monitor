import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Alpha Vantage API key
API_KEY = "5C36SA6HEI01HACN"

def get_spy_data():
    """Get SPY intraday data from Alpha Vantage"""
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=1min&apikey={API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'Time Series (1min)' in data:
                return data['Time Series (1min)']
    except Exception as e:
        print(f"Error fetching data: {e}")
    return None

def calculate_moving_averages(prices, periods):
    """Calculate EMA and SMA for given periods"""
    prices = np.array(prices, dtype=float)
    
    # Calculate SMA
    sma = []
    for i in range(len(prices)):
        if i < periods - 1:
            sma.append(np.nan)
        else:
            sma.append(np.mean(prices[i-periods+1:i+1]))
    
    # Calculate EMA
    ema = []
    multiplier = 2 / (periods + 1)
    
    for i in range(len(prices)):
        if i == 0:
            ema.append(prices[i])
        else:
            ema.append((prices[i] * multiplier) + (ema[i-1] * (1 - multiplier)))
    
    return sma, ema

def analyze_trend(current_price, ma_values):
    """Analyze trend based on current price vs moving averages"""
    ma_50_ema, ma_50_sma, ma_200_ema, ma_200_sma = ma_values
    
    # Check if we have enough data
    if any(np.isnan([ma_50_ema, ma_50_sma, ma_200_ema, ma_200_sma])):
        return "Insufficient Data", "Need more data points"
    
    # Determine trend
    above_all = current_price > ma_50_ema and current_price > ma_50_sma and current_price > ma_200_ema and current_price > ma_200_sma
    below_all = current_price < ma_50_ema and current_price < ma_50_sma and current_price < ma_200_ema and current_price < ma_200_sma
    
    if above_all:
        trend = "BULLISH"
        signal = "Price above all 4 MAs - Strong uptrend"
    elif below_all:
        trend = "BEARISH" 
        signal = "Price below all 4 MAs - Strong downtrend"
    else:
        trend = "CHOP"
        signal = "Price between MAs - Mixed signals, choppy market"
    
    # Check for potential reversals
    if trend == "CHOP":
        if current_price > ma_50_ema and current_price > ma_50_sma:
            signal += " (Approaching from above - potential bearish reversal)"
        elif current_price < ma_50_ema and current_price < ma_50_sma:
            signal += " (Approaching from below - potential bullish reversal)"
    
    return trend, signal

def get_ma_distances(current_price, ma_values):
    """Calculate distance from each MA"""
    ma_50_ema, ma_50_sma, ma_200_ema, ma_200_sma = ma_values
    
    distances = {
        '50_EMA': ((current_price - ma_50_ema) / ma_50_ema) * 100,
        '50_SMA': ((current_price - ma_50_sma) / ma_50_sma) * 100,
        '200_EMA': ((current_price - ma_200_ema) / ma_200_ema) * 100,
        '200_SMA': ((current_price - ma_200_sma) / ma_200_sma) * 100
    }
    
    return distances

def main():
    """Main function to run the EMA/SMA strategy"""
    print("🚀 SPY EMA/SMA Strategy Analysis")
    print("=" * 50)
    
    # Get data
    print("📊 Fetching SPY data...")
    data = get_spy_data()
    
    if not data:
        print("❌ Failed to fetch data")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data).T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    
    # Get closing prices
    prices = df['4. close'].astype(float).values
    
    if len(prices) < 50:
        print(f"❌ Need at least 50 data points, got {len(prices)}")
        return
    
    print(f"✅ Got {len(prices)} data points")
    
    # Calculate moving averages (adjust periods based on available data)
    print("📈 Calculating moving averages...")
    max_period = min(50, len(prices) - 1)
    sma_50, ema_50 = calculate_moving_averages(prices, max_period)
    
    # For 200 MA, use available data or skip if not enough
    if len(prices) >= 200:
        sma_200, ema_200 = calculate_moving_averages(prices, 200)
    else:
        print(f"⚠️ Not enough data for 200 MA, using {max_period} period instead")
        sma_200, ema_200 = calculate_moving_averages(prices, max_period)
    
    # Get current values
    current_price = prices[-1]
    current_ma_values = [ema_50[-1], sma_50[-1], ema_200[-1], sma_200[-1]]
    
    # Analyze trend
    trend, signal = analyze_trend(current_price, current_ma_values)
    
    # Get distances
    distances = get_ma_distances(current_price, current_ma_values)
    
    # Display results
    print(f"\n📊 Current Analysis:")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Trend: {trend}")
    print(f"Signal: {signal}")
    
    print(f"\n📈 Moving Averages:")
    print(f"50 EMA: ${ema_50[-1]:.2f} ({distances['50_EMA']:+.2f}%)")
    print(f"50 SMA: ${sma_50[-1]:.2f} ({distances['50_SMA']:+.2f}%)")
    print(f"200 EMA: ${ema_200[-1]:.2f} ({distances['200_EMA']:+.2f}%)")
    print(f"200 SMA: ${sma_200[-1]:.2f} ({distances['200_SMA']:+.2f}%)")
    
    # Check for crossovers
    print(f"\n🔄 Crossover Analysis:")
    if len(ema_50) > 1 and len(ema_200) > 1:
        if ema_50[-1] > ema_200[-1] and ema_50[-2] <= ema_200[-2]:
            print("🟢 Golden Cross: 50 EMA crossed above 200 EMA")
        elif ema_50[-1] < ema_200[-1] and ema_50[-2] >= ema_200[-2]:
            print("🔴 Death Cross: 50 EMA crossed below 200 EMA")
        else:
            print("⚪ No recent crossover")
    
    # MA slopes
    print(f"\n📊 MA Slopes (trend direction):")
    if len(ema_50) > 10:
        ema_50_slope = (ema_50[-1] - ema_50[-10]) / 10
        ema_200_slope = (ema_200[-1] - ema_200[-10]) / 10
        print(f"50 EMA slope: {ema_50_slope:+.4f} ({'📈' if ema_50_slope > 0 else '📉'})")
        print(f"200 EMA slope: {ema_200_slope:+.4f} ({'📈' if ema_200_slope > 0 else '📉'})")

if __name__ == "__main__":
    main()
