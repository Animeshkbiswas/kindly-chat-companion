// API service for communicating with the backend FastAPI server

const API_BASE_URL = 'http://localhost:8000';

interface ChatRequest {
  message: string;
  session_id?: number;
  user_id?: number;
  therapist_personality?: string;
  language?: string;
}

interface ChatResponse {
  response: string;
  session_id: number;
  message_id: number;
  character_mood: 'idle' | 'listening' | 'speaking' | 'thinking' | 'happy' | 'concerned';
  audio_url?: string;
  session_title?: string;
}

interface AudioTranscriptionRequest {
  language?: string;
  use_whisper?: boolean;
}

interface AudioTranscriptionResponse {
  text: string;
  confidence?: number;
  duration?: number;
}

interface TextToSpeechRequest {
  text: string;
  voice?: string;
  speed?: number;
}

interface TextToSpeechResponse {
  audio_url: string;
  duration?: number;
  file_size?: number;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
    }

    return response.json();
  }

  // Chat endpoints
  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/api/messages/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getSessionMessages(sessionId: number): Promise<any[]> {
    return this.request<any[]>(`/api/messages/${sessionId}`);
  }

  // Audio endpoints
  async transcribeAudio(audioBlob: Blob, request: AudioTranscriptionRequest = {}): Promise<AudioTranscriptionResponse> {
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.webm');
    formData.append('language', request.language || 'en-US');
    formData.append('use_whisper', request.use_whisper ? 'true' : 'false');

    const url = `${this.baseUrl}/api/audio/transcribe`;
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Audio transcription failed: ${response.status} ${response.statusText} - ${errorText}`);
    }

    return response.json();
  }

  async textToSpeech(request: TextToSpeechRequest): Promise<TextToSpeechResponse> {
    return this.request<TextToSpeechResponse>('/api/audio/synthesize', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }



  // Health check
  async healthCheck(): Promise<any> {
    return this.request('/health');
  }
}

// Export a singleton instance
export const apiService = new ApiService();

// Export types for use in components
export type {
  ChatRequest,
  ChatResponse,
  AudioTranscriptionRequest,
  AudioTranscriptionResponse,
  TextToSpeechRequest,
  TextToSpeechResponse,
}; 