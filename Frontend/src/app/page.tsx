"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Automatically initiate Spotify authentication
    const initiateSpotifyAuth = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/auth/spotify');
        const data = await response.json();
        
        if (data.auth_url) {
          // Redirect to Spotify's authorization page
          window.location.href = data.auth_url;
        } else {
          console.error('Failed to get auth URL');
          // Fallback to login page if auth fails
          router.push('/login');
        }
      } catch (error) {
        console.error('Error initiating Spotify auth:', error);
        // Fallback to login page if there's an error
        router.push('/login');
      }
    };

    initiateSpotifyAuth();
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-spotify-black">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">Spotilike</h1>
        <p className="text-gray-400 mb-8">Connecting to Spotify...</p>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
      </div>
    </div>
  );
}
