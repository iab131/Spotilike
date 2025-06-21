from google import genai
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from main import auth
import re

load_dotenv()

gem_api_key = os.getenv("GEM_API_KEY")

client = genai.Client(api_key=gem_api_key)

sp = auth()

def analyze_text_sentiment_and_keyword(text):
    prompt = (
        "Given the following situation, extract: "
        "1. The overall sentiment (happy, sad, angry, etc.) "
        "2. The main keyword/topic (e.g., love, jobs, family, etc.). "
        "Return your answer as a JSON object with 'sentiment' and 'keyword'. "
        f"Situation: {text}"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    print(response.text)
    return response.text
    

def play_song_for_feeling_and_keyword(sp, feeling, keyword):
    print("Searching for a track...")
    try:
        query = f"{feeling} {keyword}"
        results = sp.search(q=query, type='track', limit=1)
        tracks = results.get('tracks', {}).get('items', [])
        if not tracks:
            print(f"No tracks found for mood '{feeling}' and keyword '{keyword}'.")
            return None
        track = tracks[0]
        track_uri = track['uri']
        print(f"Playing: {track['name']} by {track['artists'][0]['name']}")
        sp.start_playback(uris=[track_uri])
        return track
    except Exception as e:
        print(f"Error during Spotify search/playback: {e}")

def extract_json_from_response(response_text):
    # Remove code block markers and whitespace
    cleaned = re.sub(r"^```(?:json)?|```$", "", response_text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)

def play_multiple_songs_for_feeling_and_keyword(sp, feeling, keyword, num_songs=5):
    query = f"{feeling} {keyword}"
    results = sp.search(q=query, type='track', limit=num_songs)
    tracks = results.get('tracks', {}).get('items', [])
    
    if not tracks:
        print(f"No tracks found for mood '{feeling}' and keyword '{keyword}'.")
        return None
    
    # Get URIs of all tracks
    track_uris = [track['uri'] for track in tracks]
    
    print(f"Found {len(tracks)} songs:")
    for i, track in enumerate(tracks, 1):
        print(f"{i}. {track['name']} by {track['artists'][0]['name']}")
    
    # Start playback with the first track, queue the rest
    try:
        sp.start_playback(uris=track_uris)
        print(f"Playing {len(tracks)} songs for '{feeling} {keyword}'")
        return tracks
    except Exception as e:
        print(f"Error during Spotify playback: {e}")
        return None

def create_and_play_playlist_for_feeling_and_keyword(sp, feeling, keyword, num_songs=10):
    query = f"{feeling} {keyword}"
    results = sp.search(q=query, type='track', limit=num_songs)
    tracks = results.get('tracks', {}).get('items', [])
    
    if not tracks:
        print(f"No tracks found for mood '{feeling}' and keyword '{keyword}'.")
        return None
    
    # Create a temporary playlist
    playlist_name = f"{feeling.title()} {keyword.title()} Mix"
    user_id = sp.current_user()['id']
    
    try:
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=f"Auto-generated playlist for {feeling} {keyword} mood"
        )
        
        # Add tracks to playlist
        track_uris = [track['uri'] for track in tracks]
        sp.playlist_add_items(playlist['id'], track_uris)
        
        print(f"Created playlist: {playlist_name}")
        print(f"Added {len(tracks)} songs:")
        for i, track in enumerate(tracks, 1):
            print(f"{i}. {track['name']} by {track['artists'][0]['name']}")
        
        # Start playing the playlist
        sp.start_playback(context_uri=playlist['uri'])
        print(f"Now playing: {playlist_name}")
        
        return playlist, tracks
        
    except Exception as e:
        print(f"Error creating/playing playlist: {e}")
        return None

def queue_songs_for_feeling_and_keyword(sp, feeling, keyword, num_songs=5):
    query = f"{feeling} {keyword}"
    results = sp.search(q=query, type='track', limit=num_songs)
    tracks = results.get('tracks', {}).get('items', [])
    
    if not tracks:
        print(f"No tracks found for mood '{feeling}' and keyword '{keyword}'.")
        return None
    
    print(f"Queueing {len(tracks)} songs for '{feeling} {keyword}':")
    
    try:
        for i, track in enumerate(tracks):
            sp.add_to_queue(track['uri'])
            print(f"{i+1}. {track['name']} by {track['artists'][0]['name']}")
        
        print("Songs added to queue!")
        return tracks
        
    except Exception as e:
        print(f"Error queueing songs: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    text = "I just got broken up with"
    result = analyze_text_sentiment_and_keyword(text)
    parsed = extract_json_from_response(result)
    feeling = parsed['sentiment']
    keyword = parsed['keyword']
    print("========", feeling, keyword)

    play_song_for_feeling_and_keyword(sp, feeling, keyword)