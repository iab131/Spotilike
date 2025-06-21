# Spotilike - Emotion-Based Music Recommendation

A full-stack web application that analyzes your emotional state and recommends music based on your current situation and mood.

## Features

- **Spotify Authentication**: Secure OAuth flow with Spotify
- **Emotion Analysis**: Uses Gemini AI to analyze text and extract sentiment/keywords
- **Music Recommendation**: Automatically finds and plays music based on your mood
- **Real-time Emotion Detection**: Webcam-based emotion analysis (backend)
- **Modern UI**: Beautiful Next.js frontend with Tailwind CSS

## Prerequisites

- Node.js (v18 or higher)
- Python 3.8+
- Spotify Premium account (for playback control)
- MongoDB database
- Google Gemini API key

## Environment Variables

Create a `.env` file in the `Backend/` directory:

```env
# Spotify API
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret

# Google Gemini API
GEM_API_KEY=your_gemini_api_key

# MongoDB
MONGODB_URI=your_mongodb_connection_string

# Flask
SECRET_KEY=your_secret_key_here
```

## Installation & Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd Backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the Flask server:
   ```bash
   python app.py
   ```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd Frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will run on `http://localhost:3000`

## Usage

1. **Open your browser** and go to `http://localhost:3000`
2. **Click "Log in with Spotify"** to authenticate
3. **Enter your current situation** in the text input (e.g., "I just got a promotion", "I'm feeling stressed about work")
4. **Click "Analyze"** to get sentiment and keyword analysis
5. **Click "Play Music"** to start playing music that matches your mood

## API Endpoints

### Authentication
- `GET /api/auth/spotify` - Get Spotify authorization URL
- `GET /callback` - Handle Spotify OAuth callback
- `GET /api/auth/status` - Check authentication status

### Music & Analysis
- `POST /api/analyze-situation` - Analyze text for sentiment and keywords
- `POST /api/play-music` - Play music based on sentiment and keyword
- `GET /api/current-emotion` - Get current emotion from webcam

## Architecture

- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Backend**: Flask with Python
- **AI**: Google Gemini for text analysis
- **Music**: Spotify Web API for music playback
- **Database**: MongoDB for storing track reactions
- **Authentication**: Spotify OAuth 2.0

## Troubleshooting

### Spotify Authentication Issues
- Ensure your Spotify app is properly configured in the Spotify Developer Dashboard
- Add your email as a user in your Spotify app settings
- Make sure you have a Spotify Premium account for playback control

### Backend Issues
- Check that all environment variables are set correctly
- Ensure MongoDB is running and accessible
- Verify that all Python dependencies are installed

### Frontend Issues
- Make sure both frontend and backend servers are running
- Check browser console for any CORS or network errors
- Ensure you're using the correct ports (3000 for frontend, 5000 for backend)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
