"""
Therapy Messages Router
Handles chat messages and AI response generation.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql import func

from models.database import get_db
from models.schemas import TherapyMessage, TherapySession
from models.pydantic_models import (
    TherapyMessageCreate, 
    TherapyMessageResponse,
    ChatRequest,
    ChatResponse
)
from services.ai_service import ai_service

router = APIRouter()


@router.post("/", response_model=TherapyMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_therapy_message(
    message_data: TherapyMessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new therapy message"""
    try:
        # Verify session exists
        session_query = select(TherapySession).where(TherapySession.id == message_data.session_id)
        session_result = await db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Create new message
        new_message = TherapyMessage(
            session_id=message_data.session_id,
            content=message_data.content,
            is_user=message_data.is_user,
            mood=message_data.mood
        )
        
        db.add(new_message)
        await db.commit()
        await db.refresh(new_message)
        
        # Update session timestamp
        update_query = (
            update(TherapySession)
            .where(TherapySession.id == message_data.session_id)
            .values(updated_at=new_message.created_at)
        )
        await db.execute(update_query)
        await db.commit()
        
        return TherapyMessageResponse(
            id=new_message.id,
            session_id=new_message.session_id,
            content=new_message.content,
            is_user=new_message.is_user,
            mood=new_message.mood,
            created_at=new_message.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating message: {str(e)}"
        )


@router.get("/{session_id}", response_model=List[TherapyMessageResponse])
async def get_session_messages(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all messages for a therapy session"""
    try:
        # Verify session exists
        session_query = select(TherapySession).where(TherapySession.id == session_id)
        session_result = await db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Get messages ordered by creation time
        messages_query = (
            select(TherapyMessage)
            .where(TherapyMessage.session_id == session_id)
            .order_by(TherapyMessage.created_at)
        )
        
        result = await db.execute(messages_query)
        messages = result.scalars().all()
        
        return [
            TherapyMessageResponse(
                id=message.id,
                session_id=message.session_id,
                content=message.content,
                is_user=message.is_user,
                mood=message.mood,
                created_at=message.created_at
            )
            for message in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching messages: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Main chat endpoint for therapy conversations
    Handles user input and generates AI responses
    """
    try:
        # Get or create session
        session_id = chat_request.session_id
        if not session_id:
            # Create new session
            new_session = TherapySession(
                user_id=chat_request.user_id,
                title="New Therapy Session"
            )
            db.add(new_session)
            await db.flush()
            session_id = new_session.id
        else:
            # Verify session exists
            session_query = select(TherapySession).where(TherapySession.id == session_id)
            session_result = await db.execute(session_query)
            session = session_result.scalar_one_or_none()
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )
        
        # Get conversation history
        history_query = (
            select(TherapyMessage)
            .where(TherapyMessage.session_id == session_id)
            .order_by(TherapyMessage.created_at.desc())
            .limit(20)  # Last 20 messages
        )
        
        history_result = await db.execute(history_query)
        history_messages = history_result.scalars().all()
        
        # Convert to conversation pairs
        conversation_history = []
        messages = list(reversed(history_messages))  # Chronological order
        
        for i in range(0, len(messages) - 1, 2):
            if i + 1 < len(messages) and messages[i].is_user and not messages[i + 1].is_user:
                conversation_history.append((messages[i].content, messages[i + 1].content))
        
        # Save user message
        user_message = TherapyMessage(
            session_id=session_id,
            content=chat_request.message,
            is_user=True,
            mood=None
        )
        db.add(user_message)
        await db.flush()
        
        # Generate AI response
        ai_response, character_mood = await ai_service.generate_therapy_response(
            user_message=chat_request.message,
            conversation_history=conversation_history,
            personality=chat_request.therapist_personality,
            user_id=chat_request.user_id
        )
        logging.info(f"[chat_endpoint] AI response: '{ai_response}' | mood: {character_mood}")
        
        # Save AI response
        ai_message = TherapyMessage(
            session_id=session_id,
            content=ai_response,
            is_user=False,
            mood=character_mood
        )
        db.add(ai_message)
        
        # Update session timestamp and title if it's the first exchange
        session_update = {"updated_at": func.now()}
        if not conversation_history:  # First exchange
            # Generate title from user's first message
            title = chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message
            session_update["title"] = title
        
        update_query = (
            update(TherapySession)
            .where(TherapySession.id == session_id)
            .values(**session_update)
        )
        await db.execute(update_query)
        
        await db.commit()
        
        # Get updated session title
        session_query = select(TherapySession).where(TherapySession.id == session_id)
        session_result = await db.execute(session_query)
        updated_session = session_result.scalar_one()

        print("DEBUG: ai_response =", ai_response)
        print("DEBUG: session_id =", session_id)
        print("DEBUG: ai_message.id =", ai_message.id)
        print("DEBUG: character_mood =", character_mood)
        print("DEBUG: updated_session.title =", updated_session.title)
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            message_id=ai_message.id,
            character_mood=character_mood,
            session_title=updated_session.title
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )