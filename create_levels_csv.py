import csv
import os
from datetime import date
from pathlib import Path

def create_levels_csv():
    """Interactive script to create a CSV file for daily levels"""
    
    # Ensure levels directory exists
    LEVELS_DIR = "levels"
    Path(LEVELS_DIR).mkdir(exist_ok=True)
    
    # Get today's date
    today = date.today().strftime("%Y_%m_%d")
    csv_file = os.path.join(LEVELS_DIR, f"levels_{today}.csv")
    
    print(f"📅 Creating levels CSV for {today}")
    print(f"📁 File will be saved as: {csv_file}")
    print("\n" + "="*50)
    
    levels = []
    
    print("\n🟢 **SUPPORT LEVELS**")
    print("Enter support levels (press Enter when done):")
    
    while True:
        try:
            level_input = input("\nSupport level (or press Enter to finish): ").strip()
            if not level_input:
                break
                
            level_value = float(level_input)
            description = input("Description: ").strip()
            importance = input("Importance (high/medium/low): ").strip().lower()
            
            if importance not in ['high', 'medium', 'low']:
                importance = 'medium'
            
            levels.append({
                'level_type': 'support',
                'level_value': level_value,
                'description': description,
                'importance': importance
            })
            
        except ValueError:
            print("❌ Invalid number. Please try again.")
        except KeyboardInterrupt:
            print("\n\n🛑 Cancelled by user.")
            return
    
    print("\n🔴 **RESISTANCE LEVELS**")
    print("Enter resistance levels (press Enter when done):")
    
    while True:
        try:
            level_input = input("\nResistance level (or press Enter to finish): ").strip()
            if not level_input:
                break
                
            level_value = float(level_input)
            description = input("Description: ").strip()
            importance = input("Importance (high/medium/low): ").strip().lower()
            
            if importance not in ['high', 'medium', 'low']:
                importance = 'medium'
            
            levels.append({
                'level_type': 'resistance',
                'level_value': level_value,
                'description': description,
                'importance': importance
            })
            
        except ValueError:
            print("❌ Invalid number. Please try again.")
        except KeyboardInterrupt:
            print("\n\n🛑 Cancelled by user.")
            return
    
    # Write to CSV
    if levels:
        try:
            with open(csv_file, 'w', newline='') as file:
                fieldnames = ['level_type', 'level_value', 'description', 'importance']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for level in levels:
                    writer.writerow(level)
            
            print(f"\n✅ Successfully created {csv_file}")
            print(f"📊 Total levels: {len(levels)}")
            
            # Show summary
            support_count = len([l for l in levels if l['level_type'] == 'support'])
            resistance_count = len([l for l in levels if l['level_type'] == 'resistance'])
            
            print(f"🟢 Support levels: {support_count}")
            print(f"🔴 Resistance levels: {resistance_count}")
            
        except Exception as e:
            print(f"❌ Error creating CSV file: {e}")
    else:
        print("❌ No levels entered. CSV file not created.")

def quick_create_from_text():
    """Quick create from pasted text analysis"""
    print("📝 Quick Create from Text Analysis")
    print("Paste your market analysis text and I'll help extract levels.")
    print("(This is a placeholder - you can manually create the CSV or use the interactive mode)")
    
    # For now, just show the format
    print("\n📋 CSV Format:")
    print("level_type,level_value,description,importance")
    print("support,6295,Major dip buy level,high")
    print("resistance,6430,POLR upside target,high")

if __name__ == "__main__":
    print("🎯 SPX Levels CSV Creator")
    print("="*30)
    
    choice = input("Choose mode:\n1. Interactive mode\n2. Quick create from text\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        create_levels_csv()
    elif choice == "2":
        quick_create_from_text()
    else:
        print("❌ Invalid choice. Running interactive mode...")
        create_levels_csv()
