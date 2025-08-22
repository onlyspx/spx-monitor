# SPX Monitor

A simple Python application that monitors the S&P 500 (SPX) index and announces its current value using text-to-speech.

## How It Works

This application fetches real-time SPX data from an external API and announces the current value every 20 seconds using macOS's built-in text-to-speech functionality.

### Key Components

1. **Data Source**: Fetches SPX data from `https://api.0dtespx.com/aggregateData`
2. **Data Processing**: Extracts the latest SPX value from the API response
3. **Text-to-Speech**: Uses macOS `say` command to announce the current SPX value
4. **Continuous Monitoring**: Runs in a loop, checking every 20 seconds

### Features

- **Real-time Monitoring**: Continuously fetches live SPX data
- **Smart Number Formatting**: Formats 4-digit SPX values for better pronunciation (e.g., "5943" becomes "59 43")
- **Error Handling**: Gracefully handles API errors and network issues
- **Voice Announcements**: Uses macOS text-to-speech to announce values

## Files

- `say.py` - Main application that monitors and announces SPX values using text-to-speech
- `csv_spx_monitor.py` - **Main**: Generic CSV-based Discord bot that reads daily levels from CSV files
- `create_levels_csv.py` - Utility script to create CSV files for daily levels
- `test_api.py` - Utility script to test the API connection and view raw data
- `test_discord.py` - Test script to verify Discord webhook functionality
- `requirements.txt` - Python dependencies
- `levels/` - Directory containing daily CSV files with SPX levels

## Installation

1. **Clone or download the project**
2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the main application:
```bash
python say.py
```

This will start the continuous monitoring and announcement system.

### Test the API connection:
```bash
python test_api.py
```

This will fetch and display the raw API response to verify connectivity.

### Test Discord webhook:
```bash
python test_discord.py
```

This will send test messages to your Discord channel to verify the webhook is working.

### Run CSV-based SPX Monitor:
```bash
python csv_spx_monitor.py
```

This will start the CSV-based monitor that reads daily levels from CSV files.

### Create Daily Levels CSV:
```bash
python create_levels_csv.py
```

This will help you create CSV files for daily SPX levels interactively.

## API Details

The application uses the following API endpoint:
```
https://api.0dtespx.com/aggregateData?series=spx,spxExpectedMove&date=live&interval=30
```

The API returns a list of data points, and the application extracts the latest SPX value from the most recent entry.

## Requirements

- Python 3.x
- macOS (for text-to-speech functionality)
- Internet connection
- `requests` library

## Discord Trading Bot Features

The CSV-based monitor (`csv_spx_monitor.py`) includes:

- **Daily Level Management**: Reads levels from CSV files organized by date
- **Generic Design**: Works with any daily levels without code changes
- **+/- 5 Point Tolerance**: Tests levels within 5 points of each level
- **Importance Indicators**: High/medium/low importance levels with different emojis
- **Rich Descriptions**: Each level includes detailed descriptions
- **Anti-Spam Protection**: Prevents duplicate alerts for the same level
- **Rich Embeds**: Beautiful Discord messages with colors and formatting
- **Status Updates**: Regular updates every 10 minutes
- **Market Hours**: Only monitors during trading hours (Mon-Fri, 6:30 AM - 1:00 PM PT)

### CSV File Format

Daily levels are stored in `levels/levels_YYYY_MM_DD.csv`:

```csv
level_type,level_value,description,importance
support,6295,Major dip buy level,high
support,6375,Key pivot level,high
resistance,6430,POLR upside target,high
```

## Deployment Options

### Local Deployment

To keep the SPX monitor running continuously on your local machine:

### Option 1: Run in Background (Simple)
```bash
source venv/bin/activate && python csv_spx_monitor.py
```
Then press `Ctrl+Z` to suspend, then `bg` to run in background.

### Option 2: Use nohup (Recommended for Long-term)
```bash
source venv/bin/activate && nohup python csv_spx_monitor.py > spx_monitor.log 2>&1 &
```
This will:
- Run the script in the background
- Keep it running even if you close the terminal
- Save all output to `spx_monitor.log`

### Option 3: Use screen/tmux (Best for Monitoring)
```bash
# Install screen if not available
brew install screen

# Start a new screen session
screen -S spx_monitor

# In the screen session, run:
source venv/bin/activate && python csv_spx_monitor.py

# Detach from screen: Ctrl+A, then D
# Reattach later: screen -r spx_monitor
```

### Option 4: System Service (Most Professional)
```bash
# Copy the plist file to the right location
cp com.spx.monitor.plist ~/Library/LaunchAgents/

# Load the service
launchctl load ~/Library/LaunchAgents/com.spx.monitor.plist

# Start the service
launchctl start com.spx.monitor
```

### Check if Monitor is Running
```bash
# Check processes
ps aux | grep csv_spx_monitor

# Check logs
tail -f spx_monitor.log

# Check Discord for bot messages
```

### Stop the Monitor
```bash
# If using nohup
pkill -f csv_spx_monitor

# If using system service
launchctl stop com.spx.monitor
launchctl unload ~/Library/LaunchAgents/com.spx.monitor.plist

# If running in terminal
Ctrl+C
```

### Cloud Deployment (Recommended)

For 24/7 monitoring without keeping your computer on, deploy to the cloud:

#### Railway (Easiest - Recommended)
1. **Sign up** at [railway.app](https://railway.app)
2. **Connect your GitHub repo**
3. **Deploy automatically** - Railway will detect the Python app
4. **Set environment variables** (if needed):
   - `DISCORD_WEBHOOK_URL`: Your Discord webhook URL
5. **Monitor logs** in Railway dashboard

#### Render (Great Free Option)
1. **Sign up** at [render.com](https://render.com)
2. **Create new Web Service**
3. **Connect GitHub repo**
4. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python csv_spx_monitor.py`
5. **Deploy**

#### Heroku (Production Ready)
1. **Sign up** at [heroku.com](https://heroku.com)
2. **Install Heroku CLI**
3. **Deploy**:
   ```bash
   heroku create your-spx-monitor
   git push heroku main
   heroku ps:scale worker=1
   ```

#### AWS Lambda (Serverless)
1. **Create Lambda function**
2. **Upload code as ZIP**
3. **Set up EventBridge** for scheduled execution
4. **Configure environment variables**

### Environment Variables for Cloud
If deploying to cloud, you may need to set these environment variables:
- `DISCORD_WEBHOOK_URL`: Your Discord webhook URL
- `API_URL`: SPX API endpoint (optional, has default)
- `TOLERANCE`: Level tolerance in points (optional, default 5)

## Notes

- The applications run indefinitely until manually stopped (Ctrl+C)
- SPX values are announced every 20 seconds (text-to-speech) or 30 seconds (Discord)
- 4-digit SPX values are formatted with a space for better pronunciation
- The applications include comprehensive error handling for network and API issues
- Discord webhook URL is configured for your specific channel
- CSV monitor uses +/- 5 point tolerance around each level
- API returns 204 status when market is closed (handled gracefully)
