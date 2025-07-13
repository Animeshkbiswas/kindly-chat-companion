"""
Pydantic models for request/response validation
Ensures type safety and API documentation.
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict


# Base models
class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = True
    message: Optional[str] = None


# User models
class UserCreate(BaseModel):
    """User creation request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class UserResponse(BaseModel):
    """User response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    created_at: datetime


class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class Token(BaseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Therapy session models
class TherapySessionCreate(BaseModel):
    """Therapy session creation request"""
    title: str = Field(..., min_length=1, max_length=255)
    user_id: Optional[int] = None


class TherapySessionUpdate(BaseModel):
    """Therapy session update request"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)


class TherapySessionResponse(BaseModel):
    """Therapy session response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: Optional[int]
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None


# Therapy message models
class TherapyMessageCreate(BaseModel):
    """Therapy message creation request"""
    session_id: int
    content: str = Field(..., min_length=1, max_length=2000)
    is_user: bool
    mood: Optional[Literal['idle', 'listening', 'speaking', 'thinking', 'happy', 'concerned']] = None


class TherapyMessageResponse(BaseModel):
    """Therapy message response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
    content: str
    is_user: bool
    mood: Optional[str]
    created_at: datetime


# Chat models
class ChatRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[int] = None
    user_id: Optional[int] = None
    therapist_personality: str = Field(default="warm", max_length=50)
    language: str = Field(default="en-US", max_length=10)


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: int
    message_id: int
    character_mood: Literal['idle', 'listening', 'speaking', 'thinking', 'happy', 'concerned']
    audio_url: Optional[str] = None
    session_title: Optional[str] = None


# User settings models
class UserSettingsCreate(BaseModel):
    """User settings creation request"""
    user_id: int
    voice_enabled: bool = True
    speech_rate: int = Field(default=90, ge=10, le=200)
    speech_pitch: int = Field(default=110, ge=10, le=200)
    language: str = Field(default="en-US", max_length=10)
    therapist_personality: str = Field(default="warm", max_length=50)
    audio_visualization_enabled: bool = False


class UserSettingsUpdate(BaseModel):
    """User settings update request"""
    voice_enabled: Optional[bool] = None
    speech_rate: Optional[int] = Field(None, ge=10, le=200)
    speech_pitch: Optional[int] = Field(None, ge=10, le=200)
    language: Optional[str] = Field(None, max_length=10)
    therapist_personality: Optional[str] = Field(None, max_length=50)
    audio_visualization_enabled: Optional[bool] = None


class UserSettingsResponse(BaseModel):
    """User settings response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    voice_enabled: bool
    speech_rate: int
    speech_pitch: int
    language: str
    therapist_personality: str
    audio_visualization_enabled: bool
    updated_at: datetime


# Audio models
class AudioTranscriptionRequest(BaseModel):
    """Audio transcription request"""
    language: str = Field(default="en-US", max_length=10)
    use_whisper: bool = False


class AudioTranscriptionResponse(BaseModel):
    """Audio transcription response"""
    text: str
    confidence: Optional[float] = None
    duration: Optional[float] = None


class TextToSpeechRequest(BaseModel):
    """Text-to-speech request"""
    text: str = Field(..., min_length=1, max_length=2000)
    voice: str = Field(default="alloy", max_length=50)
    speed: float = Field(default=1.0, ge=0.25, le=4.0)


class TextToSpeechResponse(BaseModel):
    """Text-to-speech response"""
    audio_url: str
    duration: Optional[float] = None
    file_size: Optional[int] = None


# Report models
class ReportGenerateRequest(BaseModel):
    """Report generation request"""
    session_id: int
    report_type: Literal['summary', 'progress', 'analysis'] = 'summary'
    include_audio: bool = False


class ReportResponse(BaseModel):
    """Report response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
    report_type: str
    download_url: str
    generated_at: datetime


# Health check model
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str
    database_connected: bool
    ai_services: dict


# Psychology Interview models
class PsychologyInterviewRequest(BaseModel):
    """Psychology interview request"""
    session_id: Optional[int] = None
    user_id: Optional[int] = None
    user_message: Optional[str] = None
    interviewer: str = Field(default="Sarah", max_length=50)
    language: str = Field(default="english", max_length=20)


class PsychologyInterviewResponse(BaseModel):
    """Psychology interview response"""
    session_id: int
    message: str
    audio_data: Optional[bytes] = None
    question_count: int
    total_questions: int
    is_complete: bool = False


class DocumentAnalysisRequest(BaseModel):
    """Document analysis request"""
    language: str = Field(default="english", max_length=20)


class DocumentAnalysisResponse(BaseModel):
    """Document analysis response"""
    report_content: str
    pdf_path: str


class InterviewerPersonality(BaseModel):
    """Interviewer personality model"""
    id: str
    name: str
    description: str
    voice: str
    personality: str


# Error models
class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None