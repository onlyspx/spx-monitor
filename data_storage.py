import os
import csv
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class DataStorage:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # CSV file paths
        self.spy_1min_file = self.data_dir / "spy_1min.csv"
        self.ma_signals_file = self.data_dir / "ma_signals.csv"
        
        # Initialize CSV files with headers if they don't exist
        self._init_csv_files()
    
    def _init_csv_files(self):
        """Initialize CSV files with headers if they don't exist"""
        
        # SPY 1-minute data
        if not self.spy_1min_file.exists():
            with open(self.spy_1min_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # MA signals data
        if not self.ma_signals_file.exists():
            with open(self.ma_signals_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'price', 'trend', 'signal', 'ma_50_ema', 'ma_50_sma', 'ma_200_ema', 'ma_200_sma'])
    
    def append_spy_data(self, data_point):
        """Append new SPY data point to CSV"""
        try:
            with open(self.spy_1min_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    data_point['timestamp'],
                    data_point['open'],
                    data_point['high'],
                    data_point['low'],
                    data_point['close'],
                    data_point['volume']
                ])
            print(f"✅ Appended SPY data: {data_point['timestamp']}")
            return True
        except Exception as e:
            print(f"❌ Error appending SPY data: {e}")
            return False
    
    def append_ma_signal(self, signal_data):
        """Append new MA signal to CSV"""
        try:
            with open(self.ma_signals_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    signal_data['timestamp'],
                    signal_data['price'],
                    signal_data['trend'],
                    signal_data['signal'],
                    signal_data['ma_50_ema'],
                    signal_data['ma_50_sma'],
                    signal_data['ma_200_ema'],
                    signal_data['ma_200_sma']
                ])
            print(f"✅ Appended MA signal: {signal_data['trend']}")
            return True
        except Exception as e:
            print(f"❌ Error appending MA signal: {e}")
            return False
    
    def get_historical_data(self, days=30):
        """Get historical data for MA calculations"""
        try:
            data = []
            with open(self.spy_1min_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append({
                        'timestamp': row['timestamp'],
                        'close': float(row['close']),
                        'volume': int(row['volume'])
                    })
            
            # Filter by days if specified
            if days:
                cutoff_date = datetime.now() - timedelta(days=days)
                data = [d for d in data if datetime.fromisoformat(d['timestamp']) >= cutoff_date]
            
            print(f"✅ Retrieved {len(data)} historical data points")
            return data
        except Exception as e:
            print(f"❌ Error reading historical data: {e}")
            return []
    
    def commit_and_push(self, message="Auto-commit: Update data files"):
        """Commit and push changes to GitHub"""
        try:
            # Check if we have changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd='.')
            
            if not result.stdout.strip():
                print("📝 No changes to commit")
                return True
            
            # Add files
            subprocess.run(['git', 'add', 'data/'], check=True, cwd='.')
            
            # Commit
            subprocess.run(['git', 'commit', '-m', message], check=True, cwd='.')
            
            # Push
            subprocess.run(['git', 'push'], check=True, cwd='.')
            
            print(f"✅ Successfully committed and pushed: {message}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Error in git operations: {e}")
            return False
    
    def get_file_stats(self):
        """Get statistics about stored data"""
        stats = {}
        
        try:
            # SPY data stats
            if self.spy_1min_file.exists():
                with open(self.spy_1min_file, 'r') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    stats['spy_data_points'] = len(rows) - 1  # Subtract header
                    if len(rows) > 1:
                        stats['spy_first_date'] = rows[1][0]
                        stats['spy_last_date'] = rows[-1][0]
            
            # MA signals stats
            if self.ma_signals_file.exists():
                with open(self.ma_signals_file, 'r') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    stats['ma_signals'] = len(rows) - 1  # Subtract header
                    if len(rows) > 1:
                        stats['ma_first_date'] = rows[1][0]
                        stats['ma_last_date'] = rows[-1][0]
            
        except Exception as e:
            print(f"❌ Error getting file stats: {e}")
        
        return stats

# Global instance
data_storage = DataStorage()
