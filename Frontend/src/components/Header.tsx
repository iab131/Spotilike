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
        
        <div className="border-l border-gray-700 pl-4 flex items-center gap-3">
          <div className="w-8 h-8 bg-gray-700 rounded-full overflow-hidden flex items-center justify-center">
            👤
          </div>
        </div>
      </div>
    </header>
  );
}
