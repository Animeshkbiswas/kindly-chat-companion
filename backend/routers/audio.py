"""
Audio Processing Router
Handles audio transcription and text-to-speech functionality.
"""

import os
import io
import tempfile
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from models.database import get_db
from models.pydantic_models import (
    AudioTranscriptionRequest,
    AudioTranscriptionResponse,
    TextToSpeechRequest,
    TextToSpeechResponse,
    BaseResponse
)
from services.audio_service import audio_service
from core.config import get_settings

settings = get_settings()
router = APIRouter()


@router.post("/transcribe", response_model=AudioTranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = "en-US",
    use_whisper: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Transcribe audio file to text
    Supports both browser-recorded audio and file uploads
    """
    try:
        # Validate file size
        if audio_file.size and audio_file.size > settings.max_audio_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.max_audio_file_size} bytes"
            )
        
        # Validate file type
        allowed_types = ["audio/wav", "audio/mp3", "audio/mpeg", "audio/ogg", "audio/webm"]
        if audio_file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported audio format. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Transcribe audio
        transcription_result = await audio_service.transcribe_audio(
            audio_data=audio_data,
            filename=audio_file.filename or "audio.wav",
            language=language,
            use_whisper=use_whisper
        )
        
        return AudioTranscriptionResponse(
            text=transcription_result["text"],
            confidence=transcription_result.get("confidence"),
            duration=transcription_result.get("duration")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transcribing audio: {str(e)}"
        )


@router.post("/synthesize", response_model=TextToSpeechResponse)
async def synthesize_speech(
    tts_request: TextToSpeechRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert text to speech
    Returns audio file URL for playback
    """
    try:
        # Validate text length
        if len(tts_request.text) > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text too long. Maximum 2000 characters."
            )
        
        # Generate speech
        audio_result = await audio_service.synthesize_speech(
            text=tts_request.text,
            voice=tts_request.voice,
            speed=tts_request.speed
        )
        
        return TextToSpeechResponse(
            audio_url=audio_result["audio_url"],
            duration=audio_result.get("duration"),
            file_size=audio_result.get("file_size")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error synthesizing speech: {str(e)}"
        )


@router.post("/synthesize/stream")
async def synthesize_speech_stream(
    tts_request: TextToSpeechRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert text to speech and stream audio directly
    Returns audio stream for immediate playback
    """
    try:
        # Generate speech audio
        audio_data = await audio_service.synthesize_speech_stream(
            text=tts_request.text,
            voice=tts_request.voice,
            speed=tts_request.speed
        )
        
        # Create streaming response
        def audio_stream():
            yield audio_data
        
        return StreamingResponse(
            audio_stream(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming speech: {str(e)}"
        )


@router.get("/file/{file_id}")
async def get_audio_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve audio file by ID
    Returns audio file for playback
    """
    try:
        # Get audio file path
        file_path = await audio_service.get_audio_file_path(file_id)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file not found"
            )
        
        # Determine media type
        media_type = "audio/mpeg"
        if file_path.endswith('.wav'):
            media_type = "audio/wav"
        elif file_path.endswith('.ogg'):
            media_type = "audio/ogg"
        
        # Stream file
        def file_stream():
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    yield chunk
        
        return StreamingResponse(
            file_stream(),
            media_type=media_type,
            headers={
                "Content-Disposition": f"inline; filename={os.path.basename(file_path)}",
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving audio file: {str(e)}"
        )


@router.delete("/file/{file_id}", response_model=BaseResponse)
async def delete_audio_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete audio file"""
    try:
        success = await audio_service.delete_audio_file(file_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file not found"
            )
        
        return BaseResponse(
            success=True,
            message="Audio file deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting audio file: {str(e)}"
        )


@router.get("/voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    try:
        voices = await audio_service.get_available_voices()
        return {"voices": voices}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching voices: {str(e)}"
        )