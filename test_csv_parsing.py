#!/usr/bin/env python3
"""
Test script to verify CSV parsing without connecting to serial port
"""
import csv

CSV_FILE = 'final_test.csv'
DATA_COLUMN_INDEX = 5
FUNCTION_COLUMN_INDEX = 2
DIRECTION_COLUMN_INDEX = 3
FUNCTION_FILTER = "IRP_MJ_WRITE"
DIRECTION_FILTER = "DOWN"

def clean_hex_string(hex_str):
    """Converts a string like "02 43 53" into raw bytes."""
    clean = hex_str.replace(" ", "").replace("0x", "").replace(",", "").replace("\n", "")
    try:
        return bytes.fromhex(clean)
    except ValueError:
        return None

print(f"📂 Testing CSV parsing from {CSV_FILE}...")
print(f"Looking for: {FUNCTION_FILTER} operations going {DIRECTION_FILTER}\n")

count = 0
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    next(reader, None)  # Skip header
    
    for row_num, row in enumerate(reader, start=1):
        if not row:
            continue
        
        # Filter by function
        if len(row) > FUNCTION_COLUMN_INDEX:
            function = row[FUNCTION_COLUMN_INDEX]
            if FUNCTION_FILTER.lower() not in function.lower():
                continue
        
        # Filter by direction
        if len(row) > DIRECTION_COLUMN_INDEX:
            direction = row[DIRECTION_COLUMN_INDEX]
            if DIRECTION_FILTER.lower() not in direction.lower():
                continue
        
        # Extract data
        if len(row) > DATA_COLUMN_INDEX:
            raw_data = row[DATA_COLUMN_INDEX]
            packet = clean_hex_string(raw_data)
            
            if packet:
                count += 1
                if count <= 10:  # Show first 10
                    print(f"✅ [Row {row_num}] Would send: {packet.hex().upper()} ({len(packet)} bytes)")

print(f"\n📊 Total packets to send: {count}")
print("✅ CSV parsing test completed successfully!")
