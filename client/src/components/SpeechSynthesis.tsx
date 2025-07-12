import { useCallback, useRef, useEffect } from 'react';
import { useToast } from '@/hooks/use-toast';

interface SpeechSynthesisHook {
  speak: (text: string) => void;
  stop: () => void;
  isSpeaking: boolean;
  isSupported: boolean;
}

export const useSpeechSynthesis = (): SpeechSynthesisHook => {
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const { toast } = useToast();
  
  const isSupported = 'speechSynthesis' in window;
  const isSpeaking = isSupported && speechSynthesis.speaking;

  const speak = useCallback((text: string) => {
    if (!isSupported) {
      toast({
        title: "Speech Not Supported",
        description: "Your browser doesn't support text-to-speech.",
        variant: "destructive"
      });
      return;
    }

    // Stop any ongoing speech gracefully
    if (speechSynthesis.speaking) {
      speechSynthesis.cancel();
      // Small delay to ensure previous utterance is fully stopped
      setTimeout(() => {
        startSpeech(text);
      }, 100);
    } else {
      startSpeech(text);
    }
  }, [isSupported, toast]);

  const startSpeech = useCallback((text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Configure voice settings for a warm, calming effect
    utterance.rate = 0.9; // Slightly slower for calm delivery
    utterance.pitch = 1.1; // Slightly higher pitch for friendliness
    utterance.volume = 0.8; // Comfortable volume
    
    // Try to select a female voice for warmth
    const voices = speechSynthesis.getVoices();
    const preferredVoice = voices.find(voice => 
      voice.lang.startsWith('en') && 
      (voice.name.toLowerCase().includes('female') || 
       voice.name.toLowerCase().includes('woman') ||
       voice.name.toLowerCase().includes('sarah') ||
       voice.name.toLowerCase().includes('samantha') ||
       voice.name.toLowerCase().includes('alex'))
    ) || voices.find(voice => voice.lang.startsWith('en') && voice.default);
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onerror = (event) => {
      // Only log non-interrupted errors to avoid spam
      if (event.error !== 'interrupted') {
        console.error('Speech synthesis error:', event.error);
        toast({
          title: "Speech Error",
          description: "There was an issue with text-to-speech.",
          variant: "destructive"
        });
      }
    };

    utterance.onend = () => {
      utteranceRef.current = null;
    };

    utteranceRef.current = utterance;
    speechSynthesis.speak(utterance);
  }, [toast]);

  const stop = useCallback(() => {
    if (isSupported) {
      speechSynthesis.cancel();
    }
  }, [isSupported]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (isSupported) {
        speechSynthesis.cancel();
      }
    };
  }, [isSupported]);

  return {
    speak,
    stop,
    isSpeaking,
    isSupported
  };
};