"use client";
import React, { useState } from 'react';

export default function Player() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(30);
  
  return (
    <div className="bg-spotify-light-gray border-t border-gray-700 p-4 fixed bottom-0 left-0 right-0">
      <div className="flex items-center justify-between">
        {/* Song info */}
        <div className="flex items-center space-x-4 w-1/4">
          <div className="w-14 h-14 bg-gray-600 rounded">
            {/* Album art would go here */}
          </div>
          <div>
            <h4 className="text-white font-medium">Song Title</h4>
            <p className="text-gray-400 text-sm">Artist Name</p>
          </div>
          <button className="text-gray-400 hover:text-white">
            <span className="sr-only">Like</span>
            ❤️
          </button>
        </div>
        
        {/* Player controls */}
        <div className="flex flex-col items-center w-2/4">
          <div className="flex items-center space-x-4 mb-2">
            <button className="text-gray-400 hover:text-white">
              <span className="sr-only">Shuffle</span>
              🔀
            </button>
            <button className="text-gray-400 hover:text-white">
              <span className="sr-only">Previous</span>
              ⏮️
            </button>
            <button 
              className="bg-white text-black rounded-full w-8 h-8 flex items-center justify-center hover:scale-110 transition-transform"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              <span className="sr-only">{isPlaying ? 'Pause' : 'Play'}</span>
              {isPlaying ? '⏸️' : '▶️'}
            </button>
            <button className="text-gray-400 hover:text-white">
              <span className="sr-only">Next</span>
              ⏭️
            </button>
            <button className="text-gray-400 hover:text-white">
              <span className="sr-only">Repeat</span>
              🔁
            </button>
          </div>
          
          <div className="w-full flex items-center space-x-2">
            <span className="text-xs text-gray-400">1:23</span>
            <div className="flex-grow bg-gray-600 h-1 rounded-full relative">
              <div 
                className="absolute left-0 top-0 bottom-0 bg-white rounded-full"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <span className="text-xs text-gray-400">3:45</span>
          </div>
        </div>
        
        {/* Emotion detection */}
        <div className="w-1/4 flex justify-end items-center space-x-3">
          <div>
            <span className="text-xs text-gray-400 block">Detected mood:</span>
            <span className="text-white">😊 Happy</span>
          </div>
          <div className="h-10 w-10 rounded-full border border-green-500 flex items-center justify-center">
            👤
          </div>
        </div>
      </div>
    </div>
  );
}
