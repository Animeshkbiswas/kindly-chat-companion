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
import traceback

from models.database import get_db
from models.pydantic_models import (
    TextToSpeechRequest,
    TextToSpeechResponse,
    BaseResponse
)
from services.audio_service import audio_service
from core.config import get_settings

from fastapi import UploadFile
import numpy as np
import cv2
import mediapipe as mp
from emotion_detection.model.keypoint_classifier.keypoint_classifier import KeyPointClassifier

settings = get_settings()
router = APIRouter()


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


@router.post("/emotion/detect")
async def detect_emotion(
    file: UploadFile = File(...)
):
    """
    Detect emotion from an uploaded image file (webcam frame)
    """
    try:
        # Read image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Run MediaPipe face mesh
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return {"emotion_probs": None, "success": False, "reason": "No face detected"}

        # Get landmarks for the first face
        face_landmarks = results.multi_face_landmarks[0]
        image_height, image_width = image.shape[:2]
        landmark_point = []
        for landmark in face_landmarks.landmark:
            x = min(int(landmark.x * image_width), image_width - 1)
            y = min(int(landmark.y * image_height), image_height - 1)
            landmark_point.append([x, y])

        # Preprocess landmarks
        import itertools, copy
        temp_landmark_list = copy.deepcopy(landmark_point)
        base_x, base_y = temp_landmark_list[0][0], temp_landmark_list[0][1]
        for idx, point in enumerate(temp_landmark_list):
            temp_landmark_list[idx][0] -= base_x
            temp_landmark_list[idx][1] -= base_y
        flat_landmarks = list(itertools.chain.from_iterable(temp_landmark_list))
        max_value = max(list(map(abs, flat_landmarks)))
        if max_value == 0:
            return {"emotion_probs": None, "success": False, "reason": "Invalid landmarks"}
        norm_landmarks = [n / max_value for n in flat_landmarks]

        # Run classifier
        classifier = KeyPointClassifier()
        emotion_id = classifier(norm_landmarks)
        # Read labels
        with open('emotion_detection/model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
            labels = [row.strip() for row in f.readlines() if row.strip()]
        # Build running probability dictionary
        d = {label: 0 for label in labels}
        total = 1
        d[labels[emotion_id]] += 1
        d_new = {key: value/total for key, value in d.items()}
        return {"emotion_probs": d_new, "success": True}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Emotion detection failed: {str(e)}")