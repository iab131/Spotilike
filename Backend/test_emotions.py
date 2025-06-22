#!/usr/bin/env python3
"""
Test script to demonstrate the new multi-emotion tracking system
"""

import os
from dotenv import load_dotenv
from mongoDB import MongoDBManager

# Load environment variables
load_dotenv()

def test_multi_emotion_tracking():
    """Test the new multi-emotion tracking system"""
    
    connection_string = os.getenv('MONGODB_URI')
    if not connection_string:
        print("❌ MONGODB_URI environment variable not set. Please set it in a .env file.")
        return

    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager(connection_string, "spotilike", "tracks")
        
        if not mongo_manager.connect():
            print("❌ Failed to connect to MongoDB")
            return

        # Clear the collection for testing
        print("🗑️ Clearing collection for fresh test...")
        mongo_manager.drop_collection()

        # Test track ID
        test_track_id = "4cOdK2wGLETOMsV3g9B1rA"  # Example track ID
        
        print("\n=== TESTING MULTI-EMOTION TRACKING ===")
        
        # Test 1: First emotion (happy)
        print("\n1. User is HAPPY with the song")
        mongo_manager.update_track_score(test_track_id, 1, "happy")
        
        # Test 2: Same emotion again (happy)
        print("\n2. User is HAPPY again with the song")
        mongo_manager.update_track_score(test_track_id, 1, "happy")
        
        # Test 3: Different emotion (sad)
        print("\n3. User is SAD with the song")
        mongo_manager.update_track_score(test_track_id, -1, "sad")
        
        # Test 4: Another emotion (angry)
        print("\n4. User is ANGRY with the song")
        mongo_manager.update_track_score(test_track_id, -1, "angry")
        
        # Test 5: Skip the song
        print("\n5. User SKIPS the song")
        mongo_manager.update_track_score(test_track_id, -1, "skipped")
        
        # Test 6: Neutral emotion
        print("\n6. User is NEUTRAL with the song")
        mongo_manager.update_track_score(test_track_id, 0, "neutral")
        
        # Show the final result
        print("\n=== FINAL RESULT ===")
        result = mongo_manager.find_one({'track_id': test_track_id})
        
        if result:
            print(f"Track ID: {result['track_id']}")
            print(f"Total Score: {result.get('total_score', 0)}")
            print("\nEmotion Breakdown:")
            for emotion in ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral', 'skipped']:
                emotion_field = f'emotion_{emotion}'
                count = result.get(emotion_field, 0)
                print(f"  {emotion.capitalize()}: {count}")
        else:
            print("❌ No result found")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    finally:
        if 'mongo_manager' in locals() and mongo_manager.client:
            mongo_manager.disconnect()
            print("\n🔌 Disconnected from MongoDB")

if __name__ == "__main__":
    test_multi_emotion_tracking() 