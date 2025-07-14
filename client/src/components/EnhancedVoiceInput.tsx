import React, { useState, useRef, useCallback } from 'react';
import { Mic, Square } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

interface EnhancedVoiceInputProps {
  onTranscript: (text: string) => void;
  onStartListening: () => void;
  onStopListening: () => void;
  setCurrentTranscript?: (text: string) => void; // Add this prop
  disabled?: boolean;
  language?: string;
}

export const EnhancedVoiceInput: React.FC<EnhancedVoiceInputProps> = ({
  onTranscript,
  onStartListening,
  onStopListening,
  setCurrentTranscript, // Destructure the prop
  disabled = false,
  language = 'en-US'
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const { toast } = useToast();

  const showError = useCallback((message: string) => {
    toast({
      title: "Speech Recognition Error",
      description: message,
      variant: "destructive",
    });
  }, [toast]);

  const initializeBrowserSpeechRecognition = useCallback(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setIsSupported(false);
      return null;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = language;

    recognition.onstart = () => {
      setIsListening(true);
      onStartListening();
      document.dispatchEvent(new CustomEvent('userSpeaking', { detail: { audioLevel: 0.5 } }));
    };

    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }
      if (setCurrentTranscript) {
        setCurrentTranscript(finalTranscript + interimTranscript);
      }
      if (finalTranscript) {
        onTranscript(finalTranscript.trim());
      }
    };

    recognition.onerror = (event) => {
      setIsListening(false);
      onStopListening();
      document.dispatchEvent(new CustomEvent('userQuiet'));
      let errorMessage = 'Speech recognition failed';
      switch (event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try speaking again.';
          break;
        case 'audio-capture':
          errorMessage = 'Audio capture failed. Please check your microphone.';
          break;
        case 'not-allowed':
          errorMessage = 'Microphone access denied. Please enable microphone permissions.';
          break;
        case 'network':
          errorMessage = 'Network error occurred. Please check your connection.';
          break;
      }
      showError(errorMessage);
    };

    recognition.onend = () => {
      setIsListening(false);
      onStopListening();
      document.dispatchEvent(new CustomEvent('userQuiet'));
      if (setCurrentTranscript) setCurrentTranscript(''); // Clear preview on end
    };

    return recognition;
  }, [onTranscript, onStartListening, onStopListening, showError, language, setCurrentTranscript]);

  const startListening = useCallback(() => {
    if (disabled) return;
    if (!recognitionRef.current) {
      recognitionRef.current = initializeBrowserSpeechRecognition();
    }
    if (recognitionRef.current && isSupported) {
      try {
        recognitionRef.current.start();
      } catch (error) {
        showError('Failed to start speech recognition');
      }
    } else {
      showError('Speech recognition is not supported in this browser');
    }
  }, [disabled, initializeBrowserSpeechRecognition, isSupported, showError]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  if (!isSupported) {
    return (
      <div className="text-sm text-muted-foreground p-2 rounded-md bg-muted">
        Speech recognition not supported in this browser
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <Button
        type="button"
        variant={isListening ? "destructive" : "outline"}
        size="sm"
        onClick={toggleListening}
        disabled={disabled}
        className={`transition-all duration-200 ${
          isListening 
            ? 'bg-red-500 hover:bg-red-600 pulse' 
            : 'hover:bg-primary/10'
        }`}
      >
        {isListening ? (
          <>
            <Square className="w-4 h-4 mr-1" />
            Stop
          </>
        ) : (
          <>
            <Mic className="w-4 h-4 mr-1" />
            Speak
          </>
        )}
      </Button>
    </div>
  );
};

// Add pulse animation styles
const styles = `
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.7;
    }
  }
  
  .pulse {
    animation: pulse 1.5s ease-in-out infinite;
  }
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);
}