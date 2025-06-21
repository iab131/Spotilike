from spotipy.oauth2 import SpotifyOAuth
import spotipy
from dotenv import load_dotenv
import os
import time
import threading
import cv2
import numpy as np
from deepface import DeepFace
from datetime import datetime, timedelta
from mongoDB import MongoDBManager

# Global variables to track previous track and timestamp
previous_track_id = None
previous_timestamp = None
skip_threshold_seconds = 30  # Consider it a skip if track changes within 30 seconds
mongo_manager = None

# Globals for webcam and emotion detection
webcam_active = False
webcam_thread = None
current_emotion = None
emotion_lock = threading.Lock()
positive_emotions = ['happy']
negative_emotions = ['angry', 'disgust', 'sad']
neutral_emotions = ['neutral']

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
        scope='user-read-playback-state user-modify-playback-state playlist-modify-public playlist-modify-private streaming'
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

def addDB(track_id, score, emotion="neutral"):
    if mongo_manager:
        # Only add if the track does not already exist
        existing = mongo_manager.find_one({'track_id': track_id})
        if not existing:
            mongo_manager.update_track_score(track_id, score, emotion)
        else:
            print(f"Track {track_id} already scored, skipping update.")

def start_webcam():
    """Start the webcam and emotion detection in a separate thread"""
    global webcam_active, webcam_thread, current_emotion
    
    if webcam_active:
        print("Webcam is already active")
        return
    
    webcam_active = True
    webcam_thread = threading.Thread(target=webcam_emotion_detection, daemon=True)
    webcam_thread.start()
    print("Webcam started for emotion detection")

def stop_webcam():
    """Stop the webcam thread"""
    global webcam_active
    webcam_active = False
    if webcam_thread:
        webcam_thread.join(timeout=2.0)
    print("Webcam stopped")

def webcam_emotion_detection():
    """Function to run in a thread for continuous emotion detection"""
    global webcam_active, current_emotion
    
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            webcam_active = False
            return

        # Process at regular intervals to avoid high CPU usage
        process_interval = 1.0  # Process every 1 second
        last_process_time = time.time()
        
        while webcam_active:
            ret, frame = cap.read()
            if not ret:
                break
                
            current_time = time.time()
            # Only process frames at specified intervals
            if current_time - last_process_time > process_interval:
                try:
                    # Analyze emotions
                    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    
                    # Extract the dominant emotion
                    if isinstance(result, list) and len(result) > 0:
                        detected_emotion = result[0].get('dominant_emotion', 'neutral')
                    elif isinstance(result, dict):
                        detected_emotion = result.get('dominant_emotion', 'neutral')
                    else:
                        detected_emotion = 'neutral'
                    
                    # Update current emotion with thread safety
                    with emotion_lock:
                        current_emotion = detected_emotion
                        
                    print(f"Detected emotion: {current_emotion}")
                    last_process_time = current_time
                except Exception as e:
                    print(f"Error detecting emotion: {e}")
            
            time.sleep(0.03)  # Limit to ~30 FPS
            
        # Release the webcam
        cap.release()
    except Exception as e:
        print(f"Error in webcam thread: {e}")
        webcam_active = False

def get_current_emotion():
    """Get the current detected emotion safely"""
    with emotion_lock:
        return current_emotion

def runModel():
    """
    Determine user's emotional response to the current track
    Returns: emotion category (positive, negative, neutral)
    """
    emotion = get_current_emotion()
    
    if not emotion:
        print("No emotion detected, using neutral")
        return "neutral"
    
    print(f"Current emotion for song evaluation: {emotion}")
    
    if emotion in positive_emotions:
        return "positive"
    elif emotion in negative_emotions:
        return "negative"
    else:
        return "neutral"

def main():
    global current_emotion
    if not initDB():
        print("Failed to initialize database connection. Exiting.")
        return
    
    start_webcam()

    try:
        while True:
            try:
                sp = auth()
                curr = getCurr(sp)

                if curr is not None:
                    # Get the latest emotion from the webcam thread
                    emotion = get_current_emotion()
                    
                    if emotion:
                        print(f"Current emotion is '{emotion}' for track {curr}")
                        
                        score = 0
                        if emotion in positive_emotions:
                            score = 1
                        elif emotion in negative_emotions:
                            score = -1
                        
                        if score != 0:
                            addDB(curr, score, emotion)

                    # Check for skips
                    sp_for_skip = auth()
                    if check_skip(sp_for_skip):
                        # Use a specific emotion for skips
                        addDB(curr, -1, "skipped")

            except Exception as e:
                print(f"Error in main loop: {e}")
            
            time.sleep(5)
    
    finally:
        stop_webcam()
        print("Program terminated.")

if __name__ == "__main__":
    main()