"use client";
import React, { useState, useEffect } from 'react';
import Image from 'next/image';

interface Track {
  id: string;
  name: string;
  artists: string[];
  album: string;
  album_art: string;
  duration_ms: number;
  progress_ms: number;
  uri: string;
}

interface PlaybackInfo {
  is_playing: boolean;
  track: Track;
  device: {
    name: string;
    type: string;
  };
}

interface PlaybackState {
  shuffle_state: boolean;
  repeat_state: 'off' | 'track' | 'context';
}

export default function Player() {
  const [playbackInfo, setPlaybackInfo] = useState<PlaybackInfo | null>(null);
  const [playbackState, setPlaybackState] = useState<PlaybackState>({
    shuffle_state: false,
    repeat_state: 'off'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Format milliseconds to MM:SS
  const formatTime = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // Calculate progress percentage
  const getProgressPercentage = () => {
    if (!playbackInfo?.track) return 0;
    return (playbackInfo.track.progress_ms / playbackInfo.track.duration_ms) * 100;
  };

  // Get repeat button icon based on state
  const getRepeatIcon = () => {
    switch (playbackState.repeat_state) {
      case 'track':
        return '🔂'; // Single track repeat
      case 'context':
        return '🔁'; // Playlist repeat
      default:
        return '🔁'; // No repeat
    }
  };

  // Get repeat button color based on state
  const getRepeatColor = () => {
    switch (playbackState.repeat_state) {
      case 'track':
        return 'text-green-500'; // Active - green
      case 'context':
        return 'text-green-500'; // Active - green
      default:
        return 'text-gray-400 hover:text-white'; // Inactive
    }
  };

  // Fetch current playback info
  const fetchPlaybackInfo = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5001/api/current-playback');
      if (response.ok) {
        const data = await response.json();
        if (data.is_playing !== undefined) {
          setPlaybackInfo(data);
        }
      } else {
        setError('Failed to fetch playback info');
      }
    } catch (err) {
      setError('Error connecting to server');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch playback state (shuffle, repeat)
  const fetchPlaybackState = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5001/api/playback/state');
      if (response.ok) {
        const data = await response.json();
        setPlaybackState(data);
      }
    } catch (err) {
      console.error('Error fetching playback state:', err);
    }
  };

  // Control playback
  const controlPlayback = async (action: 'play' | 'pause' | 'next' | 'previous') => {
    try {
      const response = await fetch(`http://127.0.0.1:5001/api/playback/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        // Refresh playback info after control action
        setTimeout(() => {
          fetchPlaybackInfo();
          fetchPlaybackState();
        }, 500);
      }
    } catch (err) {
      console.error(`Error controlling playback: ${err}`);
    }
  };

  // Toggle shuffle
  const toggleShuffle = async () => {
    try {
      const newState = !playbackState.shuffle_state;
      const response = await fetch('http://127.0.0.1:5001/api/playback/shuffle', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ state: newState }),
      });
      
      if (response.ok) {
        setPlaybackState(prev => ({ ...prev, shuffle_state: newState }));
      }
    } catch (err) {
      console.error('Error toggling shuffle:', err);
    }
  };

  // Cycle through repeat modes
  const cycleRepeat = async () => {
    try {
      const repeatModes: ('off' | 'track' | 'context')[] = ['off', 'context', 'track'];
      const currentIndex = repeatModes.indexOf(playbackState.repeat_state);
      const nextIndex = (currentIndex + 1) % repeatModes.length;
      const newState = repeatModes[nextIndex];
      
      const response = await fetch('http://127.0.0.1:5001/api/playback/repeat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ state: newState }),
      });
      
      if (response.ok) {
        setPlaybackState(prev => ({ ...prev, repeat_state: newState }));
      }
    } catch (err) {
      console.error('Error cycling repeat:', err);
    }
  };

  // Seek to position
  const handleSeek = async (percentage: number) => {
    if (!playbackInfo?.track) return;
    
    const positionMs = Math.floor((percentage / 100) * playbackInfo.track.duration_ms);
    
    try {
      await fetch('http://127.0.0.1:5001/api/playback/seek', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ position_ms: positionMs }),
      });
      
      // Refresh playback info after seeking
      setTimeout(fetchPlaybackInfo, 500);
    } catch (err) {
      console.error('Error seeking:', err);
    }
  };

  // Fetch playback info on mount and set up polling
  useEffect(() => {
    fetchPlaybackInfo();
    fetchPlaybackState();
    
    // Poll for updates every 2 seconds
    const interval = setInterval(() => {
      fetchPlaybackInfo();
      fetchPlaybackState();
    }, 2000);
    
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="bg-spotify-light-gray border-t border-gray-700 p-4 fixed bottom-0 left-0 right-0">
        <div className="text-center text-gray-400">Loading player...</div>
      </div>
    );
  }

  if (error || !playbackInfo) {
    return (
      <div className="bg-spotify-light-gray border-t border-gray-700 p-4 fixed bottom-0 left-0 right-0">
        <div className="text-center text-gray-400">
          {error || 'No track currently playing'}
        </div>
      </div>
    );
  }

  const { track, is_playing } = playbackInfo;
  const progressPercentage = getProgressPercentage();

  return (
    <div className="bg-spotify-light-gray border-t border-gray-700 p-4 fixed bottom-0 left-0 right-0">
      <div className="flex items-center justify-between">
        {/* Song info */}
        <div className="flex items-center space-x-4 w-1/4">
          <div className="w-14 h-14 bg-gray-600 rounded overflow-hidden">
            {track.album_art ? (
              <Image
                src={track.album_art}
                alt={track.album}
                width={56}
                height={56}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                🎵
              </div>
            )}
          </div>
          <div className="min-w-0 flex-1">
            <h4 className="text-white font-medium truncate">{track.name}</h4>
            <p className="text-gray-400 text-sm truncate">
              {track.artists.join(', ')}
            </p>
          </div>
          <button className="text-gray-400 hover:text-white">
            <span className="sr-only">Like</span>
            ❤️
          </button>
        </div>
        
        {/* Player controls */}
        <div className="flex flex-col items-center w-2/4">
          <div className="flex items-center space-x-4 mb-2">
            <button 
              className={`${playbackState.shuffle_state ? 'text-green-500' : 'text-gray-400 hover:text-white'}`}
              onClick={toggleShuffle}
              title={playbackState.shuffle_state ? 'Shuffle On' : 'Shuffle Off'}
            >
              <span className="sr-only">Shuffle</span>
              🔀
            </button>
            <button 
              className="text-gray-400 hover:text-white"
              onClick={() => controlPlayback('previous')}
            >
              <span className="sr-only">Previous</span>
              ⏮️
            </button>
            <button 
              className="bg-white text-black rounded-full w-8 h-8 flex items-center justify-center hover:scale-110 transition-transform"
              onClick={() => controlPlayback(is_playing ? 'pause' : 'play')}
            >
              <span className="sr-only">{is_playing ? 'Pause' : 'Play'}</span>
              {is_playing ? '⏸️' : '▶️'}
            </button>
            <button 
              className="text-gray-400 hover:text-white"
              onClick={() => controlPlayback('next')}
            >
              <span className="sr-only">Next</span>
              ⏭️
            </button>
            <button 
              className={`${getRepeatColor()}`}
              onClick={cycleRepeat}
              title={`Repeat: ${playbackState.repeat_state}`}
            >
              <span className="sr-only">Repeat</span>
              {getRepeatIcon()}
            </button>
          </div>
          
          <div className="w-full flex items-center space-x-2">
            <span className="text-xs text-gray-400">
              {formatTime(track.progress_ms)}
            </span>
            <div 
              className="flex-grow bg-gray-600 h-1 rounded-full relative cursor-pointer"
              onClick={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const percentage = (clickX / rect.width) * 100;
                handleSeek(percentage);
              }}
            >
              <div 
                className="absolute left-0 top-0 bottom-0 bg-white rounded-full transition-all duration-300"
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
            <span className="text-xs text-gray-400">
              {formatTime(track.duration_ms)}
            </span>
          </div>
        </div>
        
        {/* Device info */}
        <div className="w-1/4 flex justify-end items-center space-x-3">
          <div className="text-right">
            <span className="text-xs text-gray-400 block">Playing on:</span>
            <span className="text-white text-sm">{playbackInfo.device.name || 'Unknown device'}</span>
          </div>
          <div className="h-10 w-10 rounded-full border border-green-500 flex items-center justify-center">
            👤
          </div>
        </div>
      </div>
    </div>
  );
}
