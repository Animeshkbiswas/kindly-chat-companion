"""
User Settings Router
Handles user preferences and therapy settings.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from models.database import get_db
from models.schemas import UserSettings, User
from models.pydantic_models import (
    UserSettingsCreate,
    UserSettingsUpdate,
    UserSettingsResponse,
    BaseResponse
)

router = APIRouter()


@router.get("/{user_id}", response_model=UserSettingsResponse)
async def get_user_settings(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user settings, creating default settings if none exist"""
    try:
        # Check if user exists
        user_query = select(User).where(User.id == user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get user settings
        settings_query = select(UserSettings).where(UserSettings.user_id == user_id)
        settings_result = await db.execute(settings_query)
        settings = settings_result.scalar_one_or_none()
        
        # Create default settings if none exist
        if not settings:
            settings = UserSettings(
                user_id=user_id,
                voice_enabled=True,
                speech_rate=90,
                speech_pitch=110,
                language='en-US',
                therapist_personality='warm',
                audio_visualization_enabled=False
            )
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
        
        return UserSettingsResponse(
            id=settings.id,
            user_id=settings.user_id,
            voice_enabled=settings.voice_enabled,
            speech_rate=settings.speech_rate,
            speech_pitch=settings.speech_pitch,
            language=settings.language,
            therapist_personality=settings.therapist_personality,
            audio_visualization_enabled=settings.audio_visualization_enabled,
            updated_at=settings.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching settings: {str(e)}"
        )


@router.patch("/{user_id}", response_model=UserSettingsResponse)
async def update_user_settings(
    user_id: int,
    settings_update: UserSettingsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user settings"""
    try:
        # Get existing settings
        settings_query = select(UserSettings).where(UserSettings.user_id == user_id)
        settings_result = await db.execute(settings_query)
        settings = settings_result.scalar_one_or_none()
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User settings not found"
            )
        
        # Prepare update data
        update_data = {}
        if settings_update.voice_enabled is not None:
            update_data['voice_enabled'] = settings_update.voice_enabled
        if settings_update.speech_rate is not None:
            update_data['speech_rate'] = settings_update.speech_rate
        if settings_update.speech_pitch is not None:
            update_data['speech_pitch'] = settings_update.speech_pitch
        if settings_update.language is not None:
            update_data['language'] = settings_update.language
        if settings_update.therapist_personality is not None:
            update_data['therapist_personality'] = settings_update.therapist_personality
        if settings_update.audio_visualization_enabled is not None:
            update_data['audio_visualization_enabled'] = settings_update.audio_visualization_enabled
        
        if not update_data:
            # No updates provided, return current settings
            return UserSettingsResponse(
                id=settings.id,
                user_id=settings.user_id,
                voice_enabled=settings.voice_enabled,
                speech_rate=settings.speech_rate,
                speech_pitch=settings.speech_pitch,
                language=settings.language,
                therapist_personality=settings.therapist_personality,
                audio_visualization_enabled=settings.audio_visualization_enabled,
                updated_at=settings.updated_at
            )
        
        # Update settings
        update_query = (
            update(UserSettings)
            .where(UserSettings.user_id == user_id)
            .values(**update_data)
            .returning(UserSettings)
        )
        
        result = await db.execute(update_query)
        updated_settings = result.scalar_one()
        await db.commit()
        
        return UserSettingsResponse(
            id=updated_settings.id,
            user_id=updated_settings.user_id,
            voice_enabled=updated_settings.voice_enabled,
            speech_rate=updated_settings.speech_rate,
            speech_pitch=updated_settings.speech_pitch,
            language=updated_settings.language,
            therapist_personality=updated_settings.therapist_personality,
            audio_visualization_enabled=updated_settings.audio_visualization_enabled,
            updated_at=updated_settings.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating settings: {str(e)}"
        )


@router.post("/", response_model=UserSettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_user_settings(
    settings_data: UserSettingsCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new user settings"""
    try:
        # Check if user exists
        user_query = select(User).where(User.id == settings_data.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if settings already exist
        existing_query = select(UserSettings).where(UserSettings.user_id == settings_data.user_id)
        existing_result = await db.execute(existing_query)
        existing_settings = existing_result.scalar_one_or_none()
        
        if existing_settings:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User settings already exist"
            )
        
        # Create new settings
        new_settings = UserSettings(
            user_id=settings_data.user_id,
            voice_enabled=settings_data.voice_enabled,
            speech_rate=settings_data.speech_rate,
            speech_pitch=settings_data.speech_pitch,
            language=settings_data.language,
            therapist_personality=settings_data.therapist_personality,
            audio_visualization_enabled=settings_data.audio_visualization_enabled
        )
        
        db.add(new_settings)
        await db.commit()
        await db.refresh(new_settings)
        
        return UserSettingsResponse(
            id=new_settings.id,
            user_id=new_settings.user_id,
            voice_enabled=new_settings.voice_enabled,
            speech_rate=new_settings.speech_rate,
            speech_pitch=new_settings.speech_pitch,
            language=new_settings.language,
            therapist_personality=new_settings.therapist_personality,
            audio_visualization_enabled=new_settings.audio_visualization_enabled,
            updated_at=new_settings.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating settings: {str(e)}"
        )