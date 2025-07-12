import { useEffect, useRef, useState, useCallback } from 'react';
import AudioStreamProcessor from '@/utils/AudioStreamProcessor';
import { useToast } from '@/hooks/use-toast';

interface AudioVisualizationData {
  isUserSpeaking: boolean;
  audioLevel: number;
  intensity: 'low' | 'medium' | 'high';
}

export const useAudioVisualization = () => {
  const [audioData, setAudioData] = useState<AudioVisualizationData>({
    isUserSpeaking: false,
    audioLevel: 0,
    intensity: 'low'
  });
  const [isEnabled, setIsEnabled] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const processorRef = useRef<AudioStreamProcessor | null>(null);
  const { toast } = useToast();

  // Check if audio visualization is supported
  useEffect(() => {
    const supported = !!(
      navigator.mediaDevices &&
      navigator.mediaDevices.getUserMedia &&
      (window.AudioContext || (window as any).webkitAudioContext)
    );
    setIsSupported(supported);
  }, []);

  // Event listeners for audio events
  useEffect(() => {
    const handleUserSpeaking = (event: CustomEvent) => {
      setAudioData({
        isUserSpeaking: true,
        audioLevel: event.detail.level,
        intensity: event.detail.intensity
      });
    };

    const handleUserQuiet = (event: CustomEvent) => {
      setAudioData(prev => ({
        ...prev,
        isUserSpeaking: false,
        audioLevel: event.detail.level
      }));
    };

    document.addEventListener('user-speaking', handleUserSpeaking as EventListener);
    document.addEventListener('user-quiet', handleUserQuiet as EventListener);

    return () => {
      document.removeEventListener('user-speaking', handleUserSpeaking as EventListener);
      document.removeEventListener('user-quiet', handleUserQuiet as EventListener);
    };
  }, []);

  const startAudioVisualization = useCallback(async () => {
    if (!isSupported) {
      toast({
        title: "Audio Visualization Not Supported",
        description: "Your browser doesn't support real-time audio visualization.",
        variant: "destructive"
      });
      return false;
    }

    if (processorRef.current) {
      processorRef.current.stop();
    }

    try {
      processorRef.current = new AudioStreamProcessor();
      const success = await processorRef.current.setupAudioStream();
      
      if (success) {
        setIsEnabled(true);
        toast({
          title: "Audio Visualization Started",
          description: "Dr. Sarah can now respond to your voice in real-time!",
        });
        return true;
      } else {
        throw new Error('Failed to setup audio stream');
      }
    } catch (error) {
      console.error('Error starting audio visualization:', error);
      toast({
        title: "Audio Access Error",
        description: "Could not access your microphone. Please check permissions.",
        variant: "destructive"
      });
      return false;
    }
  }, [isSupported, toast]);

  const stopAudioVisualization = useCallback(() => {
    if (processorRef.current) {
      processorRef.current.stop();
      processorRef.current = null;
    }
    setIsEnabled(false);
    setAudioData({
      isUserSpeaking: false,
      audioLevel: 0,
      intensity: 'low'
    });
  }, []);

  const resumeAudioVisualization = useCallback(() => {
    if (processorRef.current) {
      processorRef.current.resume();
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (processorRef.current) {
        processorRef.current.stop();
      }
    };
  }, []);

  return {
    audioData,
    isEnabled,
    isSupported,
    startAudioVisualization,
    stopAudioVisualization,
    resumeAudioVisualization
  };
};