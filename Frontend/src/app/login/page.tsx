"use client";

import React, { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false);

  const handleSpotifyLogin = async () => {
    setIsLoading(true);
    try {
      // Get the Spotify auth URL from our backend
      const response = await fetch('http://localhost:5000/api/auth/spotify');
      const data = await response.json();
      
      if (data.auth_url) {
        // Redirect to Spotify's authorization page
        window.location.href = data.auth_url;
      } else {
        console.error('Failed to get auth URL');
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error initiating Spotify auth:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-spotify-black">
      <div className="w-full max-w-md p-8 space-y-8 bg-spotify-light-gray rounded-lg shadow-xl">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white">Spotilike</h1>
          <p className="mt-2 text-gray-400">Music that matches your mood</p>
        </div>
        
        <div className="mt-10">
          <button 
            onClick={handleSpotifyLogin}
            disabled={isLoading}
            className="btn-primary w-full flex items-center justify-center gap-2 mb-4 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span>Connecting to Spotify...</span>
            ) : (
              <>
                <span>Log in with Spotify</span>
              </>
            )}
          </button>
          
          <p className="mt-6 text-center text-sm text-gray-400">
            By logging in, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
}
