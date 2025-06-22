#!/usr/bin/env python3
"""
Test script to verify skip detection is working
"""

import os
import time
from dotenv import load_dotenv
from main import auth, getCurr, check_skip, initDB, addDB

# Load environment variables
load_dotenv()

def test_skip_detection():
    """Test the skip detection functionality"""
    
    print("🧪 Testing skip detection...")
    
    # Initialize database
    if not initDB():
        print("❌ Failed to initialize database")
        return
    
    print("✅ Database initialized")
    
    # Get Spotify client
    sp = auth()
    if not sp:
        print("❌ Failed to authenticate with Spotify")
        return
    
    print("✅ Spotify authenticated")
    
    # Get current track
    curr = getCurr(sp)
    if not curr:
        print("❌ No track currently playing")
        return
    
    print(f"🎵 Current track: {curr}")
    
    # Test skip detection
    print("\n🔍 Testing skip detection...")
    print("📝 Instructions:")
    print("1. Skip the current song in Spotify")
    print("2. Wait for the detection...")
    
    # Check for skips multiple times
    for i in range(10):
        print(f"\n--- Check #{i+1} ---")
        skip_detected = check_skip(sp)
        print(f"Skip detected: {skip_detected}")
        
        if skip_detected:
            print("🎉 SKIP DETECTED! Adding to database...")
            addDB(curr, -1, "skipped")
            print("✅ Skip added to database!")
            break
        
        time.sleep(2)  # Wait 2 seconds between checks
    
    print("\n🧪 Test completed!")

if __name__ == "__main__":
    test_skip_detection() 