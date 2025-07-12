"""
SQLAlchemy models for the therapy chat application
Converted from the existing Drizzle schema to maintain data compatibility.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    """User model - matches existing users table"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    sessions = relationship("TherapySession", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")


class TherapySession(Base):
    """Therapy session model - matches existing therapy_sessions table"""
    __tablename__ = "therapy_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("TherapyMessage", back_populates="session", cascade="all, delete-orphan")


class TherapyMessage(Base):
    """Therapy message model - matches existing therapy_messages table"""
    __tablename__ = "therapy_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("therapy_sessions.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, nullable=False)
    mood = Column(String(50), nullable=True)  # 'idle', 'listening', 'speaking', 'thinking', 'happy', 'concerned'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("TherapySession", back_populates="messages")


class UserSettings(Base):
    """User settings model - matches existing user_settings table"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    voice_enabled = Column(Boolean, default=True, nullable=False)
    speech_rate = Column(Integer, default=90, nullable=False)  # 0-200, stored as integer (90 = 0.9)
    speech_pitch = Column(Integer, default=110, nullable=False)  # 0-200, stored as integer (110 = 1.1)
    language = Column(String(10), default='en-US', nullable=False)
    therapist_personality = Column(String(50), default='warm', nullable=False)
    audio_visualization_enabled = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="settings")


# Additional models for enhanced features

class TherapyReport(Base):
    """Therapy report model for session summaries and analysis"""
    __tablename__ = "therapy_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("therapy_sessions.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # 'summary', 'progress', 'analysis'
    content = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("TherapySession")


class AudioFile(Base):
    """Audio file model for storing audio messages and responses"""
    __tablename__ = "audio_files"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("therapy_messages.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    audio_type = Column(String(20), nullable=False)  # 'input', 'response'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    message = relationship("TherapyMessage")