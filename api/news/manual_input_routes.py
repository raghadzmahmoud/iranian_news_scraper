"""
API Routes for Manual Text Input
مسارات API لإدخال النصوص اليدوية
"""
from fastapi import APIRouter, HTTPException, Form
from services.ingestion.manual_input import ManualInputProcessor
from utils.logger import logger


# إنشاء الـ Router
manual_news_router = APIRouter()


@manual_news_router.post("/manual")
async def create_manual_news(
    text: str = Form(..., description="نص الخبر"),
    source_id: int = Form(7, description="معرف المصدر (7 = نص يدوي)")
):
    """
    إدخال نص يدوي جديد
    
    - **text**: نص الخبر (يدعم النصوص الطويلة والأحرف الخاصة)
    - **source_id**: معرف المصدر (افتراضي: 7 للنصوص اليدوية)
    
    Returns:
        dict: نتيجة المعالجة
    """
    try:
        logger.info(f"📝 تم استقبال طلب إدخال نص يدوي")
        
        # معالجة النص
        # source_id = 7 (text) - Source Type ID = 5 (user_input)
        result = ManualInputProcessor.process_manual_input(
            text=text,
            user_id=source_id
        )
        
        if result["success"]:
            return {
                "success": True,
                "news_id": result["news_id"],
                "message": result["message"],
                "data": result.get("data"),
                "matched_keywords": result.get("matched_keywords", [])
            }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": result["error"],
                    "message": result["message"],
                    "matched_keywords": result.get("matched_keywords", [])
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء خبر يدوي: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "خطأ في الخادم",
                "message": "حدث خطأ أثناء معالجة الطلب"
            }
        )


@manual_news_router.get("/manual/{news_id}")
async def get_manual_news(news_id: int):
    """
    الحصول على تفاصيل خبر يدوي
    
    Args:
        news_id: معرف الخبر
        
    Returns:
        dict: تفاصيل الخبر
    """
    try:
        logger.info(f"📖 تم استقبال طلب جلب خبر يدوي برقم: {news_id}")
        
        # هنا يتم جلب البيانات من قاعدة البيانات
        # للآن نرجع بيانات افتراضية
        
        return {
            "success": True,
            "data": {
                "id": news_id,
                "content": "محتوى الخبر",
                "title": "عنوان الخبر",
                "category": "عام",
                "tags": ["مستخدم", "إدخال يدوي"],
                "created_at": "2024-03-01T10:00:00"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الخبر: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "خطأ في الخادم",
                "message": "حدث خطأ أثناء جلب الخبر"
            }
        )
