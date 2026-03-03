"""
API Routes for Media Input (Audio & Video)
مسارات API لإدخال الملفات الصوتية والفيديو
"""
import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from services.processing.audio_input_processor import AudioInputProcessor
from services.processing.video_input_processor import VideoInputProcessor
from api.response_models import APIResponse
from utils.logger import logger


# إنشاء الـ Router
media_input_router = APIRouter()


# ==================== AUDIO ROUTES ====================

@media_input_router.post("/audio/upload", response_model=APIResponse)
async def upload_audio(file: UploadFile = File(...), user_id: int = Query(None)):
    """
    رفع ملف صوتي
    
    Source ID: 5 (voice)
    Source Type ID: 5 (user_input)
    
    Args:
        file: