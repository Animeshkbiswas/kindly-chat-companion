import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface TherapistCharacterProps {
  mood: 'idle' | 'listening' | 'speaking' | 'thinking' | 'happy' | 'concerned';
  isListening?: boolean;
  isSpeaking?: boolean;
  className?: string;
}

export const TherapistCharacter: React.FC<TherapistCharacterProps> = ({
  mood = 'idle',
  isListening = false,
  isSpeaking = false,
  className
}) => {
  const [shouldBlink, setShouldBlink] = useState(true);
  const [mouthMovement, setMouthMovement] = useState(false);

  // Handle speech animation
  useEffect(() => {
    if (isSpeaking) {
      const interval = setInterval(() => {
        setMouthMovement(prev => !prev);
      }, 200);
      return () => clearInterval(interval);
    } else {
      setMouthMovement(false);
    }
  }, [isSpeaking]);

  // Get eye shape based on mood
  const getEyeShape = () => {
    switch (mood) {
      case 'happy':
        return 'M 5 15 Q 15 10 25 15'; // Crescent eyes for happiness
      case 'concerned':
        return 'M 5 12 Q 15 8 25 12'; // Slightly worried eyes
      case 'thinking':
        return 'M 8 12 Q 15 8 22 12'; // Narrowed, contemplative eyes
      default:
        return 'M 5 12 Q 15 8 25 12 Q 15 16 5 12'; // Normal oval eyes
    }
  };

  // Get mouth shape based on mood and speaking state
  const getMouthShape = () => {
    if (isSpeaking && mouthMovement) {
      return 'M 12 22 Q 15 26 18 22'; // Open mouth for speaking
    }
    
    switch (mood) {
      case 'happy':
        return 'M 10 20 Q 15 25 20 20'; // Smile
      case 'concerned':
        return 'M 10 22 Q 15 20 20 22'; // Slight frown
      case 'thinking':
        return 'M 12 21 L 18 21'; // Straight line
      default:
        return 'M 12 21 Q 15 23 18 21'; // Neutral slight smile
    }
  };

  // Get eyebrow position based on mood
  const getEyebrowTransform = () => {
    switch (mood) {
      case 'concerned':
        return 'translate(0, -2) rotate(-5)';
      case 'thinking':
        return 'translate(0, -1) rotate(-2)';
      default:
        return 'translate(0, 0)';
    }
  };

  return (
    <div className={cn(
      'relative flex items-center justify-center',
      'animate-breathe', // Gentle breathing animation
      className
    )}>
      <svg
        width="200"
        height="240"
        viewBox="0 0 200 240"
        className={cn(
          'drop-shadow-lg transition-all duration-300',
          mood === 'thinking' && 'animate-thinking',
          mood === 'happy' && 'animate-float'
        )}
      >
        {/* Character background glow */}
        <defs>
          <radialGradient id="characterGlow" cx="50%" cy="50%" r="60%">
            <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.1" />
            <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="faceGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="hsl(var(--therapy-warm))" />
            <stop offset="100%" stopColor="hsl(var(--therapy-calm))" />
          </linearGradient>
          <linearGradient id="bodyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="hsl(var(--primary))" />
            <stop offset="100%" stopColor="hsl(165 45% 55%)" />
          </linearGradient>
        </defs>

        {/* Background glow */}
        <circle
          cx="100"
          cy="120"
          r="90"
          fill="url(#characterGlow)"
          className="animate-pulse-gentle"
        />

        {/* Body/Lab coat */}
        <ellipse
          cx="100"
          cy="180"
          rx="55"
          ry="45"
          fill="url(#bodyGradient)"
          className="transition-all duration-300"
        />

        {/* Collar */}
        <path
          d="M 70 160 Q 100 150 130 160 L 130 170 Q 100 160 70 170 Z"
          fill="hsl(var(--card))"
          stroke="hsl(var(--border))"
          strokeWidth="1"
        />

        {/* Face */}
        <circle
          cx="100"
          cy="100"
          r="45"
          fill="url(#faceGradient)"
          stroke="hsl(var(--border))"
          strokeWidth="1"
          className="transition-all duration-300"
        />

        {/* Hair */}
        <path
          d="M 60 80 Q 70 55 100 60 Q 130 55 140 80 Q 135 70 100 75 Q 65 70 60 80"
          fill="hsl(210 15% 25%)"
          className="transition-all duration-300"
        />

        {/* Glasses */}
        <g className="transition-all duration-300">
          <circle
            cx="85"
            cy="90"
            r="12"
            fill="none"
            stroke="hsl(210 15% 20%)"
            strokeWidth="2"
          />
          <circle
            cx="115"
            cy="90"
            r="12"
            fill="none"
            stroke="hsl(210 15% 20%)"
            strokeWidth="2"
          />
          <line
            x1="97"
            y1="90"
            x2="103"
            y2="90"
            stroke="hsl(210 15% 20%)"
            strokeWidth="2"
          />
        </g>

        {/* Eyebrows */}
        <g className="transition-all duration-300" transform={getEyebrowTransform()}>
          <path
            d="M 78 82 Q 85 80 92 82"
            fill="none"
            stroke="hsl(210 15% 25%)"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <path
            d="M 108 82 Q 115 80 122 82"
            fill="none"
            stroke="hsl(210 15% 25%)"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </g>

        {/* Eyes */}
        <g className={cn(shouldBlink && 'animate-blink')}>
          <path
            d={getEyeShape()}
            fill="hsl(210 15% 20%)"
            transform="translate(-10, 0)"
            className="transition-all duration-300"
          />
          <path
            d={getEyeShape()}
            fill="hsl(210 15% 20%)"
            transform="translate(20, 0)"
            className="transition-all duration-300"
          />
        </g>

        {/* Nose */}
        <ellipse
          cx="100"
          cy="95"
          rx="2"
          ry="4"
          fill="hsl(var(--therapy-warm))"
          className="transition-all duration-300"
        />

        {/* Mouth */}
        <path
          d={getMouthShape()}
          fill="none"
          stroke="hsl(210 15% 20%)"
          strokeWidth="2"
          strokeLinecap="round"
          className={cn(
            'transition-all duration-200',
            isSpeaking && 'animate-mouth-open'
          )}
        />

        {/* Hands */}
        <g className={cn(
          'transition-all duration-300',
          mood === 'happy' && 'animate-wave'
        )}>
          {/* Left hand */}
          <circle
            cx="60"
            cy="170"
            r="8"
            fill="url(#faceGradient)"
            className="transition-all duration-300"
          />
          {/* Right hand */}
          <circle
            cx="140"
            cy="170"
            r="8"
            fill="url(#faceGradient)"
            className="transition-all duration-300"
          />
        </g>

        {/* Listening indicator */}
        {isListening && (
          <g className="animate-pulse-gentle">
            <circle
              cx="160"
              cy="80"
              r="4"
              fill="hsl(var(--primary))"
            />
            <circle
              cx="170"
              cy="85"
              r="3"
              fill="hsl(var(--primary))"
              opacity="0.7"
            />
            <circle
              cx="180"
              cy="90"
              r="2"
              fill="hsl(var(--primary))"
              opacity="0.5"
            />
          </g>
        )}

        {/* Speaking indicator */}
        {isSpeaking && (
          <g className="animate-pulse">
            <path
              d="M 40 95 Q 30 90 25 95 Q 30 100 40 95"
              fill="hsl(var(--primary))"
              opacity="0.6"
            />
            <path
              d="M 35 100 Q 25 95 20 100 Q 25 105 35 100"
              fill="hsl(var(--primary))"
              opacity="0.4"
            />
          </g>
        )}
      </svg>
    </div>
  );
};