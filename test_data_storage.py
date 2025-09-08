#!/usr/bin/env python3
"""
Test script for data storage and git operations
"""

import os
from datetime import datetime
from data_storage import data_storage

def test_data_storage():
    """Test the data storage functionality"""
    print("🧪 Testing Data Storage System")
    print("=" * 50)
    
    # Test 1: Check if data directory exists
    print("1. Checking data directory...")
    if data_storage.data_dir.exists():
        print("✅ Data directory exists")
    else:
        print("❌ Data directory not found")
        return
    
    # Test 2: Check if CSV files exist
    print("\n2. Checking CSV files...")
    if data_storage.spy_1min_file.exists():
        print("✅ SPY 1-minute data file exists")
    else:
        print("❌ SPY 1-minute data file not found")
    
    if data_storage.ma_signals_file.exists():
        print("✅ MA signals file exists")
    else:
        print("❌ MA signals file not found")
    
    # Test 3: Add sample data
    print("\n3. Adding sample data...")
    sample_data = {
        'timestamp': datetime.now().isoformat(),
        'open': 647.24,
        'high': 647.50,
        'low': 646.80,
        'close': 647.10,
        'volume': 1000000
    }
    
    if data_storage.append_spy_data(sample_data):
        print("✅ Sample SPY data added")
    else:
        print("❌ Failed to add sample SPY data")
    
    # Test 4: Add sample MA signal
    print("\n4. Adding sample MA signal...")
    sample_signal = {
        'timestamp': datetime.now().isoformat(),
        'price': 647.10,
        'trend': 'BULLISH',
        'signal': 'Price above all MAs',
        'ma_50_ema': 646.50,
        'ma_50_sma': 646.30,
        'ma_200_ema': 645.80,
        'ma_200_sma': 645.60
    }
    
    if data_storage.append_ma_signal(sample_signal):
        print("✅ Sample MA signal added")
    else:
        print("❌ Failed to add sample MA signal")
    
    # Test 5: Get file statistics
    print("\n5. File statistics...")
    stats = data_storage.get_file_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test 6: Test git operations (if in a git repo)
    print("\n6. Testing git operations...")
    try:
        import subprocess
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository detected")
            
            # Check if we have changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                print("📝 Changes detected, ready to commit")
            else:
                print("📝 No changes to commit")
        else:
            print("❌ Not in a git repository")
    except Exception as e:
        print(f"❌ Git test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Data storage test completed!")

if __name__ == "__main__":
    test_data_storage()
