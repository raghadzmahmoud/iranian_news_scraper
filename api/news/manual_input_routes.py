"""
API Routes for Manual Text Input
مسارات API لإدخال النصوص اليدوية
"""
from fastapi import APIRouter, HTTPException, Form
from services.ingestion.manual_input import ManualInputProcessor
from api.response_models import APIResponse
from utils.logger import logger


# إنشاء الـ Router
manual_news_router = APIRouter()


@manual_news_router.post("/manual", response_model=APIResponse)
async def create_manual_news(
    text: str = Form(..., description="نص الخبر"),
    source_id: int = Form(7, description="معرف المصدر (7 = نص يدوي)")
):
    """
    إدخال نص يدوي جديد
    
    - **text**: نص الخبر
    - **source_id**: معرف المصدر (افتراضي: 7)
    
    Returns:
        APIResponse: نتيجة المعالجة
    """
    try:
        logger.info(f"📝 تم استقبال طلب إدخال نص يدوي")
        
        result = ManualInputProcessor.process_manual_input(
            text=text,
            user_id=source_id
        )
        
        if result["success"]:
            return APIResponse(
                status=200,
                success=True,
                message=result["message"],
                data=result.get("data")
            )
        else:
            raise HTTPException(
                status_code=422,
                detail=APIResponse(
                    status=422,
                    success=False,
                    error_code="IRRELEVANT_NEWS",
                    message=result["message"],
                    details=result.get("error")
                ).dict()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء خبر يدوي: {e}")
        raise HTTPException(
            status_code=500,
            detail=APIResponse(
                status=500,
                success=False,
                error_code="SERVER_ERROR",
                message="حدث خطأ في الخادم"
            ).dict()
        )


@manual_news_router.get("/manual/{news_id}", response_model=APIResponse)
async def get_manual_news(news_id: int):
    """
    الحصول على تفاصيل خبر يدوي
    
    Args:
        news_id: معرف الخبر
        
    Returns:
        APIResponse: تفاصيل الخبر
    """
    try:
        logger.info(f"📖 تم استقبال طلب جلب خبر يدوي برقم: {news_id}")
        
        return APIResponse(
            status=200,
            success=True,
            message="تم جلب الخبر بنجاح",
            data={
                "id": news_id,
                "content": "محتوى الخبر",
                "title": "عنوان الخبر",
                "tags": ["مستخدم", "إدخال يدوي"],
                "created_at": "2024-03-01T10:00:00"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الخبر: {e}")
        raise HTTPException(
            status_code=500,
            detail=APIResponse(
                status=500,
                success=False,
                error_code="SERVER_ERROR",
                message="حدث خطأ في الخادم"
            ).dict()
        )
