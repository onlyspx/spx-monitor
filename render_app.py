import threading
import time
from flask import Flask
from datetime import datetime
import pytz
import csv_spx_monitor

app = Flask(__name__)

# Global flag to track if SPX monitor is running
spx_monitor_running = False

@app.route('/')
def health_check():
    """Health check endpoint for Render.com"""
    pacific_tz = pytz.timezone('US/Pacific')
    now = datetime.now(pacific_tz)
    
    return {
        "status": "healthy",
        "service": "SPX Monitor Bot",
        "timestamp": now.isoformat(),
        "timezone": "US/Pacific",
        "spx_monitor_status": "running" if spx_monitor_running else "starting",
        "message": "SPX Monitor is running and monitoring market levels"
    }

@app.route('/health')
def detailed_health():
    """Detailed health check endpoint"""
    pacific_tz = pytz.timezone('US/Pacific')
    now = datetime.now(pacific_tz)
    
    return {
        "status": "healthy",
        "service": "SPX Monitor Bot",
        "timestamp": now.isoformat(),
        "timezone": "US/Pacific",
        "spx_monitor_status": "running" if spx_monitor_running else "starting",
        "market_hours": "Mon-Fri 6:30 AM - 1:00 PM PT",
        "features": [
            "CSV-based level monitoring",
            "Discord webhook integration",
            "Market hours awareness",
            "Trading alerts"
        ]
    }

def run_spx_monitor():
    """Run the SPX monitor in a separate thread"""
    global spx_monitor_running
    try:
        spx_monitor_running = True
        csv_spx_monitor.monitor_spx()
    except Exception as e:
        print(f"SPX Monitor error: {e}")
        spx_monitor_running = False

def start_spx_monitor():
    """Start SPX monitor in background thread"""
    spx_thread = threading.Thread(target=run_spx_monitor, daemon=True)
    spx_thread.start()
    return spx_thread

if __name__ == '__main__':
    # Start SPX monitor in background
    print("🚀 Starting SPX Monitor in background...")
    spx_thread = start_spx_monitor()
    
    # Give SPX monitor a moment to start
    time.sleep(2)
    
    # Start Flask app
    print("🌐 Starting Flask health check server...")
    app.run(host='0.0.0.0', port=10000, debug=False)
