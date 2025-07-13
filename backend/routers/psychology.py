"""
Psychology Interview Router
Handles clinical psychology interviews, document analysis, and report generation.
"""

import os
import sys
import tempfile
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add the psychology test module to the path
psychology_path = Path(__file__).parent.parent / "hugg" / "1.PsychologyTest"
sys.path.append(str(psychology_path))

from models.database import get_db
from models.schemas import TherapySession
from models.pydantic_models import (
    PsychologyInterviewRequest,
    PsychologyInterviewResponse,
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    InterviewerPersonality
)
from services.psychology_service import psychology_service

router = APIRouter()


@router.post("/start-interview", response_model=PsychologyInterviewResponse)
async def start_interview(
    request: PsychologyInterviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start a new psychology interview session"""
    try:
        # Get or create session
        session_id = request.session_id
        if not session_id:
            # Create new session
            new_session = TherapySession(
                user_id=request.user_id,
                title=f"Psychology Interview - {request.interviewer}"
            )
            db.add(new_session)
            await db.flush()
            session_id = new_session.id
        
        # Initialize interview with selected interviewer
        initial_message, audio_buffer = await psychology_service.start_interview(
            interviewer=request.interviewer,
            language=request.language or "english"
        )
        
        # Save initial message to database
        from models.schemas import TherapyMessage
        initial_msg = TherapyMessage(
            session_id=session_id,
            content=initial_message,
            is_user=False,
            mood="speaking"
        )
        db.add(initial_msg)
        await db.commit()
        
        return PsychologyInterviewResponse(
            session_id=session_id,
            message=initial_message,
            audio_data=audio_buffer.getvalue() if audio_buffer else None,
            question_count=1,
            total_questions=25
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting interview: {str(e)}"
        )


@router.post("/continue-interview", response_model=PsychologyInterviewResponse)
async def continue_interview(
    request: PsychologyInterviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """Continue the psychology interview with user response"""
    try:
        # Verify session exists
        session_query = select(TherapySession).where(TherapySession.id == request.session_id)
        session_result = await db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Get conversation history
        from models.schemas import TherapyMessage
        history_query = (
            select(TherapyMessage)
            .where(TherapyMessage.session_id == request.session_id)
            .order_by(TherapyMessage.created_at)
        )
        history_result = await db.execute(history_query)
        history_messages = history_result.scalars().all()
        
        # Save user message
        user_message = TherapyMessage(
            session_id=request.session_id,
            content=request.user_message,
            is_user=True,
            mood="listening"
        )
        db.add(user_message)
        await db.flush()
        
        # Generate next interview question
        response, audio_buffer, question_count, is_complete = await psychology_service.continue_interview(
            user_message=request.user_message,
            session_history=history_messages,
            interviewer=request.interviewer,
            language=request.language or "english"
        )
        
        # Save AI response
        ai_message = TherapyMessage(
            session_id=request.session_id,
            content=response,
            is_user=False,
            mood="speaking"
        )
        db.add(ai_message)
        await db.commit()
        
        return PsychologyInterviewResponse(
            session_id=request.session_id,
            message=response,
            audio_data=audio_buffer.getvalue() if audio_buffer else None,
            question_count=question_count,
            total_questions=25,
            is_complete=is_complete
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error continuing interview: {str(e)}"
        )


@router.post("/generate-report/{session_id}")
async def generate_interview_report(
    session_id: int,
    language: str = "english",
    db: AsyncSession = Depends(get_db)
):
    """Generate clinical report from completed interview"""
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
        
        # Get all messages from session
        from models.schemas import TherapyMessage
        messages_query = (
            select(TherapyMessage)
            .where(TherapyMessage.session_id == session_id)
            .order_by(TherapyMessage.created_at)
        )
        messages_result = await db.execute(messages_query)
        messages = messages_result.scalars().all()
        
        # Generate report
        report_content, pdf_path = await psychology_service.generate_interview_report(
            messages=messages,
            language=language
        )
        
        return {
            "report_content": report_content,
            "pdf_path": pdf_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )


@router.post("/analyze-document", response_model=DocumentAnalysisResponse)
async def analyze_document(
    file: UploadFile = File(...),
    language: str = "english",
    db: AsyncSession = Depends(get_db)
):
    """Analyze uploaded document and generate clinical report"""
    try:
        # Validate file type
        allowed_extensions = ['.txt', '.pdf', '.docx']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Analyze document
            report_content, pdf_path = await psychology_service.analyze_document(
                file_path=temp_file_path,
                language=language
            )
            
            return DocumentAnalysisResponse(
                report_content=report_content,
                pdf_path=pdf_path
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing document: {str(e)}"
        )


@router.get("/download-report/{filename}")
async def download_report(filename: str):
    """Download generated PDF report"""
    try:
        # Security: validate filename to prevent path traversal
        if ".." in filename or "/" in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename"
            )
        
        report_path = Path(__file__).parent.parent / "uploads" / "reports" / filename
        
        if not report_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        return FileResponse(
            path=str(report_path),
            filename=filename,
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading report: {str(e)}"
        )


@router.get("/interviewers")
async def get_available_interviewers():
    """Get list of available interviewer personalities"""
    return {
        "interviewers": [
            {
                "id": "sarah",
                "name": "Sarah",
                "description": "An empathic, compassionate clinical psychologist with over 30 years of experience, specializing in trauma, anxiety disorders, and family therapy.",
                "voice": "alloy",
                "personality": "empathetic"
            },
            {
                "id": "aaron", 
                "name": "Aaron",
                "description": "A tough minded, clinical psychologist with over 15 years of experience, specializing in stress, trauma, and high-performance demands, with a background as a military officer.",
                "voice": "onyx",
                "personality": "direct"
            }
        ]
    } 