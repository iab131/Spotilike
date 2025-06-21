from spotipy.oauth2 import SpotifyOAuth
import spotipy
from dotenv import load_dotenv
import os
import time
from datetime import datetime, timedelta
from mongoDB import MongoDBManager

# Global variables to track previous track and timestamp
previous_track_id = None
previous_timestamp = None
skip_threshold_seconds = 30  # Consider it a skip if track changes within 30 seconds
mongo_manager = None

def auth():
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # Check if environment variables are loaded
    if not client_id or not client_secret:
        print("Error: CLIENT_ID and CLIENT_SECRET must be set in .env file")
        return
    
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri='https://linhong.dev',
        scope='user-read-playback-state playlist-modify-public playlist-modify-private'
    ))

    
def getCurr(sp):
    current = sp.current_playback()
    
    if current is None or current.get('item') is None:
        print("No track currently playing")
        return None
        
    track_id = current['item']['id']
    print(f"Currently playing track ID: {track_id}")
    return track_id

def check_skip(sp):
    """
    Check if the current track was skipped by comparing with previous track
    Returns True if a skip is detected, False otherwise
    """
    global previous_track_id, previous_timestamp
    
    current = sp.current_playback()
    
    if current is None or current.get('item') is None:
        return False
    
    current_track_id = current['item']['id']
    current_timestamp = datetime.now()
    
    # If this is the first time checking, just store the current track
    if previous_track_id is None:
        previous_track_id = current_track_id
        previous_timestamp = current_timestamp
        return False
    
    # If track has changed
    if current_track_id != previous_track_id:
        # Calculate time difference
        if previous_timestamp:
            time_diff = (current_timestamp - previous_timestamp).total_seconds()
            
            # If the track changed within the skip threshold, consider it a skip
            if time_diff < skip_threshold_seconds:
                print(f"Skip detected! Track changed from {previous_track_id} to {current_track_id} after {time_diff:.1f} seconds")
                previous_track_id = current_track_id
                previous_timestamp = current_timestamp
                return True
            else:
                print(f"Track changed naturally from {previous_track_id} to {current_track_id} after {time_diff:.1f} seconds")
        else:
            # This case handles the very first track change where previous_timestamp might be None
            # but previous_track_id is set.
            print(f"Track changed from {previous_track_id} to {current_track_id}")
    
    # Update previous track info
    previous_track_id = current_track_id
    previous_timestamp = current_timestamp
    return False

def skipped():
    """
    Wrapper function to check for skips - can be called from main
    """
    try:
        sp = auth()
        return check_skip(sp)
    except Exception as e:
        print(f"Error checking for skips: {e}")
        return False

def initDB():
    global mongo_manager
    connection_string = os.getenv('MONGODB_URI')
    if not connection_string:
        print("❌ MONGODB_URI environment variable not set. Please set it in a .env file.")
        return None
    mongo_manager = MongoDBManager(connection_string, "spotilike", "tracks")
    if not mongo_manager.connect():
        return None
    return mongo_manager

def addDB(track_id, score):
    if mongo_manager:
        mongo_manager.update_track_score(track_id, score)

def runModel():
    # Placeholder for model execution
    return "happy"

def main():
    if not initDB():
        print("Failed to initialize database connection. Exiting.")
        return

    while True:
        try:
            sp = auth()
            curr = getCurr(sp)
            print(curr)
            if curr != None:
                res = "sad"
                res = runModel()
                if res == "happy":
                    addDB(curr, 1)
                
                # We need to re-auth here because check_skip creates its own sp instance
                # which might be different. A better approach would be to pass the sp object.
                sp_for_skip = auth()
                if check_skip(sp_for_skip):
                    addDB(curr, -1)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()