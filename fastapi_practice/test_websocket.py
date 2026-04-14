#!/usr/bin/env python3
"""Test WebSocket endpoint"""

import asyncio
import websockets
import json
import sys

async def test_ws():
    # Token - replace with your actual token
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0dXllbnNpbmhwcm81NEBnbWFpbC5jb20iLCJleHAiOjE3NzYxNTczNzN9.PEbAXhpA0PQyLQpYzNf5kxwNQ12Gb2yTjr_XV76OBBo"
    
    uri = f"ws://localhost:8000/ws?token={TOKEN}"
    
    print(f"[INFO] Connecting to {uri}")
    print()
    
    try:
        async with websockets.connect(uri) as websocket:
            print("[OK] Connected!")
            
            # STEP 1: Receive connection confirmation
            response = await websocket.recv()
            print(f"\n[RECV] Connection confirmation:")
            print(f"  {response}")
            
            # STEP 2: Send subscribe message
            subscribe_msg = {"action": "subscribe", "task_id": 10}
            print(f"\n[SEND] Subscribe message:")
            print(f"  {json.dumps(subscribe_msg)}")
            
            await websocket.send(json.dumps(subscribe_msg))
            
            # STEP 3: Receive subscription confirmation
            response = await websocket.recv()
            print(f"\n[RECV] Subscription confirmation:")
            print(f"  {response}")
            
            print("\n[SUCCESS] WebSocket working!")
            print("\nNext: Open another terminal and run:")
            print("  curl -X PUT http://localhost:8000/tasks/1 \\")
            print("    -H 'Content-Type: application/json' \\")
            print("    -H 'Authorization: Bearer YOUR_TOKEN' \\")
            print("    -d '{\"title\": \"Updated\", \"status\": \"in_progress\"}'")
            print("\nYou should see the update message here ^")
            
            # Wait for broadcast (optional - listen for task updates)
            print("\n[LISTENING] Waiting for task updates... (press Ctrl+C to exit)")
            try:
                while True:
                    msg = await websocket.recv()
                    print(f"\n[RECV] Task update:")
                    print(f"  {msg}")
            except KeyboardInterrupt:
                print("\n\n[INFO] Disconnecting...")
                
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print(f"\nDebug:")
        print(f"  - Is server running? (uvicorn app.main:app --reload)")
        print(f"  - Is token valid? (Login first)")
        print(f"  - Is task_id=1 valid? (Create a task first)")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_ws())
