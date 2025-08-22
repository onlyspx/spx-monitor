from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)

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
        "market_hours": "Mon-Fri 6:30 AM - 1:00 PM PT",
        "features": [
            "CSV-based level monitoring",
            "Discord webhook integration",
            "Market hours awareness",
            "Trading alerts"
        ]
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
