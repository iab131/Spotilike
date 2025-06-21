"use client";
import React, { useState } from 'react';

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  
  return (
    <header className="bg-spotify-gray p-4 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <button className="bg-black rounded-full p-2 opacity-70 hover:opacity-100">
          <span className="sr-only">Back</span>
          &lt;
        </button>
        <button className="bg-black rounded-full p-2 opacity-70 hover:opacity-100">
          <span className="sr-only">Forward</span>
          &gt;
        </button>
      </div>
      
      <div className="flex-grow max-w-lg mx-4">
        <div className="relative">
          <input
            type="text"
            placeholder="Search for songs, moods, or feelings..."
            className="w-full py-2 px-4 rounded-full bg-spotify-light-gray text-white border border-gray-700 focus:outline-none focus:border-white"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white">
            🔍
          </button>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <button className="bg-black rounded-full p-2 opacity-70 hover:opacity-100 relative">
          <span className="sr-only">Emotion Detection</span>
          👁️
          <span className="absolute top-0 right-0 w-3 h-3 bg-green-500 rounded-full"></span>
        </button>
        
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
        
        <div className="border-l border-gray-700 pl-4 flex items-center gap-3">
          <div className="w-8 h-8 bg-gray-700 rounded-full overflow-hidden flex items-center justify-center">
            👤
          </div>
        </div>
      </div>
    </header>
  );
}
