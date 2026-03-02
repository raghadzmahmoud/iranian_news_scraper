"""
FastAPI Application
تطبيق FastAPI الرئيسي
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import api_router
from database.connection import db
from utils.logger import logger
import os


# إنشاء تطبيق FastAPI
app = FastAPI(
    title="User Input APIs",
    description="نظام إدخال البيانات من المستخدم (نص، صوت، فيديو)",
    version="1.0.0"
)

# إضافة CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تسجيل الـ API Router
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """تهيئة التطبيق عند البدء"""
    logger.info("🚀 جاري بدء التطبيق...")
    
    # الاتصال بقاعدة البيانات
    if db.connect():
        logger.info("✅ تم الاتصال بقاعدة البيانات بنجاح")
    else:
        logger.error("❌ فشل الاتصال بقاعدة البيانات")


@app.on_event("shutdown")
async def shutdown_event():
    """تنظيف الموارد عند إيقاف التطبيق"""
    logger.info("🛑 جاري إيقاف التطبيق...")
    db.close()


@app.get("/")
async def root():
    """الـ Endpoint الرئيسي"""
    return {
        "message": "مرحبًا بك في نظام إدخال البيانات من المستخدم",
        "version": "1.0.0",
        "source_type_id": 5,
        "source_type_name": "user_input",
        "sources": {
            "text": {
                "source_id": 7,
                "name": "نص يدوي",
                "endpoint": "POST /news/manual"
            },
            "voice": {
                "source_id": 5,
                "name": "صوت",
                "endpoints": [
                    "POST /media/input/audio/upload",
                    "POST /media/input/audio/record",
                    "GET /media/input/audio/status/{id}"
                ]
            },
            "video": {
                "source_id": 6,
                "name": "فيديو",
                "endpoints": [
                    "POST /media/input/video/upload",
                    "POST /media/input/video/record",
                    "GET /media/input/video/status/{id}"
                ]
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
async def health_check():
    """فحص صحة التطبيق"""
    return {
        "status": "healthy",
        "message": "التطبيق يعمل بشكل صحيح"
    }


if __name__ == "__main__":
    import uvicorn
    
    # الحصول على المتغيرات من البيئة
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    # تشغيل الخادم
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True
    )
