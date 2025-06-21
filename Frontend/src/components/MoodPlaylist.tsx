"use client";
import React from 'react';

export default function MoodPlaylist({ title, songs }: { title: string; songs: any[] }) {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">{title}</h2>
        <button className="text-sm text-gray-400 hover:text-white">
          See all
        </button>
      </div>
      
      <div className="grid grid-cols-5 gap-6">
        {songs.map((song, index) => (
          <div key={index} className="bg-spotify-light-gray rounded-md p-4 hover:bg-gray-700 transition-colors">
            <div className="w-full aspect-square bg-gray-700 mb-4 relative">
              {/* This would be the song/album image */}
              <button 
                className="absolute right-2 bottom-2 bg-spotify-green rounded-full w-10 h-10 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
              >
                ▶️
              </button>
            </div>
            <h3 className="font-medium text-white mb-1 truncate">{song.title}</h3>
            <p className="text-sm text-gray-400 truncate">{song.artist}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
