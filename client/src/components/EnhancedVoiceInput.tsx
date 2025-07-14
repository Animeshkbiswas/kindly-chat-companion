import React, { useState, useRef, useCallback } from 'react';
import { Mic, MicOff, Square } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';
import RecordRTC from 'recordrtc';

interface EnhancedVoiceInputProps {
  onTranscript: (text: string) => void;
  onStartListening: () => void;
  onStopListening: () => void;
  disabled?: boolean;
  useWhisper?: boolean;
  apiKey?: string;
  language?: string;
}

// Replace BackendSpeechRecognition with RecordRTC-based implementation
class BackendSpeechRecognition {
  private recorder: any = null;
  private stream: MediaStream | null = null;
  private onTranscriptionComplete: (text: string) => void;
  private onError: (error: string) => void;
  private language: string;

  constructor(language: string, onTranscription: (text: string) => void, onError: (error: string) => void) {
    this.language = language;
    this.onTranscriptionComplete = onTranscription;
    this.onError = onError;
  }

  async startRecording() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.recorder = new RecordRTC(this.stream, {
        type: 'audio',
        mimeType: 'audio/webm', // Changed from 'audio/wav' to 'audio/webm'
      });
      this.recorder.startRecording();
    } catch (error) {
      this.onError(`Error accessing microphone: ${error}`);
    }
  }

  stopRecording() {
    if (this.recorder) {
      this.recorder.stopRecording(async () => {
        const wavBlob = this.recorder.getBlob();
        console.log('Recorded audio blob type:', wavBlob.type); // Log the blob type for debugging
        if (this.stream) {
          this.stream.getTracks().forEach(track => track.stop());
        }
        await this.processAudio(wavBlob);
      });
    }
  }

  private async processAudio(wavBlob: Blob) {
    if (!wavBlob || wavBlob.size === 0) {
      this.onError('No audio data recorded');
      return;
    }
    try {
      const result = await apiService.transcribeAudio(wavBlob, {
        language: this.language,
        use_whisper: false, // Use local Vosk model
      });
      this.onTranscriptionComplete(result.text || '');
    } catch (error) {
      this.onError(`Error transcribing audio: ${error}`);
    }
  }
}

export const EnhancedVoiceInput: React.FC<EnhancedVoiceInputProps> = ({
  onTranscript,
  onStartListening,
  onStopListening,
  disabled = false,
  useWhisper = false,
  apiKey,
  language = 'en-US'
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const backendRecognitionRef = useRef<BackendSpeechRecognition | null>(null);
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
      // Dispatch custom events for audio visualization
      document.dispatchEvent(new CustomEvent('userSpeaking', { 
        detail: { audioLevel: 0.5 } 
      }));
    };

    recognition.onresult = (event) => {
      let finalTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        }
      }
      
      if (finalTranscript) {
        onTranscript(finalTranscript.trim());
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
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
    };

    return recognition;
  }, [onTranscript, onStartListening, onStopListening, showError, language]);

  const startListening = useCallback(() => {
    if (disabled) return;

    if (useWhisper) {
      // Use Backend API for speech recognition
      if (!backendRecognitionRef.current) {
        backendRecognitionRef.current = new BackendSpeechRecognition(
          language,
          (text: string) => {
            onTranscript(text);
            setIsListening(false);
            onStopListening();
            document.dispatchEvent(new CustomEvent('userQuiet'));
          },
          (error: string) => {
            showError(error);
            setIsListening(false);
            onStopListening();
            document.dispatchEvent(new CustomEvent('userQuiet'));
          }
        );
      }
      
      backendRecognitionRef.current.startRecording();
      setIsListening(true);
      onStartListening();
      document.dispatchEvent(new CustomEvent('userSpeaking', { 
        detail: { audioLevel: 0.5 } 
      }));
    } else {
      // Use browser Speech Recognition
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
    }
  }, [disabled, useWhisper, apiKey, onTranscript, onStartListening, onStopListening, initializeBrowserSpeechRecognition, isSupported, showError]);

  const stopListening = useCallback(() => {
    if (useWhisper && backendRecognitionRef.current) {
      backendRecognitionRef.current.stopRecording();
    } else if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, [useWhisper]);

  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  if (!isSupported && !useWhisper) {
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
            {useWhisper ? 'Record (Backend)' : 'Speak'}
          </>
        )}
      </Button>
      
      {useWhisper && (
        <span className="text-xs text-blue-600">
          Using backend transcription
        </span>
      )}
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