"use client";
import React, { useState } from 'react';

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  
  return (
    <header className="bg-spotify-gray px-20 py-4 flex items-center justify-between">
      <h1 className="text-2xl font-bold">Spotilike</h1>
      
      
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <button className="opacity-70 hover:opacity-100">
            <span className="sr-only">Volume</span>
            🔊
          </button>
          <input
            type="range"
            min="0"
            max="100"
            className="volume-slider"
            defaultValue="80"
          />
          <button className="ml-1 opacity-70 hover:opacity-100 text-sm">
            <span className="sr-only">Auto-adjust volume</span>
            📏
          </button>
        </div>

      </div>
    </header>
  );
}
