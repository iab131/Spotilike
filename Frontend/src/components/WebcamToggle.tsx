"use client";
import React, { useState, useEffect } from 'react';

interface WebcamStatus {
  webcam_active: boolean;
  current_emotion: string | null;
}

export default function WebcamToggle() {
  const [webcamStatus, setWebcamStatus] = useState<WebcamStatus>({
    webcam_active: false,
    current_emotion: null
  });
  const [isLoading, setIsLoading] = useState(false);

  // Get emotion emoji
  const getEmotionEmoji = (emotion: string) => {
    switch (emotion?.toLowerCase()) {
      case 'happy':
        return '😊';
      case 'sad':
        return '😢';
      case 'angry':
        return '😠';
      case 'disgust':
        return '🤢';
      case 'neutral':
        return '😐';
      default:
        return '👤';
    }
  };

  // Get emotion color
  const getEmotionColor = (emotion: string) => {
    switch (emotion?.toLowerCase()) {
      case 'happy':
        return 'text-green-500';
      case 'sad':
        return 'text-blue-500';
      case 'angry':
        return 'text-red-500';
      case 'disgust':
        return 'text-yellow-500';
      case 'neutral':
        return 'text-gray-500';
      default:
        return 'text-gray-400';
    }
  };

  // Fetch webcam status
  const fetchWebcamStatus = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5001/api/webcam/status');
      if (response.ok) {
        const data = await response.json();
        setWebcamStatus(data);
      }
    } catch (err) {
      console.error('Error fetching webcam status:', err);
    }
  };

  // Toggle webcam
  const toggleWebcam = async () => {
    setIsLoading(true);
    try {
      const endpoint = webcamStatus.webcam_active ? 'stop' : 'start';
      const response = await fetch(`http://127.0.0.1:5001/api/webcam/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        // Refresh status after toggle
        setTimeout(fetchWebcamStatus, 1000);
      }
    } catch (err) {
      console.error('Error toggling webcam:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Poll for status updates
  useEffect(() => {
    fetchWebcamStatus();
    const interval = setInterval(fetchWebcamStatus, 3000); // Check every 3 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-spotify-light-gray bg-opacity-30 rounded-lg p-6 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <div className={`w-12 h-12 rounded-full border-2 flex items-center justify-center ${
              webcamStatus.webcam_active 
                ? 'border-green-500 bg-green-500 bg-opacity-20' 
                : 'border-gray-500 bg-gray-500 bg-opacity-20'
            }`}>
              {webcamStatus.webcam_active ? (
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              ) : (
                <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
              )}
            </div>
            {webcamStatus.webcam_active && (
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full animate-pulse"></div>
            )}
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-white">
              Mood Detection
            </h3>
            <p className="text-sm text-gray-400">
              {webcamStatus.webcam_active 
                ? 'Camera active - detecting emotions' 
                : 'Camera inactive - click to start'
              }
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Current Emotion Display */}
          {webcamStatus.webcam_active && webcamStatus.current_emotion && (
            <div className="text-center">
              <div className={`text-2xl ${getEmotionColor(webcamStatus.current_emotion)}`}>
                {getEmotionEmoji(webcamStatus.current_emotion)}
              </div>
              <p className={`text-xs capitalize ${getEmotionColor(webcamStatus.current_emotion)}`}>
                {webcamStatus.current_emotion}
              </p>
            </div>
          )}

          {/* Toggle Button */}
          <button
            onClick={toggleWebcam}
            disabled={isLoading}
            className={`px-6 py-2 rounded-full font-medium transition-all duration-200 ${
              webcamStatus.webcam_active
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-green-500 hover:bg-green-600 text-white'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isLoading ? (
              <span className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Loading...</span>
              </span>
            ) : (
              <span className="flex items-center space-x-2">
                {webcamStatus.webcam_active ? (
                  <>
                    <span>📷</span>
                    <span>Stop Camera</span>
                  </>
                ) : (
                  <>
                    <span>📷</span>
                    <span>Start Camera</span>
                  </>
                )}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Status Info */}
      {webcamStatus.webcam_active && (
        <div className="mt-4 p-3 bg-green-500 bg-opacity-10 border border-green-500 border-opacity-30 rounded-lg">
          <div className="flex items-center space-x-2 text-sm text-green-400">
            <span>🔄</span>
            <span>Mood detection active - emotions are being tracked and saved to database</span>
          </div>
        </div>
      )}
    </div>
  );
} 