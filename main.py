from spotipy.oauth2 import SpotifyOAuth
import spotipy
from dotenv import load_dotenv
import os
import time
from datetime import datetime, timedelta

# Global variables to track previous track and timestamp
previous_track_id = None
previous_timestamp = None
skip_threshold_seconds = 30  # Consider it a skip if track changes within 30 seconds

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
        time_diff = (current_timestamp - previous_timestamp).total_seconds()
        
        # If the track changed within the skip threshold, consider it a skip
        if time_diff < skip_threshold_seconds:
            print(f"Skip detected! Track changed from {previous_track_id} to {current_track_id} after {time_diff:.1f} seconds")
            previous_track_id = current_track_id
            previous_timestamp = current_timestamp
            return True
        else:
            print(f"Track changed naturally from {previous_track_id} to {current_track_id} after {time_diff:.1f} seconds")
    
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

def main():
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
                if check_skip(sp):
                    addDB(curr, -1)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()