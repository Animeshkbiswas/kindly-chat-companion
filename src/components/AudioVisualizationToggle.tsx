import React from 'react';
import { Waves, VolumeX } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface AudioVisualizationToggleProps {
  isEnabled: boolean;
  isSupported: boolean;
  onToggle: () => void;
  disabled?: boolean;
}

export const AudioVisualizationToggle: React.FC<AudioVisualizationToggleProps> = ({
  isEnabled,
  isSupported,
  onToggle,
  disabled = false
}) => {
  if (!isSupported) {
    return null;
  }

  return (
    <Button
      variant={isEnabled ? "default" : "outline"}
      size="icon"
      onClick={onToggle}
      disabled={disabled}
      className={cn(
        'transition-all duration-300',
        isEnabled && 'animate-pulse-gentle shadow-warm',
        !isEnabled && 'shadow-gentle hover:shadow-soft hover:scale-105'
      )}
      aria-label={isEnabled ? 'Disable real-time audio visualization' : 'Enable real-time audio visualization'}
    >
      {isEnabled ? (
        <Waves className="w-4 h-4" />
      ) : (
        <VolumeX className="w-4 h-4" />
      )}
    </Button>
  );
};