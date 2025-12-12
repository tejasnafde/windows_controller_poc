import csv
import time
import serial
import binascii

# ================= CONFIGURATION =================
# 1. Your Serial Port Settings (Match what you saw in the Sniffer)
SERIAL_PORT = 'COM7'  # Change to your actual port
BAUD_RATE = 9600      # Topcon standard is usually 9600
TIMEOUT = 1           # Seconds to wait for a response

# 2. CSV Settings
CSV_FILE = 'final_test.csv'

# CSV Format: Columns are separated by semicolons (;)
# Header: #;Time;Function;Direction;Status;Data;Data (chars);Data length;Req. length;Port;Comments;
# Column indices (0-based):
# 0: # (row number)
# 1: Time
# 2: Function (IRP_MJ_WRITE, IRP_MJ_READ)
# 3: Direction (DOWN, UP)
# 4: Status
# 5: Data (hex bytes)

DATA_COLUMN_INDEX = 5  # The "Data" column with hex bytes
FUNCTION_COLUMN_INDEX = 2  # The "Function" column
DIRECTION_COLUMN_INDEX = 3  # The "Direction" column

# Only replay IRP_MJ_WRITE operations going DOWN (from PC to device)
FUNCTION_FILTER = "IRP_MJ_WRITE"
DIRECTION_FILTER = "DOWN"

# =================================================

def clean_hex_string(hex_str):
    """
    Converts a string like "02 43 53" or "0x02, 0x43" into raw bytes.
    """
    # Remove common separators and prefixes
    clean = hex_str.replace(" ", "").replace("0x", "").replace(",", "").replace("\n", "")
    try:
        return bytes.fromhex(clean)
    except ValueError:
        return None

def main():
    try:
        # Open Serial Connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        print(f"✅ Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    except serial.SerialException as e:
        print(f"❌ Could not open port {SERIAL_PORT}: {e}")
        return

    print(f"📂 Reading from {CSV_FILE}...")
    
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')  # CSV uses semicolons as delimiters
        
        # Skip header if exists (Comment out if no header)
        next(reader, None) 

        for row_num, row in enumerate(reader, start=1):
            if not row: continue # Skip empty rows
            time.sleep(1)
            # 1. Filter Check - Only process IRP_MJ_WRITE operations going DOWN
            if FUNCTION_COLUMN_INDEX is not None:
                if len(row) > FUNCTION_COLUMN_INDEX:
                    function = row[FUNCTION_COLUMN_INDEX]
                    if FUNCTION_FILTER.lower() not in function.lower():
                        # print(f"⏭️  Skipping Row {row_num} (Function: {function})")
                        continue
            
            if DIRECTION_COLUMN_INDEX is not None:
                if len(row) > DIRECTION_COLUMN_INDEX:
                    direction = row[DIRECTION_COLUMN_INDEX]
                    if DIRECTION_FILTER.lower() not in direction.lower():
                        # print(f"⏭️  Skipping Row {row_num} (Direction: {direction})")
                        continue

            # 2. Extract Data
            if len(row) > DATA_COLUMN_INDEX:
                raw_data = row[DATA_COLUMN_INDEX]
                packet = clean_hex_string(raw_data)
                
                if packet:
                    print(f"🚀 [Row {row_num}] Sending: {packet.hex().upper()}")
                    
                    # SEND THE PACKET
                    ser.write(packet)
                    
                    # Optional: Read response to clear buffer (prevents clogging)
                    response = ser.read_all()
                    if response:
                        print(f"    ⬅️  Device Ack: {response.hex().upper()}")
                    
                    # Crucial: Small delay so we don't choke the hardware
                    time.sleep(0.2) 
                else:
                    print(f"⚠️  [Row {row_num}] Could not parse hex: {raw_data}")
            else:
                print(f"⚠️  [Row {row_num}] Column index out of range.")


    ser.close()
    print("\n🏁 Replay finished.")

if __name__ == "__main__":
    main()