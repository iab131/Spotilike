# Spotilike with Emotion Detection

This extended version of Spotilike incorporates facial emotion detection to analyze your reaction to music in real-time, in addition to tracking skipped songs.

## Features

- **Real-time Emotion Detection**: Uses your webcam to detect your emotional response to the music you're listening to
- **Automated Music Feedback**: Automatically records positive scores for songs that make you happy or surprised, and negative scores for songs that trigger negative emotions
- **Skip Detection**: Still maintains the original skip detection as an additional signal for disliked songs
- **MongoDB Integration**: All song preferences are stored in MongoDB for future recommendations

## How It Works

1. The webcam captures your facial expressions while you listen to music on Spotify
2. DeepFace analyzes your emotions in real-time (happy, sad, angry, etc.)
3. Positive emotions (happy, surprised) result in a +1 score for the current song
4. Negative emotions (sad, angry, disgusted, fearful) result in a -1 score
5. Skipping a song (before 30 seconds) also results in a -1 score
6. All scores are saved to your MongoDB database

## Emotion Categories

- **Positive**: happy, surprise
- **Negative**: angry, disgust, fear, sad
- **Neutral**: neutral (no score change)

## Requirements

- Spotify Premium account
- Webcam
- MongoDB database
- Python 3.6+
- Required packages (see requirements.txt)

## Setup

1. Make sure you have all required packages installed:
   ```
   pip install -r requirements.txt
   ```

2. Set up your environment variables in a `.env` file:
   ```
   CLIENT_ID=your_spotify_client_id
   CLIENT_SECRET=your_spotify_client_secret
   MONGODB_URI=your_mongodb_connection_string
   ```

3. Run the application:
   ```
   python main.py
   ```

4. Start playing music on Spotify while the application is running

## Important Notes

- The application needs permission to access your webcam
- Ensure you have good lighting for accurate emotion detection
- DeepFace may take a moment to initialize on first run as it downloads necessary models
- You need to have a Spotify session active (playing music) for the application to work
- If you want to turn off the webcam feature, you can modify the code to use only the skip detection logic

## Troubleshooting

- If the webcam doesn't start, check that it's not being used by another application
- If emotion detection is inaccurate, try improving lighting or positioning
- If Spotify connection fails, ensure your credentials are correct and your account is active
- If MongoDB connection fails, verify your connection string and network connectivity

## Privacy Note

This application processes facial data locally on your device for emotion detection. No facial images are stored or transmitted.
