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
import ffmpeg
import gc
import shutil
import time

from core.config import get_settings

settings = get_settings()

CUSTOM_TEMP_DIR = r'C:\temp'
os.makedirs(CUSTOM_TEMP_DIR, exist_ok=True)

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
        use_whisper: bool = False,
        upload_file_obj=None  # Pass UploadFile object if available
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using Vosk (local STT)
        """
        ext = os.path.splitext(filename)[-1].lower()
        if upload_file_obj is not None:
            # Save the uploaded file to a new temp file and ensure all handles are closed
            fd, temp_file_path = tempfile.mkstemp(suffix=ext)
            with os.fdopen(fd, 'wb') as out_file:
                shutil.copyfileobj(upload_file_obj.file, out_file)
            upload_file_obj.file.close()
        else:
            # Fallback for when only bytes are provided
            fd, temp_file_path = tempfile.mkstemp(suffix=ext)
            with os.fdopen(fd, 'wb') as tmp:
                tmp.write(audio_data)
        # Now temp_file_path is fully closed and safe for ffmpeg
        try:
            gc.collect()  # Ensure all handles are released

            if ext != ".wav":
                wav_temp_path = temp_file_path + ".wav"
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        (
                            ffmpeg
                            .input(temp_file_path)
                            .output(wav_temp_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000')
                            .run(quiet=True, overwrite_output=True)
                        )
                        break  # Success!
                    except Exception as e:
                        if attempt < max_retries - 1 and 'being used by another process' in str(e):
                            time.sleep(0.2)  # Wait 200ms and try again
                        else:
                            os.unlink(temp_file_path)
                            return {"text": f"Transcription error: failed to convert audio to WAV: {e}", "confidence": 0.0, "duration": None}
                os.unlink(temp_file_path)
                temp_file_path = wav_temp_path
        except Exception as e:
            return {"text": f"Transcription error: {e}", "confidence": 0.0, "duration": None}
        try:
            wf = wave.open(temp_file_path, "rb")
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                result = {"text": "Audio must be WAV format mono PCM.", "confidence": 0.0, "duration": None}
                print("Returning transcription result (bad wav):", result)
                return result
            if not self.vosk_model:
                result = {"text": "Vosk model not available.", "confidence": 0.0, "duration": None}
                print("Returning transcription result (no model):", result)
                return result
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
            result = {"text": text, "confidence": 1.0, "duration": wf.getnframes() / wf.getframerate()}
            print("Returning transcription result (success):", result)
            return result
        except Exception as e:
            result = {"text": f"Transcription error: {e}", "confidence": 0.0, "duration": None}
            print("Returning transcription result (exception):", result)
            return result
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