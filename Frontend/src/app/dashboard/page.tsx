"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import Player from '@/components/Player';
import MoodPlaylist from '@/components/MoodPlaylist';
import WebcamToggle from '@/components/WebcamToggle';

export default function Dashboard() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [situation, setSituation] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<{sentiment: string; keyword: string} | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

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
      <Sidebar />
      
      <div className="flex flex-col flex-grow overflow-hidden">
        <Header />
        
        <div className="flex-grow px-8 py-6 overflow-y-auto pb-24">
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
          
          <MoodPlaylist 
            title="Your Most Reacted Songs" 
            songs={mostReactedSongs}
          />
          
          <MoodPlaylist 
            title="Browse by Mood" 
            songs={moodCategories}
          />
          
          <section className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Recently Played</h2>
            <div className="bg-spotify-light-gray bg-opacity-30 rounded-lg p-4">
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
                  {[1, 2, 3, 4, 5].map((item) => (
                    <tr key={item} className="hover:bg-white hover:bg-opacity-10">
                      <td className="py-3">{item}</td>
                      <td className="py-3">Song Name {item}</td>
                      <td className="py-3">
                        <span className="text-lg">
                          {item % 2 === 0 ? '😊' : '🔥'}
                        </span>
                      </td>
                      <td className="py-3">Artist {item}</td>
                      <td className="py-3">3:2{item}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
        
        <Player />
      </div>
    </main>
  );
}
