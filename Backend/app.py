from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from situation import analyze_text_sentiment_and_keyword, extract_json_from_response, play_multiple_songs_for_feeling_and_keyword
from main import auth
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Required for sessions

# Initialize Spotify client
sp = auth()

# Spotify OAuth setup
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri='http://localhost:5000/callback',
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
        # Redirect to frontend dashboard
        return redirect('http://localhost:3000/dashboard')
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
    try:
        from main import get_current_emotion
        emotion = get_current_emotion()
        return jsonify({"emotion": emotion})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port) 