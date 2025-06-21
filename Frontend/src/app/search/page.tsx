"use client";

import React, { useState } from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import Player from '@/components/Player';

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');
  
  // Mock search categories
  const searchCategories = [
    { name: 'Happy', color: 'from-yellow-400 to-orange-500' },
    { name: 'Chill', color: 'from-blue-400 to-indigo-500' },
    { name: 'Focus', color: 'from-green-400 to-emerald-500' },
    { name: 'Energetic', color: 'from-red-400 to-pink-500' },
    { name: 'Sad', color: 'from-purple-400 to-violet-500' },
    { name: 'Workout', color: 'from-orange-400 to-red-500' },
    { name: 'Party', color: 'from-pink-400 to-purple-500' },
    { name: 'Sleep', color: 'from-indigo-400 to-blue-500' },
    { name: 'Ambient', color: 'from-teal-400 to-cyan-500' },
    { name: 'Jazz', color: 'from-amber-400 to-yellow-500' },
    { name: 'Throwbacks', color: 'from-slate-400 to-gray-500' },
    { name: 'Rap', color: 'from-gray-400 to-slate-500' },
  ];

  return (
    <main className="flex h-screen bg-spotify-black text-white overflow-hidden">
      <Sidebar />
      
      <div className="flex flex-col flex-grow overflow-hidden">
        <Header />
        
        <div className="flex-grow px-8 py-6 overflow-y-auto pb-24">
          <h1 className="text-3xl font-bold mb-8">Search</h1>
          
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4">Browse by mood or feeling</h2>
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-6">
              {searchCategories.map((category, index) => (
                <div key={index} className={`p-5 rounded-lg bg-gradient-to-br ${category.color} hover:shadow-lg transition-shadow cursor-pointer`}>
                  <h3 className="font-bold text-lg">{category.name}</h3>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4">Recommended emotions for you</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {['Happy', 'Energetic', 'Calm', 'Focused'].map((mood, index) => (
                <div key={index} className="p-4 bg-spotify-light-gray rounded-lg hover:bg-opacity-80 transition-colors cursor-pointer">
                  <div className="w-full aspect-square bg-gradient-to-br from-purple-500 to-blue-500 rounded-md flex items-center justify-center mb-4">
                    <span className="text-5xl">
                      {mood === 'Happy' && '😊'}
                      {mood === 'Energetic' && '🔥'}
                      {mood === 'Calm' && '😌'}
                      {mood === 'Focused' && '🧠'}
                    </span>
                  </div>
                  <h3 className="font-medium">{mood} Playlist</h3>
                  <p className="text-sm text-gray-400">Curated for your {mood.toLowerCase()} moments</p>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4">Based on your camera reactions</h2>
            <p className="text-gray-400 mb-6">Songs that made you smile and nod along</p>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {[1, 2, 3, 4, 5].map((item) => (
                <div key={item} className="p-4 bg-spotify-light-gray rounded-lg hover:bg-opacity-80 transition-colors cursor-pointer">
                  <div className="w-full aspect-square bg-gray-700 rounded-md mb-4"></div>
                  <h3 className="font-medium">Song Title {item}</h3>
                  <p className="text-sm text-gray-400">Artist {item}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <Player />
      </div>
    </main>
  );
}
