"use client";

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';

export default function LoginPage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-spotify-black">
      <div className="w-full max-w-md p-8 space-y-8 bg-spotify-light-gray rounded-lg shadow-xl">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white">Spotilike</h1>
          <p className="mt-2 text-gray-400">Music that matches your mood</p>
        </div>
        
        <div className="mt-10">
          <Link href="/dashboard" 
                className="btn-primary w-full flex items-center justify-center gap-2 mb-4">
            <span>Log in with Spotify</span>
          </Link>
          
          <p className="mt-6 text-center text-sm text-gray-400">
            By logging in, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
}
