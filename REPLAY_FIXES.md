# Replay Topcon - Code Fixes Summary

## Issues Fixed

### 1. **CSV Delimiter Issue**
- **Problem**: The code was using comma (`,`) as the CSV delimiter, but `final_test.csv` uses semicolons (`;`)
- **Fix**: Updated CSV reader to use `delimiter=';'`

### 2. **Incorrect Column Indices**
- **Problem**: Column indices were wrong for the actual CSV structure
- **Fix**: Updated to correct indices based on CSV header:
  - `DATA_COLUMN_INDEX = 5` (was 6) - Contains hex data
  - `DIRECTION_COLUMN_INDEX = 3` (was 1) - Contains "DOWN" or "UP"
  - Added `FUNCTION_COLUMN_INDEX = 2` - Contains "IRP_MJ_WRITE" or "IRP_MJ_READ"

### 3. **Wrong Direction Filter**
- **Problem**: Code was filtering for "Write" but CSV contains "DOWN" for outgoing data
- **Fix**: Changed `DIRECTION_FILTER = "DOWN"`

### 4. **Missing Function Filter**
- **Problem**: Code wasn't filtering by operation type (WRITE vs READ)
- **Fix**: Added `FUNCTION_FILTER = "IRP_MJ_WRITE"` to only replay write operations

### 5. **Serial Port Code Commented Out**
- **Problem**: Serial port connection code was commented out, so nothing would be sent
- **Fix**: Uncommented the serial port initialization code

## CSV Structure

The `final_test.csv` file has the following structure:
```
#;Time;Function;Direction;Status;Data;Data (chars);Data length;Req. length;Port;Comments;
```

**Column Breakdown:**
- Column 0: Row number (#)
- Column 1: Timestamp
- Column 2: Function (IRP_MJ_WRITE or IRP_MJ_READ)
- Column 3: Direction (DOWN = PC→Device, UP = Device→PC)
- Column 4: Status
- Column 5: Data (hex bytes like "01 72 0d 04")
- Column 6: Data as characters
- Column 7: Data length
- Column 8: Requested length
- Column 9: Port (COM7)
- Column 10: Comments

## What the Script Does Now

1. **Opens COM7** at 9600 baud
2. **Reads `final_test.csv`** with semicolon delimiter
3. **Filters for**:
   - `IRP_MJ_WRITE` operations only (ignores reads)
   - `DOWN` direction only (PC to device, not device responses)
4. **Sends each hex packet** to the device
5. **Reads responses** and displays them
6. **Waits 0.1 seconds** between packets to avoid overwhelming the device

## Example Output

When running, you should see:
```
✅ Connected to COM7 at 9600 baud.
📂 Reading from final_test.csv...
🚀 [Row 2] Sending: 01720D04
    ⬅️  Device Ack: 016572...
🚀 [Row 8] Sending: 01760D50530D04
...
🏁 Replay finished.
```

## Usage

Simply run:
```bash
python replay_topcon.py
```

Make sure:
- The Topcon device is connected to COM7
- You have the `pyserial` library installed: `pip install pyserial`
- `final_test.csv` is in the same directory
