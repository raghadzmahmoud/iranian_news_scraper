"""
Main API Router
الـ Router الرئيسي للـ API
"""
from fastapi import APIRouter
from api.news.manual_input_routes import manual_news_router
from api.media.audio_input_routes import audio_input_router
from api.media.video_input_routes import video_input_router
from api.translation import router as translation_router


# إنشاء الـ Router الرئيسي
api_router = APIRouter()

# تسجيل الـ Routers
# Media Input Module - الصوت والفيديو
api_router.include_router(
    audio_input_router,
    prefix="/media/input/audio",
    tags=["Media Input - Audio"]
)

api_router.include_router(
    video_input_router,
    prefix="/media/input/video",
    tags=["Media Input - Video"]
)

# News Module - النصوص اليدوية
api_router.include_router(
    manual_news_router,
    prefix="/news",
    tags=["News - Manual Input"]
)

# Translation Module - الترجمة
api_router.include_router(
    translation_router,
    tags=["Translation"]
)
