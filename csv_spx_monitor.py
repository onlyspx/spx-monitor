import requests
import time
import json
import csv
import os
import socket
from datetime import datetime, date, timedelta
from pathlib import Path
import pytz

# Configuration
API_URL = "https://api.0dtespx.com/aggregateData?series=spx,spxExpectedMove&date=live&interval=30"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1408429479189151865/OxyU99MokLJ2-4LfTYwh42-O0DJ99SECgg4Jvt5vfMrho0Bz0dnCZ5euw6fsuXt1oRRA"
LEVELS_DIR = "levels"  # Directory to store CSV files
TOLERANCE = 5  # +/- points to test around each level

# Market hours (Pacific Time)
MARKET_OPEN_HOUR = 6
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 13  # 1 PM
MARKET_CLOSE_MINUTE = 0

# Track last posted levels to avoid spam
last_posted_levels = set()

def is_market_hours():
    """Check if current time is within market hours (Mon-Fri, 6:30 AM - 1:00 PM PT)"""
    pacific_tz = pytz.timezone('US/Pacific')
    now = datetime.now(pacific_tz)
    
    # Check if it's a weekday (Monday = 0, Sunday = 6)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if it's within market hours
    market_open = now.replace(hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE, second=0, microsecond=0)
    market_close = now.replace(hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MINUTE, second=0, microsecond=0)
    
    return market_open <= now <= market_close

def ensure_levels_directory():
    """Ensure the levels directory exists"""
    Path(LEVELS_DIR).mkdir(exist_ok=True)

def get_todays_levels_file():
    """Get the CSV file for today's levels"""
    today = date.today().strftime("%Y_%m_%d")
    return os.path.join(LEVELS_DIR, f"levels_{today}.csv")

def load_levels_from_csv(csv_file):
    """Load levels from CSV file"""
    levels = {"support": [], "resistance": []}
    
    if not os.path.exists(csv_file):
        print(f"⚠️ No levels file found for today: {csv_file}")
        return levels
    
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                level_type = row['level_type']
                level_value = float(row['level_value'])
                description = row['description']
                importance = row['importance']
                
                levels[level_type].append({
                    'value': level_value,
                    'description': description,
                    'importance': importance
                })
        
        print(f"✅ Loaded {len(levels['support'])} support and {len(levels['resistance'])} resistance levels from {csv_file}")
        return levels
        
    except Exception as e:
        print(f"❌ Error loading levels from {csv_file}: {e}")
        return levels

