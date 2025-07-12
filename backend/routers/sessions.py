"""
Therapy Sessions Router
Handles CRUD operations for therapy sessions.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload

from models.database import get_db
from models.schemas import TherapySession, TherapyMessage, User
from models.pydantic_models import (
    TherapySessionCreate, 
    TherapySessionUpdate, 
    TherapySessionResponse,
    BaseResponse
)

router = APIRouter()


@router.post("/", response_model=TherapySessionResponse, status_code=status.HTTP_201_CREATED)
async def create_therapy_session(
    session_data: TherapySessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new therapy session"""
    try:
        # Create new session
        new_session = TherapySession(
            user_id=session_data.user_id,
            title=session_data.title
        )
        
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        
        return TherapySessionResponse(
            id=new_session.id,
            user_id=new_session.user_id,
            title=new_session.title,
            created_at=new_session.created_at,
            updated_at=new_session.updated_at,
            message_count=0
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session: {str(e)}"
        )


@router.get("/{user_id}", response_model=List[TherapySessionResponse])
async def get_user_sessions(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all therapy sessions for a user"""
    try:
        # Query sessions with message count
        query = (
            select(
                TherapySession,
                func.count(TherapyMessage.id).label('message_count')
            )
            .outerjoin(TherapyMessage)
            .where(TherapySession.user_id == user_id)
            .group_by(TherapySession.id)
            .order_by(TherapySession.updated_at.desc())
        )
        
        result = await db.execute(query)
        sessions_with_counts = result.all()
        
        return [
            TherapySessionResponse(
                id=session.id,
                user_id=session.user_id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=message_count
            )
            for session, message_count in sessions_with_counts
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching sessions: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=TherapySessionResponse)
async def get_therapy_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific therapy session"""
    try:
        # Query session with message count
        query = (
            select(
                TherapySession,
                func.count(TherapyMessage.id).label('message_count')
            )
            .outerjoin(TherapyMessage)
            .where(TherapySession.id == session_id)
            .group_by(TherapySession.id)
        )
        
        result = await db.execute(query)
        session_data = result.first()
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        session, message_count = session_data
        
        return TherapySessionResponse(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=message_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching session: {str(e)}"
        )


@router.patch("/session/{session_id}/title", response_model=BaseResponse)
async def update_session_title(
    session_id: int,
    update_data: TherapySessionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update therapy session title"""
    try:
        if not update_data.title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required"
            )
        
        # Update session title
        query = (
            update(TherapySession)
            .where(TherapySession.id == session_id)
            .values(title=update_data.title)
            .returning(TherapySession.id)
        )
        
        result = await db.execute(query)
        updated_session = result.first()
        
        if not updated_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        await db.commit()
        
        return BaseResponse(
            success=True,
            message="Session title updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating session: {str(e)}"
        )


@router.delete("/session/{session_id}", response_model=BaseResponse)
async def delete_therapy_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a therapy session and all its messages"""
    try:
        # Check if session exists
        query = select(TherapySession).where(TherapySession.id == session_id)
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Delete session (cascade will delete messages)
        await db.delete(session)
        await db.commit()
        
        return BaseResponse(
            success=True,
            message="Session deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session: {str(e)}"
        )


@router.post("/demo/init", response_model=dict)
async def initialize_demo_session(
    db: AsyncSession = Depends(get_db)
):
    """Create a demo user and initial therapy session for testing"""
    try:
        # Check if demo user already exists
        query = select(User).where(User.username == "demo_user")
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            # Create demo user
            from models.schemas import User
            user = User(
                username="demo_user",
                password="demo_password"  # In production, this should be hashed
            )
            db.add(user)
            await db.flush()
        
        # Create initial therapy session
        session = TherapySession(
            user_id=user.id,
            title="Initial Therapy Session"
        )
        db.add(session)
        await db.flush()
        
        # Create welcome message
        welcome_message = TherapyMessage(
            session_id=session.id,
            content="Hello! I'm Dr. Sarah, your virtual therapist. I'm here to listen and help you work through whatever is on your mind. How are you feeling today?",
            is_user=False,
            mood='idle'
        )
        db.add(welcome_message)
        
        await db.commit()
        
        return {
            "user": {
                "id": user.id,
                "username": user.username
            },
            "session": {
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at
            }
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing demo: {str(e)}"
        )