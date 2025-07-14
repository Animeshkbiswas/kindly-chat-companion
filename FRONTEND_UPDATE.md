# Frontend Update: Backend API Integration

This document describes the changes made to update the frontend to use the backend FastAPI server instead of calling OpenAI directly.

## Changes Made

### 1. New API Service (`client/src/lib/api.ts`)

Created a centralized API service that handles all communication with the backend:

- **Chat endpoints**: Send messages and get AI responses
- **Audio endpoints**: Speech-to-text and text-to-speech
- **Session management endpoints**: Create and manage therapy sessions
- **Health check**: Verify backend connectivity

### 2. Updated TherapyChat Component

- **Removed OpenAI dependency**: No longer calls OpenAI directly
- **Uses backend chat endpoint**: `/api/messages/chat`
- **Backend TTS**: Uses local pyttsx3 for text-to-speech
- **Fallback responses**: Still available if backend is unavailable

### 3. Updated EnhancedVoiceInput Component

- **Backend STT**: Uses local Vosk model for speech-to-text
- **Removed OpenAI Whisper**: No longer requires OpenAI API key
- **Browser fallback**: Still supports browser speech recognition

### 4. Updated SpeechSynthesis Component

- **Backend TTS support**: Can use local pyttsx3 via backend
- **Browser fallback**: Falls back to browser TTS if backend fails
- **Configurable**: Can choose between backend and browser TTS

### 5. Updated TherapyChat Component

- **Uses apiService**: All API calls now go through the centralized service
- **Consistent error handling**: Better error messages and fallbacks
- **Type safety**: Improved TypeScript support

## Configuration

The frontend is configured to connect to the backend at `http://localhost:8000` by default. No environment file is required.

If you need to change the backend URL, edit `client/src/lib/api.ts` and update the `API_BASE_URL` constant.

### Backend Requirements

Ensure your backend is running with:

1. **Local LLM**: DeepSeek or other local model configured
2. **Audio services**: Vosk for STT, pyttsx3 for TTS
3. **Database**: SQLite or PostgreSQL with proper migrations
4. **CORS**: Configured to allow frontend requests

## Usage

### Starting the Application

1. **Start the backend**:
   ```bash
   cd backend
   python run.py
   ```

2. **Start the frontend**:
   ```bash
   cd client
   npm run dev
   ```

3. **Access the application**: http://localhost:5173

### Features

- **Therapy Chat**: Full conversation with local LLM
- **Therapy Sessions**: Persistent conversation history
- **Voice Input**: Speech-to-text using local Vosk model
- **Voice Output**: Text-to-speech using local pyttsx3
- **Session Management**: Persistent chat sessions
- **Report Generation**: Clinical reports and analysis

## Benefits

1. **Privacy**: All processing happens locally
2. **Cost**: No external API costs
3. **Reliability**: No dependency on external services
4. **Customization**: Full control over models and responses
5. **Offline**: Works without internet connection

## Troubleshooting

### Backend Connection Issues

1. **Check backend URL**: Verify backend is running on `http://localhost:8000`
2. **CORS errors**: Ensure backend allows frontend origin
3. **Port conflicts**: Make sure backend is running on port 8000

### Audio Issues

1. **Microphone permissions**: Allow browser microphone access
2. **Vosk model**: Ensure Vosk model is downloaded and configured
3. **pyttsx3**: Check if text-to-speech is working on your system

### LLM Issues

1. **Model loading**: Check backend logs for model loading errors
2. **Memory**: Ensure sufficient RAM for local LLM
3. **Fallback**: Check if fallback responses are working

## Migration Notes

- **OpenAI dependency removed**: No longer requires OpenAI API key
- **Local processing**: All AI processing happens on your server
- **Better error handling**: More informative error messages
- **Type safety**: Improved TypeScript support throughout
- **Consistent API**: All endpoints use the same service pattern 