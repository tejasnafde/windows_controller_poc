#!/usr/bin/env python3
"""
Test WebSocket Connection to Relay Server

This script tests if your relay server is running and accepting connections.
"""

import asyncio
import websockets
import sys

# Your relay server URL
SERVER_URL = 'ws://34.63.226.183:8765'

async def test_connection():
    """Test connection to relay server."""
    print("=" * 60)
    print("WebSocket Connection Test")
    print("=" * 60)
    print(f"\nServer URL: {SERVER_URL}")
    print("\nAttempting to connect...")
    
    try:
        # Try to connect (with overall timeout)
        async with asyncio.timeout(10):
            async with websockets.connect(SERVER_URL) as websocket:
                print("✓ Connected successfully!")
                print(f"  Connection established to {SERVER_URL}")
            
                # Send a test message
                print("\nSending test message...")
                test_message = {
                    'type': 'test',
                    'message': 'Hello from test script'
                }
                
                import json
                await websocket.send(json.dumps(test_message))
                print("✓ Message sent")
                
                # Try to receive a response (with timeout)
                print("\nWaiting for response (5 seconds)...")
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"✓ Received response: {response}")
                except asyncio.TimeoutError:
                    print("⚠️  No response received (this is normal for relay server)")
                    print("   The server is running but waiting for proper client registration")
                
                print("\n" + "=" * 60)
                print("✅ CONNECTION TEST PASSED!")
                print("=" * 60)
                print("\nYour relay server is running and accepting connections.")
                print("\nNext steps:")
                print("  1. Start Windows client: python windows_client_websocket.py")
                print("  2. Run controller: python brain_example.py")
                
                return True
            
    except asyncio.TimeoutError:
        print("❌ Connection timeout!")
        print("\nPossible issues:")
        print("  1. Server is not running")
        print("  2. Firewall is blocking port 8765")
        print("  3. Wrong IP address")
        print("\nCheck server status:")
        print(f"  ./check_server_status.sh")
        return False
        
    except ConnectionRefusedError:
        print("❌ Connection refused!")
        print("\nThe server is not accepting connections.")
        print("\nCheck if server is running:")
        print("  gcloud compute ssh relay-server --zone=us-central1-a \\")
        print("    --command='sudo systemctl status relay-server'")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"\nError type: {type(e).__name__}")
        print("\nTroubleshooting:")
        print("  1. Check if server is running: ./check_server_status.sh")
        print("  2. Check firewall rules:")
        print("     gcloud compute firewall-rules list --filter='name~websocket'")
        print("  3. Check server logs:")
        print("     gcloud compute ssh relay-server --zone=us-central1-a \\")
        print("       --command='sudo journalctl -u relay-server -n 50'")
        return False

if __name__ == '__main__':
    try:
        result = asyncio.run(test_connection())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
