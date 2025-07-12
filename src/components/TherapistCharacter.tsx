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
      return 'M 95 108 Q 100 112 105 108'; // Open mouth for speaking
    }
    
    switch (mood) {
      case 'happy':
        return 'M 92 108 Q 100 115 108 108'; // Smile
      case 'concerned':
        return 'M 92 110 Q 100 106 108 110'; // Slight frown
      case 'thinking':
        return 'M 96 108 L 104 108'; // Straight line
      default:
        return 'M 94 108 Q 100 112 106 108'; // Neutral slight smile
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
          <linearGradient id="skinGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#F4C2A1" />
            <stop offset="100%" stopColor="#E8A87C" />
          </linearGradient>
          <linearGradient id="shirtGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="hsl(var(--primary))" />
            <stop offset="100%" stopColor="hsl(200 60% 45%)" />
          </linearGradient>
          <linearGradient id="hairGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2C1810" />
            <stop offset="100%" stopColor="#1A0F08" />
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

        {/* Body/Shirt */}
        <path
          d="M 100 140 
             C 70 140, 45 160, 45 185
             L 45 220
             C 45 225, 50 230, 55 230
             L 145 230
             C 150 230, 155 225, 155 220
             L 155 185
             C 155 160, 130 140, 100 140 Z"
          fill="url(#shirtGradient)"
          className="transition-all duration-300"
        />

        {/* Neck */}
        <ellipse
          cx="100"
          cy="135"
          rx="12"
          ry="15"
          fill="url(#skinGradient)"
          className="transition-all duration-300"
        />

        {/* Face */}
        <circle
          cx="100"
          cy="100"
          r="42"
          fill="url(#skinGradient)"
          className="transition-all duration-300"
        />

        {/* Hair - Bob cut style */}
        <path
          d="M 100 58
             C 75 55, 58 70, 58 90
             C 58 105, 62 115, 68 120
             L 68 110
             C 68 95, 75 85, 85 80
             L 115 80
             C 125 85, 132 95, 132 110
             L 132 120
             C 138 115, 142 105, 142 90
             C 142 70, 125 55, 100 58 Z"
          fill="url(#hairGradient)"
          className="transition-all duration-300"
        />

        {/* Hair bangs */}
        <path
          d="M 85 75
             C 90 70, 95 68, 100 68
             C 105 68, 110 70, 115 75
             C 110 78, 105 80, 100 80
             C 95 80, 90 78, 85 75 Z"
          fill="url(#hairGradient)"
          className="transition-all duration-300"
        />

        {/* Eyebrows */}
        <g className="transition-all duration-300" transform={getEyebrowTransform()}>
          <ellipse
            cx="87"
            cy="85"
            rx="8"
            ry="2"
            fill="#2C1810"
            className="transition-all duration-300"
          />
          <ellipse
            cx="113"
            cy="85"
            rx="8"
            ry="2"
            fill="#2C1810"
            className="transition-all duration-300"
          />
        </g>

        {/* Eyes */}
        <g className={cn(shouldBlink && 'animate-blink')}>
          {/* Eye whites */}
          <ellipse
            cx="87"
            cy="92"
            rx="8"
            ry="6"
            fill="white"
            className="transition-all duration-300"
          />
          <ellipse
            cx="113"
            cy="92"
            rx="8"
            ry="6"
            fill="white"
            className="transition-all duration-300"
          />
          
          {/* Pupils */}
          <circle
            cx="87"
            cy="92"
            r="3"
            fill="#2C1810"
            className="transition-all duration-300"
          />
          <circle
            cx="113"
            cy="92"
            r="3"
            fill="#2C1810"
            className="transition-all duration-300"
          />
          
          {/* Eye highlights */}
          <circle
            cx="88"
            cy="90"
            r="1"
            fill="white"
            className="transition-all duration-300"
          />
          <circle
            cx="114"
            cy="90"
            r="1"
            fill="white"
            className="transition-all duration-300"
          />
        </g>

        {/* Nose - simplified */}
        <ellipse
          cx="100"
          cy="100"
          rx="1.5"
          ry="3"
          fill="#E8A87C"
          className="transition-all duration-300"
        />

        {/* Mouth */}
        <path
          d={getMouthShape()}
          fill="none"
          stroke="#C97856"
          strokeWidth="2"
          strokeLinecap="round"
          className={cn(
            'transition-all duration-200',
            isSpeaking && 'animate-mouth-open'
          )}
        />

        {/* Listening indicator */}
        {isListening && (
          <g className="animate-pulse-gentle">
            <circle
              cx="160"
              cy="80"
              r="3"
              fill="hsl(var(--primary))"
            />
            <circle
              cx="168"
              cy="85"
              r="2.5"
              fill="hsl(var(--primary))"
              opacity="0.7"
            />
            <circle
              cx="175"
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
              d="M 40 95 Q 32 90 28 95 Q 32 100 40 95"
              fill="hsl(var(--primary))"
              opacity="0.6"
            />
            <path
              d="M 36 100 Q 28 95 24 100 Q 28 105 36 100"
              fill="hsl(var(--primary))"
              opacity="0.4"
            />
          </g>
        )}
      </svg>
    </div>
  );
};