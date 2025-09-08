import os
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from data_storage import data_storage

# Environment variables
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '5C36SA6HEI01HACN')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', 'https://discord.com/api/webhooks/1408429479189151865/OxyU99MokLJ2-4LfTYwh42-O0DJ99SECgg4Jvt5vfMrho0Bz0dnCZ5euw6fsuXt1oRRA')

class EMASMABot:
    def __init__(self):
        self.api_key = ALPHA_VANTAGE_KEY
        self.discord_webhook = DISCORD_WEBHOOK_URL
        self.last_signal = None
        self.last_commit_time = None
        
    def get_spy_data(self):
        """Get SPY intraday data from Alpha Vantage"""
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=1min&apikey={self.api_key}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'Time Series (1min)' in data:
                    return data['Time Series (1min)']
        except Exception as e:
            print(f"Error fetching data: {e}")
        return None
    
    def calculate_moving_averages(self, prices, periods):
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
    
    def analyze_trend(self, current_price, ma_values):
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
    
    def post_to_discord(self, message, color=0x00ff00):
        """Post message to Discord webhook"""
        try:
            embed = {
                "title": "SPY EMA/SMA Analysis",
                "description": message,
                "color": color,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            payload = {"embeds": [embed]}
            response = requests.post(self.discord_webhook, json=payload)
            
            if response.status_code == 204:
                print(f"✅ Posted to Discord: {message[:50]}...")
                return True
            else:
                print(f"❌ Failed to post to Discord. Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error posting to Discord: {e}")
            return False
    
    def process_new_data(self):
        """Process new data and generate signals"""
        print("🔍 Fetching new SPY data...")
        data = self.get_spy_data()
        
        if not data:
            print("❌ No data received")
            return
        
        # Get the latest data point
        latest_time = max(data.keys())
        latest_data = data[latest_time]
        
        # Store the data point
        data_point = {
            'timestamp': latest_time,
            'open': float(latest_data['1. open']),
            'high': float(latest_data['2. high']),
            'low': float(latest_data['3. low']),
            'close': float(latest_data['4. close']),
            'volume': int(latest_data['5. volume'])
        }
        
        # Append to storage
        data_storage.append_spy_data(data_point)
        
        # Get historical data for MA calculations
        historical_data = data_storage.get_historical_data(days=30)
        
        if len(historical_data) < 50:
            print(f"⚠️ Need at least 50 data points, got {len(historical_data)}")
            return
        
        # Extract prices
        prices = [d['close'] for d in historical_data]
        
        # Calculate moving averages
        max_period = min(50, len(prices) - 1)
        sma_50, ema_50 = self.calculate_moving_averages(prices, max_period)
        
        if len(prices) >= 200:
            sma_200, ema_200 = self.calculate_moving_averages(prices, 200)
        else:
            sma_200, ema_200 = self.calculate_moving_averages(prices, max_period)
        
        # Get current values
        current_price = prices[-1]
        current_ma_values = [ema_50[-1], sma_50[-1], ema_200[-1], sma_200[-1]]
        
        # Analyze trend
        trend, signal = self.analyze_trend(current_price, current_ma_values)
        
        # Store the signal
        signal_data = {
            'timestamp': latest_time,
            'price': current_price,
            'trend': trend,
            'signal': signal,
            'ma_50_ema': ema_50[-1],
            'ma_50_sma': sma_50[-1],
            'ma_200_ema': ema_200[-1],
            'ma_200_sma': sma_200[-1]
        }
        
        data_storage.append_ma_signal(signal_data)
        
        # Check if we should send a Discord alert
        if self.last_signal != trend:
            self.send_discord_alert(current_price, trend, signal, current_ma_values)
            self.last_signal = trend
        
        # Commit to GitHub every 30 minutes
        if self.should_commit():
            self.commit_to_github()
    
    def send_discord_alert(self, price, trend, signal, ma_values):
        """Send Discord alert for trend changes"""
        ma_50_ema, ma_50_sma, ma_200_ema, ma_200_sma = ma_values
        
        # Choose color based on trend
        if trend == "BULLISH":
            color = 0x00ff00  # Green
            emoji = "🟢"
        elif trend == "BEARISH":
            color = 0xff0000  # Red
            emoji = "🔴"
        else:
            color = 0xffaa00  # Orange
            emoji = "🟡"
        
        message = f"{emoji} **SPY Trend Change: {trend}**\n"
        message += f"Price: ${price:.2f}\n"
        message += f"Signal: {signal}\n\n"
        message += f"**Moving Averages:**\n"
        message += f"50 EMA: ${ma_50_ema:.2f}\n"
        message += f"50 SMA: ${ma_50_sma:.2f}\n"
        message += f"200 EMA: ${ma_200_ema:.2f}\n"
        message += f"200 SMA: ${ma_200_sma:.2f}\n\n"
        message += f"**Distance from MAs:**\n"
        message += f"50 EMA: {((price - ma_50_ema) / ma_50_ema * 100):+.2f}%\n"
        message += f"200 EMA: {((price - ma_200_ema) / ma_200_ema * 100):+.2f}%"
        
        self.post_to_discord(message, color)
    
    def should_commit(self):
        """Check if we should commit to GitHub"""
        if self.last_commit_time is None:
            return True
        
        time_since_last_commit = datetime.now() - self.last_commit_time
        return time_since_last_commit.total_seconds() > 1800  # 30 minutes
    
    def commit_to_github(self):
        """Commit and push to GitHub"""
        print("📝 Committing data to GitHub...")
        success = data_storage.commit_and_push("Auto-commit: Update SPY data and MA signals")
        
        if success:
            self.last_commit_time = datetime.now()
            print("✅ Successfully committed to GitHub")
        else:
            print("❌ Failed to commit to GitHub")
    
    def run(self):
        """Main run loop"""
        print("🚀 Starting SPY EMA/SMA Bot...")
        
        while True:
            try:
                self.process_new_data()
                
                # Wait 60 seconds before next check
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping bot...")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = EMASMABot()
    bot.run()
