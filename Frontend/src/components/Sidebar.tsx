"use client";
import React from 'react';
import Link from 'next/link';

export default function Sidebar() {
  return (
    <div className="bg-black w-64 h-full p-6 flex flex-col">
      <h1 className="text-2xl font-bold mb-8">Spotilike</h1>
      
      <nav className="space-y-2">
        <Link href="/dashboard" className="sidebar-item active">
          <span>Home</span>
        </Link>
        <Link href="/search" className="sidebar-item">
          <span>Search</span>
        </Link>
        <Link href="/library" className="sidebar-item">
          <span>Your Library</span>
        </Link>
      </nav>
      
      <div className="mt-8">
        <h2 className="text-lg font-semibold mb-2">Mood Playlists</h2>
        <div className="space-y-2">
          <Link href="/mood/happy" className="sidebar-item">
            <span>Happy</span>
          </Link>
          <Link href="/mood/calm" className="sidebar-item">
            <span>Calm</span>
          </Link>
          <Link href="/mood/energetic" className="sidebar-item">
            <span>Energetic</span>
          </Link>
          <Link href="/mood/sad" className="sidebar-item">
            <span>Sad</span>
          </Link>
          <Link href="/mood/throwbacks" className="sidebar-item">
            <span>Throwbacks</span>
          </Link>
          <Link href="/mood/rap" className="sidebar-item">
            <span>Rap</span>
          </Link>
        </div>
      </div>
      
      <div className="mt-auto pt-6 border-t border-gray-700">
        <div className="text-sm text-gray-400">
          <p className="mb-16">Camera Detection: Active</p>
          <p>Auto-like feature: On</p>
        </div>
      </div>
    </div>
  );
}
