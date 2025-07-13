"""
Audio Service for transcription and text-to-speech
Handles OpenAI Whisper, browser audio, and TTS functionality.
"""

import os
import io
import tempfile
import hashlib
from typing import Dict, Any, Optional, List
import pyttsx3
import wave
import vosk
import json

from core.config import get_settings

settings = get_settings()

class AudioService:
    """Audio processing service for therapy chat (local only)"""
    def __init__(self):
        self.audio_dir = settings.audio_upload_dir
        self._ensure_audio_dir()
        self.tts_engine = pyttsx3.init()
        self.vosk_model = None
        try:
            self.vosk_model = vosk.Model("C:/Users/anime/Downloads/microsoft/kindly-chat-companion/backend/vosk-model-small-en-us-0.15")
        except Exception as e:
            print(f"Vosk model not found or failed to load: {e}")
    
    def _ensure_audio_dir(self):
        os.makedirs(self.audio_dir, exist_ok=True)
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        filename: str,
        language: str = "en-US",
        use_whisper: bool = False
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using Vosk (local STT)
        """
        # Save audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        try:
            wf = wave.open(temp_file_path, "rb")
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                return {"text": "Audio must be WAV format mono PCM.", "confidence": 0.0, "duration": None}
            if not self.vosk_model:
                return {"text": "Vosk model not available.", "confidence": 0.0, "duration": None}
            rec = vosk.KaldiRecognizer(self.vosk_model, wf.getframerate())
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    results.append(json.loads(rec.Result()))
            results.append(json.loads(rec.FinalResult()))
            text = " ".join([r.get("text", "") for r in results])
            return {"text": text, "confidence": 1.0, "duration": wf.getnframes() / wf.getframerate()}
        except Exception as e:
            return {"text": f"Transcription error: {e}", "confidence": 0.0, "duration": None}
        finally:
            os.unlink(temp_file_path)
    
    async def synthesize_speech(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Convert text to speech using pyttsx3 (local TTS)
        Returns audio file URL for playback
        """
        file_id = self._generate_file_id(text, voice, speed)
        file_path = os.path.join(self.audio_dir, f"{file_id}.mp3")
        try:
            self.tts_engine.setProperty('rate', int(200 * speed))
            self.tts_engine.save_to_file(text, file_path)
            self.tts_engine.runAndWait()
        file_size = os.path.getsize(file_path)
        return {
            "audio_url": f"/api/audio/file/{file_id}",
            "file_path": file_path,
            "file_size": file_size,
                "duration": None
            }
            except Exception as e:
            return {"audio_url": None, "file_path": None, "file_size": 0, "duration": None, "error": str(e)}
        
    def _generate_file_id(self, text: str, voice: str, speed: float) -> str:
        content = f"{text}_{voice}_{speed}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def get_audio_file_path(self, file_id: str) -> Optional[str]:
        file_path = os.path.join(self.audio_dir, f"{file_id}.mp3")
        return file_path if os.path.exists(file_path) else None
    
    async def delete_audio_file(self, file_id: str) -> bool:
        file_path = os.path.join(self.audio_dir, f"{file_id}.mp3")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    async def get_available_voices(self) -> List[Dict[str, str]]:
        # Only default pyttsx3 voice for now
        return [{"id": "default", "name": "Default", "provider": "pyttsx3"}]

audio_service = AudioService()