def get_spx_value():
    """Fetch current SPX value from API"""
    try:
        print(f"🔍 Fetching SPX data from: {API_URL}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(API_URL, headers=headers, timeout=10)
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                latest_datapoint = data[-1]
                spx_value_str = latest_datapoint.get("spx")
                if spx_value_str is not None:
                    return float(spx_value_str)
                else:
                    print("SPX key not found in the latest data point.")
                    print(f"Available keys: {list(latest_datapoint.keys())}")
            else:
                print("API returned empty data list.")
        elif response.status_code == 204:
            print(f"API returned no content (204). Market might be closed or API temporarily unavailable.")
        else:
            print(f"Failed to get SPX value from API. Status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response text: {response.text[:200]}...")
    except requests.exceptions.Timeout:
        print("⏰ API request timed out after 10 seconds")
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 Connection error: {e}")
    except Exception as e:
        print(f"❌ Error fetching SPX: {e}")
        print(f"Error type: {type(e).__name__}")
    return None

def post_to_discord(message, color=0x00ff00):
    """Post message to Discord webhook"""
    try:
        # Get hostname for identification
        hostname = socket.gethostname()
        
        embed = {
            "title": "SPX Trading Alert",
            "description": f"{message}\n\n🏠 **Host**: {hostname}",
            "color": color,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        payload = {
            "embeds": [embed]
        }
        
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"✅ Posted to Discord: {message}")
            return True
        else:
            print(f"❌ Failed to post to Discord. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error posting to Discord: {e}")
        return False

def test_discord_connection():
    """Test the Discord webhook connection"""
    print("Testing Discord webhook connection...")
    success = post_to_discord("🤖 SPX CSV Monitor Bot is now online and monitoring!", 0x00ff00)
    if success:
        print("✅ Discord webhook test successful!")
    else:
        print("❌ Discord webhook test failed!")
    return success

def get_nearby_levels(spx_value, levels, direction="up", count=3):
    """Get nearby levels in the specified direction"""
    nearby_levels = []
    
    if direction == "up":
        # Get resistance levels above current price
        for level_info in levels["resistance"]:
            level_value = level_info['value']
            if level_value > spx_value:
                nearby_levels.append({
                    'value': level_value,
                    'description': level_info['description'],
                    'importance': level_info['importance'],
                    'distance': level_value - spx_value
                })
        # Sort by distance (closest first)
        nearby_levels.sort(key=lambda x: x['distance'])
        return nearby_levels[:count]
    
    else:  # direction == "down"
        # Get support levels below current price
        for level_info in levels["support"]:
            level_value = level_info['value']
            if level_value < spx_value:
                nearby_levels.append({
                    'value': level_value,
                    'description': level_info['description'],
                    'importance': level_info['importance'],
                    'distance': spx_value - level_value
                })
        # Sort by distance (closest first)
        nearby_levels.sort(key=lambda x: x['distance'])
        return nearby_levels[:count]

def format_nearby_levels(nearby_levels):
    """Format nearby levels for display"""
    if not nearby_levels:
        return ""
    
    level_strings = []
    for level in nearby_levels:
        importance_emoji = "🔴" if level['importance'] == "high" else "🟡"
        level_strings.append(f"{importance_emoji} {level['description']} at {level['value']:.1f}")
    
    return "\n".join(level_strings)

def analyze_spx_levels(spx_value, levels):
    """Analyze SPX value against key levels and return trading signals"""
    signals = []
    
    # Check support levels (bullish signals)
    for level_info in levels["support"]:
        level_value = level_info['value']
        description = level_info['description']
        importance = level_info['importance']
        
        # Check if SPX is within tolerance of this level
        if spx_value >= level_value - TOLERANCE and spx_value <= level_value + TOLERANCE:
            level_key = f"support_{level_value}"
            if level_key not in last_posted_levels:
                importance_emoji = "🔴" if importance == "high" else "🟡"
                
                # Get nearby upside levels
                nearby_upside = get_nearby_levels(spx_value, levels, "up", 3)
                nearby_text = format_nearby_levels(nearby_upside)
                
                message = f"{importance_emoji} **SPX Support Test**: {spx_value:.2f} testing {description} at {level_value}"
                if nearby_text:
                    message += f"\n\n📈 **Next Upside Levels**:\n{nearby_text}"
                
                signals.append({
                    "type": "support",
                    "level": level_value,
                    "message": message,
                    "color": 0x00ff00
                })
                last_posted_levels.add(level_key)
    
    # Check resistance levels (bearish signals)
    for level_info in levels["resistance"]:
        level_value = level_info['value']
        description = level_info['description']
        importance = level_info['importance']
        
        # Check if SPX is within tolerance of this level
        if spx_value >= level_value - TOLERANCE and spx_value <= level_value + TOLERANCE:
            level_key = f"resistance_{level_value}"
            if level_key not in last_posted_levels:
                importance_emoji = "🔴" if importance == "high" else "🟡"
                
                # Get nearby upside levels (since we're testing resistance, show what's above)
                nearby_upside = get_nearby_levels(spx_value, levels, "up", 3)
                nearby_text = format_nearby_levels(nearby_upside)
                
                message = f"{importance_emoji} **SPX Resistance Test**: {spx_value:.2f} testing {description} at {level_value}"
                if nearby_text:
                    message += f"\n\n📈 **Next Upside Levels**:\n{nearby_text}"
                
                signals.append({
                    "type": "resistance", 
                    "level": level_value,
                    "message": message,
                    "color": 0xff0000
                })
                last_posted_levels.add(level_key)
    
    # Check for breakouts (when price moves beyond tolerance)
    for level_info in levels["resistance"]:
        level_value = level_info['value']
        description = level_info['description']
        
        if spx_value > level_value + TOLERANCE:
            level_key = f"breakout_up_{level_value}"
            if level_key not in last_posted_levels:
                # Get nearby upside levels for breakout
                nearby_upside = get_nearby_levels(spx_value, levels, "up", 3)
                nearby_text = format_nearby_levels(nearby_upside)
                
                message = f"🚀 **SPX Breakout**: {spx_value:.2f} broke above {description} at {level_value}!"
                if nearby_text:
                    message += f"\n\n📈 **Next Upside Levels**:\n{nearby_text}"
                
                signals.append({
                    "type": "breakout_up",
                    "level": level_value,
                    "message": message,
                    "color": 0x00ff00
                })
                last_posted_levels.add(level_key)
    
    for level_info in levels["support"]:
        level_value = level_info['value']
        description = level_info['description']
        
        if spx_value < level_value - TOLERANCE:
            level_key = f"breakout_down_{level_value}"
            if level_key not in last_posted_levels:
                # Get nearby downside levels for breakdown
                nearby_downside = get_nearby_levels(spx_value, levels, "down", 3)
                nearby_text = format_nearby_levels(nearby_downside)
                
                message = f"📉 **SPX Breakdown**: {spx_value:.2f} broke below {description} at {level_value}!"
                if nearby_text:
                    message += f"\n\n📉 **Next Downside Levels**:\n{nearby_text}"
                
                signals.append({
                    "type": "breakout_down",
                    "level": level_value,
                    "message": message,
                    "color": 0xff0000
                })
                last_posted_levels.add(level_key)
    
    return signals

def clear_old_signals(spx_value, levels):
    """Clear old signals when price moves away from levels"""
    global last_posted_levels
    
    # Clear support signals when price moves up significantly
    for level_info in levels["support"]:
        level_value = level_info['value']
        if spx_value > level_value + 50:
            last_posted_levels.discard(f"support_{level_value}")
            last_posted_levels.discard(f"breakout_down_{level_value}")
    
    # Clear resistance signals when price moves down significantly
    for level_info in levels["resistance"]:
        level_value = level_info['value']
        if spx_value < level_value - 50:
            last_posted_levels.discard(f"resistance_{level_value}")
            last_posted_levels.discard(f"breakout_up_{level_value}")

def monitor_spx():
    """Main monitoring function"""
    print("🤖 Starting SPX CSV Monitor...")
    
    # Ensure levels directory exists
    ensure_levels_directory()
    
    # Test Discord connection first
    if not test_discord_connection():
        print("❌ Discord connection failed. Exiting...")
        return
    
    while True:
        try:
            # Load today's levels
            csv_file = get_todays_levels_file()
            levels = load_levels_from_csv(csv_file)
            
            if not levels["support"] and not levels["resistance"]:
                print("⚠️ No levels loaded. Waiting for levels file...")
                time.sleep(60)
                continue
            
            # Only fetch SPX data during market hours
            if is_market_hours():
                spx_value = get_spx_value()
                
                if spx_value is not None:
                    print(f"📈 Current SPX: {spx_value:.2f}")
                    
                    # Clear old signals
                    clear_old_signals(spx_value, levels)
                    
                    # Analyze for trading signals
                    signals = analyze_spx_levels(spx_value, levels)
                    
                    # Post signals to Discord
                    for signal in signals:
                        post_to_discord(signal["message"], signal["color"])
                        time.sleep(1)  # Small delay between posts
                    
                    # Post regular updates every 10 minutes (optional)
                    current_minute = datetime.now().minute
                    if current_minute % 10 == 0 and datetime.now().second < 30:
                        status_message = f"📊 **SPX Status Update**: {spx_value:.2f} | Time: {datetime.now().strftime('%H:%M:%S')}"
                        post_to_discord(status_message, 0x0099ff)
                else:
                    # Post API status message every 5 minutes when API is unavailable
                    current_minute = datetime.now().minute
                    if current_minute % 5 == 0 and datetime.now().second < 30:
                        status_message = f"⚠️ **API Status**: SPX data temporarily unavailable. Market might be closed or API experiencing issues. | Time: {datetime.now().strftime('%H:%M:%S')}"
                        post_to_discord(status_message, 0xff9900)
            else:
                # Outside market hours - just log status
                pacific_tz = pytz.timezone('US/Pacific')
                now = datetime.now(pacific_tz)
                print(f"🌙 Outside market hours: {now.strftime('%A, %H:%M:%S PT')} - Waiting for market open...")
                
                # Post market status every hour when outside market hours
                current_minute = datetime.now().minute
                if current_minute == 0 and datetime.now().second < 30:
                    status_message = f"🌙 **Market Closed**: Outside trading hours ({now.strftime('%A, %H:%M PT')}). Market opens Mon-Fri 6:30 AM - 1:00 PM PT."
                    post_to_discord(status_message, 0x666666)
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping SPX Monitor...")
            post_to_discord("🛑 SPX CSV Monitor Bot is shutting down.", 0xff9900)
            break
        except Exception as e:
            print(f"❌ Error in monitoring loop: {e}")
            time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    monitor_spx()
