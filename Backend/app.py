from flask import Flask, request, jsonify, redirect, url_for, session, Response
from flask_cors import CORS
from situation import analyze_text_sentiment_and_keyword, extract_json_from_response, play_multiple_songs_for_feeling_and_keyword
from main import auth, initDB, getCurr, check_skip, addDB, get_current_emotion, start_webcam, stop_webcam, get_webcam_status as get_webcam_status_main, main as main_function
from mongoDB import MongoDBManager
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import json
import threading
import time
from monitoring_flag import set_main_monitoring_should_stop, get_main_monitoring_should_stop

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Required for sessions

# Initialize Spotify client
sp = auth()

# Global variable to track database updates
db_update_event = threading.Event()
last_db_update = time.time()

# Global variable to track the main monitoring thread
main_monitoring_thread = None
monitoring_active = False

# Spotify OAuth setup
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri='http://127.0.0.1:5001/callback',
        scope='user-read-playback-state user-modify-playback-state playlist-modify-public playlist-modify-private streaming user-read-private user-read-email'
    )

@app.route('/')
def home():
    return jsonify({"message": "Spotilike API is running!"})

@app.route('/api/auth/spotify')
def spotify_auth():
    """Initiate Spotify OAuth flow"""
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"auth_url": auth_url})

@app.route('/callback')
def callback():
    """Handle Spotify OAuth callback"""
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    
    if token_info:
        session["token_info"] = token_info
        return redirect("http://localhost:3000/dashboard?auth=success")
    else:
        return jsonify({"error": "Failed to get access token"}), 400

@app.route('/api/auth/status')
def auth_status():
    """Check if user is authenticated"""
    try:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info:
            return jsonify({"authenticated": False})
        
        # Check if token is expired
        if sp_oauth.is_token_expired(token_info):
            return jsonify({"authenticated": False})
        
        return jsonify({"authenticated": True})
    except Exception as e:
        return jsonify({"authenticated": False, "error": str(e)})

