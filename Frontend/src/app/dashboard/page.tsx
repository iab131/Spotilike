"use client";

import React from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import Player from '@/components/Player';
import MoodPlaylist from '@/components/MoodPlaylist';

export default function Dashboard() {
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
