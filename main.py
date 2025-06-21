from spotipy.oauth2 import SpotifyOAuth
import spotipy

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_SECRET',
    redirect_uri='http://localhost:8888/callback',
    scope='user-read-playback-state playlist-modify-public playlist-modify-private'
))

current = sp.current_playback()
track_id = current['item']['id']