@app.route('/api/analyze-situation', methods=['POST'])
def analyze_situation():
    try:
        data = request.get_json()
        situation_text = data.get('situation', '')
        
        if not situation_text:
            return jsonify({"error": "No situation text provided"}), 400
        
        # Analyze the situation using Gemini
        result = analyze_text_sentiment_and_keyword(situation_text)
        parsed = extract_json_from_response(result)
        
        return jsonify({
            "sentiment": parsed['sentiment'],
            "keyword": parsed['keyword'],
            "situation": situation_text
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/play-music', methods=['POST'])
def play_music():
    try:
        data = request.get_json()
        sentiment = data.get('sentiment', '')
        keyword = data.get('keyword', '')
        num_songs = data.get('num_songs', 5)
        
        if not sentiment or not keyword:
            return jsonify({"error": "Sentiment and keyword are required"}), 400
        
        # Play multiple songs based on sentiment and keyword
        tracks = play_multiple_songs_for_feeling_and_keyword(sp, sentiment, keyword, num_songs)
        
        if tracks:
            track_list = []
            for track in tracks:
                track_list.append({
                    "name": track['name'],
                    "artist": track['artists'][0]['name'],
                    "uri": track['uri']
                })
            
            return jsonify({
                "message": f"Playing {len(tracks)} songs for {sentiment} {keyword}",
                "tracks": track_list
            })
        else:
            return jsonify({"error": "No tracks found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/current-emotion', methods=['GET'])
def get_current_emotion():
    """Get the current detected emotion from webcam"""
    try:
        from main import get_current_emotion
        emotion = get_current_emotion()
        return jsonify({"emotion": emotion})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/current-playback', methods=['GET'])
def get_current_playback():
    """Get current playback information from Spotify"""
    try:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info or sp_oauth.is_token_expired(token_info):
            return jsonify({"error": "Not authenticated"}), 401
        
        # Create a Spotify client with the token
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        # Get current playback
        current = sp.current_playback()
        
        if not current or not current.get('item'):
            return jsonify({
                "is_playing": False,
                "message": "No track currently playing"
            })
        
        track = current['item']
        progress_ms = current.get('progress_ms', 0)
        duration_ms = track.get('duration_ms', 0)
        
        # Get the smallest album art (for better performance)
        album_art = None
        if track.get('album', {}).get('images'):
            album_art = track['album']['images'][-1]['url']  # Last image is usually smallest
        
        playback_info = {
            "is_playing": current.get('is_playing', False),
            "track": {
                "id": track.get('id'),
                "name": track.get('name'),
                "artists": [artist.get('name') for artist in track.get('artists', [])],
                "album": track.get('album', {}).get('name'),
                "album_art": album_art,
                "duration_ms": duration_ms,
                "progress_ms": progress_ms,
                "uri": track.get('uri')
            },
            "device": {
                "name": current.get('device', {}).get('name'),
                "type": current.get('device', {}).get('type')
            }
        }
        
        return jsonify(playback_info)
        
    except Exception as e:
        print(f"Error getting current playback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/playback/play', methods=['POST'])
def start_playback():
    """Play or resume playback"""
    try:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info or sp_oauth.is_token_expired(token_info):
            return jsonify({"error": "Not authenticated"}), 401
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        sp.start_playback()
        
        return jsonify({"message": "Playback started"})
        
    except Exception as e:
        print(f"Error starting playback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/playback/pause', methods=['POST'])
def pause_playback():
    """Pause playback"""
    try:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info or sp_oauth.is_token_expired(token_info):
            return jsonify({"error": "Not authenticated"}), 401
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        sp.pause_playback()
        
        return jsonify({"message": "Playback paused"})
        
    except Exception as e:
        print(f"Error pausing playback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/playback/next', methods=['POST'])
def skip_next():
    """Skip to next track"""
    try:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info or sp_oauth.is_token_expired(token_info):
            return jsonify({"error": "Not authenticated"}), 401
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        sp.next_track()
        
        return jsonify({"message": "Skipped to next track"})
        
    except Exception as e:
        print(f"Error skipping track: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/playback/previous', methods=['POST'])
def skip_previous():
    """Go to previous track"""
    try:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info or sp_oauth.is_token_expired(token_info):
            return jsonify({"error": "Not authenticated"}), 401
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        sp.previous_track()
        
        return jsonify({"message": "Went to previous track"})
        
    except Exception as e:
        print(f"Error going to previous track: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/playback/seek', methods=['POST'])
def seek_track():
    """Seek to position in track"""
    try:
        data = request.get_json()
        position_ms = data.get('position_ms', 0)
        
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info or sp_oauth.is_token_expired(token_info):
            return jsonify({"error": "Not authenticated"}), 401
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        sp.seek_track(position_ms)
        
        return jsonify({"message": f"Seeked to {position_ms}ms"})
        
    except Exception as e:
        print(f"Error seeking track: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/playback/shuffle', methods=['POST'])
def toggle_shuffle():
    """Toggle shuffle mode"""
    try:
        data = request.get_json()
        state = data.get('state', True)  # Default to True (enable shuffle)
        
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info or sp_oauth.is_token_expired(token_info):
            return jsonify({"error": "Not authenticated"}), 401
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        sp.shuffle(state)
        
        return jsonify({"message": f"Shuffle {'enabled' if state else 'disabled'}"})
        
    except Exception as e:
        print(f"Error toggling shuffle: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/playback/repeat', methods=['POST'])
def set_repeat_mode():
    """Set repeat mode (off, track, context)"""
    try:
        data = request.get_json()
        state = data.get('state', 'context')  # Default to context (repeat playlist)
        
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info or sp_oauth.is_token_expired(token_info):
            return jsonify({"error": "Not authenticated"}), 401
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        sp.repeat(state)
        
        return jsonify({"message": f"Repeat mode set to {state}"})
        
    except Exception as e:
        print(f"Error setting repeat mode: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/playback/state', methods=['GET'])
def get_playback_state():
    """Get current playback state including shuffle and repeat modes"""
    try:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info or sp_oauth.is_token_expired(token_info):
            return jsonify({"error": "Not authenticated"}), 401
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        current = sp.current_playback()
        
        if not current:
            return jsonify({
                "shuffle_state": False,
                "repeat_state": "off"
            })
        
        return jsonify({
            "shuffle_state": current.get('shuffle_state', False),
            "repeat_state": current.get('repeat_state', 'off')
        })
        
    except Exception as e:
        print(f"Error getting playback state: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webcam/start', methods=['POST'])
def start_webcam():
    """Start webcam and emotion detection"""
    try:
        # Start the main monitoring system which includes webcam
        start_main_monitoring()
        return jsonify({"message": "Webcam and monitoring started for emotion detection"})
    except Exception as e:
        print(f"Error starting webcam: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webcam/stop', methods=['POST'])
def stop_webcam():
    """Stop webcam and emotion detection"""
    try:
        # Stop the main monitoring system which includes webcam
        stop_main_monitoring()
        return jsonify({"message": "Webcam and monitoring stopped"})
    except Exception as e:
        print(f"Error stopping webcam: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webcam/status', methods=['GET'])
def webcam_status_api():
    """Get current webcam status"""
    try:
        status = get_webcam_status_main()
        status['monitoring_active'] = monitoring_active
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitoring/start', methods=['POST'])
def api_start_monitoring():
    """Start the main monitoring system"""
    try:
        start_main_monitoring()
        return jsonify({"message": "Main monitoring system started"})
    except Exception as e:
        print(f"Error starting monitoring: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitoring/stop', methods=['POST'])
def api_stop_monitoring():
    """Stop the main monitoring system"""
    try:
        stop_main_monitoring()
        return jsonify({"message": "Main monitoring system stopped"})
    except Exception as e:
        print(f"Error stopping monitoring: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitoring/status', methods=['GET'])
def api_get_monitoring_status():
    """Get current monitoring status"""
    try:
        webcam_status = get_webcam_status_main()
        return jsonify({
            "monitoring_active": monitoring_active,
            "webcam_active": webcam_status.get('webcam_active', False),
            "current_emotion": webcam_status.get('current_emotion', 'none')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/enjoyed-songs', methods=['GET'])
def get_enjoyed_songs():
    """Get top 5 songs with total_score greater than 1 from database"""
    try:
        # Initialize MongoDB connection
        mongo_manager = MongoDBManager()
        if not mongo_manager.connect():
            return jsonify({"error": "Database connection failed"}), 500
        
        # Get top 5 songs with total_score > 1, sorted by total_score descending
        songs = mongo_manager.find_many(
            filter_query={"total_score": {"$gt": 1}},
            limit=5,
            sort_by=("total_score", -1)
        )
        
        if not songs:
            return jsonify({"songs": []})
        
        # Get Spotify client for additional track info
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info or sp_oauth.is_token_expired(token_info):
            return jsonify({"error": "Not authenticated with Spotify"}), 401
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        # Get detailed track information from Spotify
        track_ids = [song['track_id'] for song in songs]
        track_details = sp.tracks(track_ids)['tracks']
        
        # Combine database data with Spotify data
        enjoyed_songs = []
        for i, song in enumerate(songs):
            spotify_track = track_details[i]
            if spotify_track:
                # Convert duration from ms to mm:ss format
                duration_ms = spotify_track.get('duration_ms', 0)
                duration_min = duration_ms // 60000
                duration_sec = (duration_ms % 60000) // 1000
                duration_str = f"{duration_min}:{duration_sec:02d}"
                
                # Get album art (smallest for better performance)
                album_art = None
                if spotify_track.get('album', {}).get('images'):
                    album_art = spotify_track['album']['images'][-1]['url']
                
                # Get artist name safely
                artist_name = 'Unknown'
                if spotify_track.get('artists') and len(spotify_track['artists']) > 0:
                    artist_name = spotify_track['artists'][0].get('name', 'Unknown')
                
                # Find the dominant emotion (highest count)
                emotion_counts = {}
                for emotion in ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral', 'skipped']:
                    emotion_field = f'emotion_{emotion}'
                    emotion_counts[emotion] = song.get(emotion_field, 0)
                
                # Get the emotion with the highest count
                dominant_emotion = max(emotion_counts, key=emotion_counts.get)
                
                enjoyed_songs.append({
                    "track_id": song['track_id'],
                    "title": spotify_track.get('name', 'Unknown'),
                    "artist": artist_name,
                    "album_art": album_art,
                    "duration": duration_str,
                    "emotion": dominant_emotion,
                    "score": song.get('total_score', 0),
                    "emotion_breakdown": emotion_counts
                })
        
        mongo_manager.disconnect()
        return jsonify({"songs": enjoyed_songs})
        
    except Exception as e:
        print(f"Error getting enjoyed songs: {str(e)}")
        return jsonify({"error": str(e)}), 500

def notify_db_update():
    """Notify frontend that database has been updated"""
    global db_update_event, last_db_update
    last_db_update = time.time()
    db_update_event.set()
    # Reset the event after a short delay
    threading.Timer(0.1, db_update_event.clear).start()

@app.route('/api/db-updates', methods=['GET'])
def db_updates_sse():
    """Server-Sent Events endpoint for database updates"""
    def generate():
        global last_db_update
        while True:
            # Wait for database update event
            db_update_event.wait(timeout=30)  # 30 second timeout
            
            # Send update notification
            yield f"data: {json.dumps({'timestamp': last_db_update, 'type': 'db_update'})}\n\n"
            
            # Small delay to prevent rapid firing
            time.sleep(0.5)
    
    return Response(generate(), mimetype='text/plain')

def main_monitoring_loop():
    """Run the original main function from main.py in a thread"""
    global monitoring_active
    
    print("🔄 Starting main function from main.py...")
    
    try:
        # Run the original main function
        main_function()
    except Exception as e:
        print(f"❌ Error in main function: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔄 Main function from main.py stopped.")

def start_main_monitoring():
    """Start the main function from main.py in a thread"""
    global main_monitoring_thread, monitoring_active
    if monitoring_active:
        print("⚠️ Main monitoring is already active")
        return
    monitoring_active = True
    set_main_monitoring_should_stop(False)  # Reset flag when starting
    main_monitoring_thread = threading.Thread(target=main_monitoring_loop, daemon=True)
    main_monitoring_thread.start()
    print("✅ Main function from main.py started in background thread")

def stop_main_monitoring():
    """Stop the main monitoring thread"""
    global monitoring_active
    if not monitoring_active:
        print("⚠️ Main monitoring is not active")
        return
    monitoring_active = False
    set_main_monitoring_should_stop(True)  # Set flag to request stop
    print("🛑 Main monitoring thread stop requested")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    
    # Start the main monitoring system automatically
    print("🚀 Starting Spotilike Flask app...")
    # print("🔄 Initializing main monitoring system...")
    # start_main_monitoring()
    
    print(f"🌐 Flask app running on port {port}")
    # print("📊 Main monitoring system is active and tracking emotions/skips")
    print("🎵 Ready to analyze your music listening experience!")
    
    app.run(debug=True, host='0.0.0.0', port=port)

# Remove: exported_main_monitoring_should_stop = lambda: main_monitoring_should_stop 