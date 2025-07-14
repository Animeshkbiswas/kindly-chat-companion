import { useCallback, useRef, useEffect } from 'react';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';

interface SpeechSynthesisHook {
  speak: (text: string, settings?: SpeechSettings) => void;
  stop: () => void;
  isSpeaking: boolean;
  isSupported: boolean;
}

interface SpeechSettings {
  rate?: number;
  pitch?: number;
  language?: string;
  voiceEnabled?: boolean;
  useBackend?: boolean;
}

export const useSpeechSynthesis = (): SpeechSynthesisHook => {
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const { toast } = useToast();
  
  const isSupported = 'speechSynthesis' in window;
  const isSpeaking = isSupported && speechSynthesis.speaking;

  const speak = useCallback(async (text: string, settings: SpeechSettings = {}) => {
    // Check if voice is disabled
    if (settings.voiceEnabled === false) {
      return;
    }

    // Use backend TTS if specified
    if (settings.useBackend) {
      try {
        const response = await apiService.textToSpeech({
          text,
          voice: 'sarah', // Default voice
          speed: settings.rate ? settings.rate / 100 : 1.0,
        });
        
        // Play the audio from the backend
        const audio = new Audio(response.audio_url);
        audio.play();
        
        return;
      } catch (error) {
        console.error('Backend TTS error:', error);
        toast({
          title: "TTS Error",
          description: "Failed to generate speech from backend. Falling back to browser TTS.",
          variant: "destructive"
        });
        // Fall back to browser TTS
      }
    }

    // Use browser TTS
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
        startSpeech(text, settings);
      }, 100);
    } else {
      startSpeech(text, settings);
    }
  }, [isSupported, toast]);

  const startSpeech = useCallback((text: string, settings: SpeechSettings = {}) => {
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Apply user settings or defaults
    utterance.rate = settings.rate || 0.9;
    utterance.pitch = settings.pitch || 1.1;
    utterance.volume = 0.8; // Keep comfortable volume
    
    // Select voice based on language preference
    const voices = speechSynthesis.getVoices();
    const targetLanguage = settings.language || 'en-US';
    const languageCode = targetLanguage.split('-')[0];
    
    // Find the best voice for the selected language
    let preferredVoice = voices.find(voice => 
      voice.lang === targetLanguage && 
      (voice.name.toLowerCase().includes('female') || 
       voice.name.toLowerCase().includes('woman') ||
       voice.name.toLowerCase().includes('sarah') ||
       voice.name.toLowerCase().includes('samantha'))
    );
    
    // Fallback to any voice in the language
    if (!preferredVoice) {
      preferredVoice = voices.find(voice => voice.lang.startsWith(languageCode));
    }
    
    // Final fallback to default voice
    if (!preferredVoice) {
      preferredVoice = voices.find(voice => voice.default);
    }
    
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