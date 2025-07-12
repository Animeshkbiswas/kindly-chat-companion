"""
Reports Router
Handles therapy session reports and analytics.
"""

import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import get_db
from models.schemas import TherapySession, TherapyMessage, TherapyReport
from models.pydantic_models import (
    ReportGenerateRequest,
    ReportResponse,
    BaseResponse
)
from services.report_service import report_service

router = APIRouter()


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_therapy_report(
    report_request: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate therapy session report
    Creates PDF report with session analysis and insights
    """
    try:
        # Verify session exists
        session_query = select(TherapySession).where(TherapySession.id == report_request.session_id)
        session_result = await db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Get session messages
        messages_query = (
            select(TherapyMessage)
            .where(TherapyMessage.session_id == report_request.session_id)
            .order_by(TherapyMessage.created_at)
        )
        messages_result = await db.execute(messages_query)
        messages = messages_result.scalars().all()
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No messages found in session"
            )
        
        # Generate report
        report_data = await report_service.generate_session_report(
            session=session,
            messages=messages,
            report_type=report_request.report_type,
            include_audio=report_request.include_audio
        )
        
        # Save report to database
        new_report = TherapyReport(
            session_id=report_request.session_id,
            report_type=report_request.report_type,
            content=report_data["content"]
        )
        
        db.add(new_report)
        await db.commit()
        await db.refresh(new_report)
        
        return ReportResponse(
            id=new_report.id,
            session_id=new_report.session_id,
            report_type=new_report.report_type,
            download_url=report_data["download_url"],
            generated_at=new_report.generated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=List[ReportResponse])
async def get_session_reports(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all reports for a therapy session"""
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
        
        # Get reports
        reports_query = (
            select(TherapyReport)
            .where(TherapyReport.session_id == session_id)
            .order_by(TherapyReport.generated_at.desc())
        )
        reports_result = await db.execute(reports_query)
        reports = reports_result.scalars().all()
        
        return [
            ReportResponse(
                id=report.id,
                session_id=report.session_id,
                report_type=report.report_type,
                download_url=f"/api/reports/download/{report.id}",
                generated_at=report.generated_at
            )
            for report in reports
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching reports: {str(e)}"
        )


@router.get("/download/{report_id}")
async def download_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Download therapy report as PDF"""
    try:
        # Get report
        report_query = select(TherapyReport).where(TherapyReport.id == report_id)
        report_result = await db.execute(report_query)
        report = report_result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Get report file path
        file_path = await report_service.get_report_file_path(report_id)
        
        if not file_path or not os.path.exists(file_path):
            # Regenerate report if file doesn't exist
            session_query = select(TherapySession).where(TherapySession.id == report.session_id)
            session_result = await db.execute(session_query)
            session = session_result.scalar_one()
            
            messages_query = (
                select(TherapyMessage)
                .where(TherapyMessage.session_id == report.session_id)
                .order_by(TherapyMessage.created_at)
            )
            messages_result = await db.execute(messages_query)
            messages = messages_result.scalars().all()
            
            # Regenerate report
            report_data = await report_service.generate_session_report(
                session=session,
                messages=messages,
                report_type=report.report_type,
                include_audio=False
            )
            file_path = report_data["file_path"]
        
        # Return file
        filename = f"therapy_report_{report.session_id}_{report.report_type}.pdf"
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading report: {str(e)}"
        )


@router.delete("/{report_id}", response_model=BaseResponse)
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete therapy report"""
    try:
        # Get report
        report_query = select(TherapyReport).where(TherapyReport.id == report_id)
        report_result = await db.execute(report_query)
        report = report_result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Delete report file
        await report_service.delete_report_file(report_id)
        
        # Delete from database
        await db.delete(report)
        await db.commit()
        
        return BaseResponse(
            success=True,
            message="Report deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting report: {str(e)}"
        )


@router.get("/analytics/{session_id}")
async def get_session_analytics(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get analytics and insights for a therapy session"""
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
        
        # Get session messages
        messages_query = (
            select(TherapyMessage)
            .where(TherapyMessage.session_id == session_id)
            .order_by(TherapyMessage.created_at)
        )
        messages_result = await db.execute(messages_query)
        messages = messages_result.scalars().all()
        
        # Generate analytics
        analytics = await report_service.generate_session_analytics(session, messages)
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating analytics: {str(e)}"
        )