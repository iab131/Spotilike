"use client";
import React, { useState, useRef } from 'react';

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoadingDistance, setIsLoadingDistance] = useState(false);
  const [sliderValue, setSliderValue] = useState(50);
  const [autoVolume, setAutoVolume] = useState(false);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const ensureCameraOn = async () => {
    const statusResp = await fetch('http://127.0.0.1:5001/api/webcam/status');
    const statusData = await statusResp.json();
    if (!statusData.webcam_active) {
      await fetch('http://127.0.0.1:5001/api/webcam/start', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
      // Wait for camera to become active (poll every 500ms, up to 5s)
      let waited = 0;
      while (waited < 5000) {
        await new Promise(res => setTimeout(res, 500));
        const pollResp = await fetch('http://127.0.0.1:5001/api/webcam/status');
        const pollData = await pollResp.json();
        if (pollData.webcam_active) break;
        waited += 500;
      }
    }
  };

  const handleAutoVolumeToggle = async () => {
    if (!autoVolume) {
      setIsLoadingDistance(true);
      await ensureCameraOn();
      setIsLoadingDistance(false);
      setAutoVolume(true);
      // Start polling every 2 seconds
      pollingRef.current = setInterval(async () => {
        try {
          const response = await fetch('http://127.0.0.1:5001/api/face-distance');
          const data = await response.json();
          if (data && data.distance_cm != null && data.volume != null) {
            const adjustResp = await fetch('http://127.0.0.1:5001/api/adjust-volume', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
            const adjustData = await adjustResp.json();
            if (adjustData && adjustData.volume != null) {
              setSliderValue(adjustData.volume);
            }
          }
        } catch (err) {
          // Optionally show an error
        }
      }, 2000);
    } else {
      setAutoVolume(false);
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
      // Turn off the camera
      await fetch('http://127.0.0.1:5001/api/webcam/stop', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
    }
  };

  const handleSliderChange = async (value: number) => {
    setSliderValue(value);
    try {
      await fetch('http://127.0.0.1:5001/api/set-spotify-volume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ volume: value })
      });
    } catch (err) {
      // Optionally show an error
    }
  };

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
            value={sliderValue}
            onChange={e => handleSliderChange(Number(e.target.value))}
          />
          <button
            className={`ml-1 px-4 py-2 rounded-full font-medium transition-all duration-200 ${autoVolume ? 'bg-green-500 text-white' : 'bg-gray-600 text-white'} opacity-70 hover:opacity-100 text-sm`}
            onClick={handleAutoVolumeToggle}
            disabled={isLoadingDistance}
          >
            <span className="sr-only">Auto-adjust volume</span>
            {isLoadingDistance ? '⏳' : (autoVolume ? '📏 On' : '📏 Off')}
          </button>
        </div>

      </div>
    </header>
  );
}
