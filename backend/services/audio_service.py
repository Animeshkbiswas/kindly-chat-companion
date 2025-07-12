"""
Audio Service for transcription and text-to-speech
Handles OpenAI Whisper, browser audio, and TTS functionality.
"""

import os
import io
import tempfile
import hashlib
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
import httpx

from core.config import get_settings

settings = get_settings()


class AudioService:
    """Audio processing service for therapy chat"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.audio_dir = settings.audio_upload_dir
        self._ensure_audio_dir()
    
    def _ensure_audio_dir(self):
        """Ensure audio upload directory exists"""
        os.makedirs(self.audio_dir, exist_ok=True)
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        filename: str,
        language: str = "en-US",
        use_whisper: bool = False
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text
        Falls back to local transcription if OpenAI is unavailable
        """
        
        if use_whisper and self.openai_client:
            try:
                return await self._transcribe_with_whisper(audio_data, filename, language)
            except Exception as e:
                print(f"Whisper transcription failed: {e}")
                # Fall back to local transcription
        
        # Browser-based transcription (placeholder - would integrate with Web Speech API)
        return await self._transcribe_locally(audio_data, filename, language)
    
    async def _transcribe_with_whisper(
        self,
        audio_data: bytes,
        filename: str,
        language: str
    ) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe with Whisper
            with open(temp_file_path, 'rb') as audio_file:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language.split('-')[0] if '-' in language else language,
                    response_format="verbose_json"
                )
            
            return {
                "text": transcript.text,
                "confidence": getattr(transcript, 'confidence', None),
                "duration": getattr(transcript, 'duration', None)
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    async def _transcribe_locally(
        self,
        audio_data: bytes,
        filename: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Local transcription fallback
        In production, this would integrate with speech recognition libraries
        """
        
        # For now, return a placeholder response
        # In a real implementation, you could use:
        # - speech_recognition library with Google/Sphinx
        # - Mozilla DeepSpeech
        # - wav2vec2 models
        
        return {
            "text": "Audio transcription not available. Please enable OpenAI Whisper or use browser speech recognition.",
            "confidence": 0.0,
            "duration": None
        }
    
    async def synthesize_speech(
        self,
        text: str,
        voice: str = "alloy",
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Convert text to speech and save to file
        Returns audio file URL
        """
        
        if self.openai_client:
            try:
                return await self._synthesize_with_openai(text, voice, speed)
            except Exception as e:
                print(f"OpenAI TTS failed: {e}")
        
        # Fallback to browser TTS (placeholder)
        return await self._synthesize_locally(text, voice, speed)
    
    async def _synthesize_with_openai(
        self,
        text: str,
        voice: str,
        speed: float
    ) -> Dict[str, Any]:
        """Synthesize speech using OpenAI TTS"""
        
        # Generate speech
        response = await self.openai_client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=speed
        )
        
        # Save to file
        file_id = self._generate_file_id(text, voice, speed)
        file_path = os.path.join(self.audio_dir, f"{file_id}.mp3")
        
        with open(file_path, 'wb') as f:
            async for chunk in response.iter_bytes():
                f.write(chunk)
        
        file_size = os.path.getsize(file_path)
        
        return {
            "audio_url": f"/api/audio/file/{file_id}",
            "file_path": file_path,
            "file_size": file_size,
            "duration": None  # Could be calculated if needed
        }
    
    async def _synthesize_locally(
        self,
        text: str,
        voice: str,
        speed: float
    ) -> Dict[str, Any]:
        """
        Local TTS fallback
        Returns browser TTS instructions
        """
        
        # For browser-based TTS, we return instructions for client-side synthesis
        return {
            "audio_url": None,
            "browser_tts": True,
            "text": text,
            "voice": voice,
            "speed": speed,
            "message": "Using browser text-to-speech. Enable OpenAI TTS for better quality."
        }
    
    async def synthesize_speech_stream(
        self,
        text: str,
        voice: str = "alloy",
        speed: float = 1.0
    ) -> bytes:
        """
        Convert text to speech and return audio data for streaming
        """
        
        if self.openai_client:
            try:
                response = await self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text,
                    speed=speed
                )
                
                # Collect all audio data
                audio_data = b""
                async for chunk in response.iter_bytes():
                    audio_data += chunk
                
                return audio_data
                
            except Exception as e:
                print(f"OpenAI TTS streaming failed: {e}")
        
        # Fallback - return empty audio
        return b""
    
    async def get_audio_file_path(self, file_id: str) -> Optional[str]:
        """Get file path for audio file ID"""
        file_path = os.path.join(self.audio_dir, f"{file_id}.mp3")
        return file_path if os.path.exists(file_path) else None
    
    async def delete_audio_file(self, file_id: str) -> bool:
        """Delete audio file"""
        file_path = os.path.join(self.audio_dir, f"{file_id}.mp3")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    async def get_available_voices(self) -> List[Dict[str, str]]:
        """Get list of available TTS voices"""
        
        # OpenAI TTS voices
        openai_voices = [
            {"id": "alloy", "name": "Alloy", "provider": "openai"},
            {"id": "echo", "name": "Echo", "provider": "openai"},
            {"id": "fable", "name": "Fable", "provider": "openai"},
            {"id": "onyx", "name": "Onyx", "provider": "openai"},
            {"id": "nova", "name": "Nova", "provider": "openai"},
            {"id": "shimmer", "name": "Shimmer", "provider": "openai"},
        ]
        
        # Browser voices (placeholder)
        browser_voices = [
            {"id": "browser-female", "name": "Browser Female", "provider": "browser"},
            {"id": "browser-male", "name": "Browser Male", "provider": "browser"},
        ]
        
        return openai_voices + browser_voices
    
    def _generate_file_id(self, text: str, voice: str, speed: float) -> str:
        """Generate unique file ID for audio content"""
        content = f"{text}_{voice}_{speed}"
        return hashlib.md5(content.encode()).hexdigest()


# Global audio service instance
audio_service = AudioService()