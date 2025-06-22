"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import Player from '@/components/Player';
import MoodPlaylist from '@/components/MoodPlaylist';
import WebcamToggle from '@/components/WebcamToggle';

interface EnjoyedSong {
  track_id: string;
  title: string;
  artist: string;
  album_art?: string;
  duration: string;
  emotion: string;
  score: number;
  happy?: number;
  sad?: number;
  angry?: number;
  surprise?: number;
  fear?: number;
  disgust?: number;
  neutral?: number;
}


export default function Dashboard() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [situation, setSituation] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<{sentiment: string; keyword: string} | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [enjoyedSongs, setEnjoyedSongs] = useState<EnjoyedSong[]>([]);
  const [isLoadingSongs, setIsLoadingSongs] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMood, setSelectedMood] = useState<string | null>(null);
  const [rankedSongs, setRankedSongs] = useState<EnjoyedSong[]>([]);
  
  // Only keep these moods
  const searchCategories = [
    { name: 'Happy', color: 'from-yellow-400 to-orange-500', key: 'happy' },
    { name: 'Sad', color: 'from-purple-400 to-violet-500', key: 'sad' },
    { name: 'Angry', color: 'from-red-500 to-yellow-700', key: 'angry' },
    { name: 'Surprise', color: 'from-pink-400 to-yellow-400', key: 'surprise' },
    { name: 'Fear', color: 'from-blue-900 to-gray-700', key: 'fear' },
    { name: 'Disgust', color: 'from-green-600 to-lime-400', key: 'disgust' },
    { name: 'Neutral', color: 'from-gray-400 to-gray-600', key: 'neutral' },
  ];

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  // Fetch enjoyed songs when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchEnjoyedSongs();
    }
  }, [isAuthenticated]);

  // Listen for database updates
  useEffect(() => {
    if (!isAuthenticated) return;

    const eventSource = new EventSource('http://localhost:5001/api/db-updates');
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'db_update') {
          console.log('Database updated, refreshing enjoyed songs...');
          fetchEnjoyedSongs();
        }
      } catch (error) {
        console.error('Error parsing SSE data:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      eventSource.close();
    };

    // Cleanup on unmount
    return () => {
      eventSource.close();
    };
  }, [isAuthenticated]);

  // Periodic refresh as fallback (every 30 seconds)
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(() => {
      fetchEnjoyedSongs();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/auth/status');
      const data = await response.json();
      
      if (data.authenticated) {
        setIsAuthenticated(true);
      } else {
        // Redirect to login if not authenticated
        router.push('/login');
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      router.push('/login');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchEnjoyedSongs = async () => {
    try {
      setIsLoadingSongs(true);
      const response = await fetch('http://localhost:5001/api/enjoyed-songs');
      const data = await response.json();
      
      console.log('Fetched enjoyed songs data:', data); // Debug log
      
      if (data.songs) {
        console.log('Setting enjoyed songs:', data.songs); // Debug log
        setEnjoyedSongs(data.songs);
      }
    } catch (error) {
      console.error('Error fetching enjoyed songs:', error);
    } finally {
      setIsLoadingSongs(false);
    }
  };

  const handleAnalyzeSituation = async () => {
    if (!situation.trim()) return;
    
    setIsAnalyzing(true);
    try {
      const response = await fetch('http://localhost:5001/api/analyze-situation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ situation: situation }),
      });
      
      const data = await response.json();
      if (data.sentiment && data.keyword) {
        setAnalysis(data);
      }
    } catch (error) {
      console.error('Error analyzing situation:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handlePlayMusic = async () => {
    if (!analysis) return;
    
    setIsPlaying(true);
    try {
      const response = await fetch('http://localhost:5001/api/play-music', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sentiment: analysis.sentiment,
          keyword: analysis.keyword,
          num_songs: 5
        }),
      });
      
      const data = await response.json();
      if (data.tracks) {
        console.log('Playing tracks:', data.tracks);
      }
    } catch (error) {
      console.error('Error playing music:', error);
    } finally {
      setIsPlaying(false);
    }
  };

  const getEmotionEmoji = (emotion: string) => {
    const emotionMap: { [key: string]: string } = {
      'happy': '😊',
      'sad': '😢',
      'angry': '😠',
      'surprise': '😲',
      'fear': '😨',
      'disgust': '🤢',
      'neutral': '😐'
    };
    return emotionMap[emotion.toLowerCase()] || '🎵';
  };

  // Handler for mood button click
  const handleMoodClick = async (moodKey: string) => {
    setSelectedMood(moodKey);
    setIsLoadingSongs(true);
    try {
      const response = await fetch('http://localhost:5001/api/enjoyed-songs');
      const data = await response.json();
      if (data.songs) {
        const sorted = [...data.songs].sort((a, b) => {
          // 1. Sort by mood score if available
          if (typeof b[moodKey] === 'number' && typeof a[moodKey] === 'number') {
            return b[moodKey] - a[moodKey];
          }
          // 2. Prioritize songs whose main emotion matches the mood
          if (b.emotion === moodKey && a.emotion !== moodKey) return -1;
          if (a.emotion === moodKey && b.emotion !== moodKey) return 1;
          // 3. Fallback: sort by generic score
          return (b.score || 0) - (a.score || 0);
        });
        setRankedSongs(sorted);
      } else {
        setRankedSongs([]);
      }
    } catch (error) {
      console.error(error);
      setRankedSongs([]);
    } finally {
      setIsLoadingSongs(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-spotify-black">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to login
  }

  // Mock data for demonstration
  const mostReactedSongs = [
    { title: 'Happy Vibes', artist: 'Good Mood', },
    { title: 'Upbeat Tempo', artist: 'Feel Good Inc', },
    { title: 'Energy Boost', artist: 'Positive Vibes', },
    { title: 'Sunshine Melody', artist: 'Happy Days', },
    { title: 'Dance Moves', artist: 'Groove Master', },
  ];

  const moodCategories = [
    { title: 'Calm', artist: 'Relaxing Playlist', },
    { title: 'Energetic', artist: 'Workout Mix', },
    { title: 'Focus', artist: 'Concentration', },
    { title: 'Throwbacks', artist: 'Nostalgia', },
    { title: 'Rap', artist: 'Hip Hop Collection', },
  ];

  return (
    <main className="flex h-screen bg-spotify-black text-white overflow-hidden">
      
      <div className="flex flex-col flex-grow overflow-hidden">
        <Header />
        
        <div className="flex-grow px-20 py-6 overflow-y-auto pb-24">
          <section className="mb-6">
            <div className="flex items-center">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-4xl">
                👤
              </div>
              <div className="ml-6">
                <h1 className="text-3xl font-bold">Welcome Back!</h1>
                <p className="text-gray-400">Your music, tailored to your emotions</p>
              </div>
            </div>
          </section>

          {/* Webcam Mood Detection Toggle */}
          <WebcamToggle />

          {/* Situation Input Section */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold mb-4">How are you feeling today?</h2>
            <div className="bg-spotify-light-gray bg-opacity-30 rounded-lg p-6">
              <div className="flex gap-4 mb-4">
                <input
                  type="text"
                  value={situation}
                  onChange={(e) => setSituation(e.target.value)}
                  placeholder="Tell us what's happening... (e.g., 'I just got a promotion', 'I'm feeling stressed about work')"
                  className="flex-1 bg-spotify-light-gray text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-green-500"
                />
                <button
                  onClick={handleAnalyzeSituation}
                  disabled={isAnalyzing || !situation.trim()}
                  className="bg-green-500 hover:bg-green-600 disabled:bg-gray-600 text-white px-6 py-2 rounded-lg font-medium"
                >
                  {isAnalyzing ? 'Analyzing...' : 'Analyze'}
                </button>
              </div>
              
              {analysis && (
                <div className="bg-spotify-light-gray bg-opacity-50 rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400">Detected Mood:</p>
                      <p className="text-xl font-semibold capitalize">{analysis.sentiment}</p>
                      <p className="text-gray-400 mt-1">Topic:</p>
                      <p className="text-lg capitalize">{analysis.keyword}</p>
                    </div>
                    <button
                      onClick={handlePlayMusic}
                      disabled={isPlaying}
                      className="bg-green-500 hover:bg-green-600 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium"
                    >
                      {isPlaying ? 'Playing...' : 'Play Music'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </section>
          
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4">Browse by mood or feeling</h2>
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-6">
              {searchCategories.map((category, index) => (
                <div
                  key={index}
                  className={`p-5 rounded-lg bg-gradient-to-br ${category.color} hover:shadow-lg transition-shadow cursor-pointer ${selectedMood === category.key ? 'ring-4 ring-green-400' : ''}`}
                  onClick={() => handleMoodClick(category.key)}
                >
                  <h3 className="font-bold text-lg">{category.name}</h3>
                </div>
              ))}
            </div>
          </div>
          

          <section className="mb-8">
            <h2 className="text-2xl font-bold mb-4">
              {selectedMood ? `Top Songs for "${selectedMood.charAt(0).toUpperCase() + selectedMood.slice(1)}"` : 'Songs You Enjoyed Most'}
            </h2>
            <div className="bg-spotify-light-gray bg-opacity-30 rounded-lg p-4">
              {isLoadingSongs ? (
                <div className="text-center py-8">
                  <div className="text-gray-400">Loading songs...</div>
                </div>
              ) : (selectedMood ? (
                rankedSongs.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-gray-400">No songs found for this mood.</div>
                  </div>
                ) : (
                  <table className="w-full">
                    <thead className="border-b border-gray-700 text-left text-gray-400">
                      <tr>
                        <th className="pb-3 font-normal">#</th>
                        <th className="pb-3 font-normal">TITLE</th>
                        <th className="pb-3 font-normal">SCORE</th>
                        <th className="pb-3 font-normal">ARTIST</th>
                        <th className="pb-3 font-normal">DURATION</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rankedSongs.map((song, index) => (
                        <tr key={song.track_id} className="hover:bg-white hover:bg-opacity-10">
                          <td className="py-3">{index + 1}</td>
                          <td className="py-3">
                            <div className="flex items-center">
                              {song && song.album_art && song.album_art !== 'null' && (
                                <img 
                                  src={song.album_art} 
                                  alt={song.title || 'Album cover'}
                                  className="w-10 h-10 rounded mr-3"
                                  onError={(e) => {
                                    e.currentTarget.style.display = 'none';
                                  }}
                                />
                              )}
                              <div>
                                <div className="font-medium">{song?.title || 'Unknown Title'}</div>
                                <div className="text-sm text-gray-400">Score: {song[selectedMood] || 0}</div>
                              </div>
                            </div>
                          </td>
                          <td className="py-3">{song[selectedMood] || 0}</td>
                          <td className="py-3">{song?.artist || 'Unknown Artist'}</td>
                          <td className="py-3">{song?.duration || '0:00'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )
              ) : (
                // Default: show enjoyed songs
                isLoadingSongs ? (
                  <div className="text-center py-8">
                    <div className="text-gray-400">Loading your enjoyed songs...</div>
                  </div>
                ) : enjoyedSongs.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-gray-400">No songs with high scores yet. Start listening and reacting to build your collection!</div>
                  </div>
                ) : (
                  <table className="w-full">
                    <thead className="border-b border-gray-700 text-left text-gray-400">
                      <tr>
                        <th className="pb-3 font-normal">#</th>
                        <th className="pb-3 font-normal">TITLE</th>
                        <th className="pb-3 font-normal">YOUR REACTION</th>
                        <th className="pb-3 font-normal">ARTIST</th>
                        <th className="pb-3 font-normal">DURATION</th>
                      </tr>
                    </thead>
                    <tbody>
                      {enjoyedSongs.map((song, index) => {
                        console.log('Rendering song:', song); // Debug log
                        return (
                          <tr key={song.track_id} className="hover:bg-white hover:bg-opacity-10">
                            <td className="py-3">{index + 1}</td>
                            <td className="py-3">
                              <div className="flex items-center">
                                {song && song.album_art && song.album_art !== 'null' && (
                                  <img 
                                    src={song.album_art} 
                                    alt={song.title || 'Album cover'}
                                    className="w-10 h-10 rounded mr-3"
                                    onError={(e) => {
                                      // Hide the image if it fails to load
                                      e.currentTarget.style.display = 'none';
                                    }}
                                  />
                                )}
                                <div>
                                  <div className="font-medium">{song?.title || 'Unknown Title'}</div>
                                  <div className="text-sm text-gray-400">Score: {song?.score || 0}</div>
                                </div>
                              </div>
                            </td>
                            <td className="py-3">
                              <span className="text-lg" title={song?.emotion || 'unknown'}>
                                {getEmotionEmoji(song?.emotion || 'unknown')}
                              </span>
                            </td>
                            <td className="py-3">{song?.artist || 'Unknown Artist'}</td>
                            <td className="py-3">{song?.duration || '0:00'}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                )
              )}
            </div>
          </section>
        </div>
        
        <Player />
      </div>
    </main>
  );
}
