"""
API Routes for Audio Input
مسارات API لإدخال الملفات الصوتية
"""
import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from services.processing.audio_input_processor import AudioInputProcessor
from utils.logger import logger


# إنشاء الـ Router
audio_input_router = APIRouter()


@audio_input_router.post("/upload")
async def upload_audio(file: UploadFile = File(...), user_id: int = Query(None)):
    """
    رفع ملف صوتي
    
    Source ID: 5 (voice)
    Source Type ID: 5 (user_input)
    
    Args:
        file: الملف الصوتي
        user_id: معرف المستخدم (اختياري)
        
    Returns:
        dict: نتيجة الرفع
    """
    temp_file_path = None
    try:
        logger.info(f"🎙️ تم استقبال طلب رفع ملف صوتي: {file.filename}")
        
        # التحقق من نوع الملف
        if file.content_type not in AudioInputProcessor.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "نوع ملف غير مدعوم",
                    "message": f"الصيغ المدعومة: {', '.join(AudioInputProcessor.SUPPORTED_FORMATS.keys())}"
                }
            )
        
        # حفظ الملف مؤقتًا
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # معالجة الملف الصوتي
        result = AudioInputProcessor.process_audio(
            file_path=temp_file_path,
            file_name=file.filename,
            content_type=file.content_type,
            user_id=user_id
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=result
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ خطأ في رفع الملف الصوتي: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "خطأ في الخادم",
                "message": "حدث خطأ أثناء رفع الملف"
            }
        )
    finally:
        # حذف الملف المؤقت
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"⚠️ فشل حذف الملف المؤقت: {e}")


@audio_input_router.post("/record")
async def record_audio(file: UploadFile = File(...), user_id: int = Query(None)):
    """
    تسجيل صوتي جديد
    
    Source ID: 5 (voice)
    Source Type ID: 5 (user_input)
    
    Args:
        file: الملف الصوتي المسجل
        user_id: معرف المستخدم (اختياري)
        
    Returns:
        dict: نتيجة التسجيل
    """
    temp_file_path = None
    try:
        logger.info(f"🎙️ تم استقبال طلب تسجيل صوتي: {file.filename}")
        
        # التحقق من نوع الملف
        if file.content_type not in AudioInputProcessor.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "نوع ملف غير مدعوم",
                    "message": f"الصيغ المدعومة: {', '.join(AudioInputProcessor.SUPPORTED_FORMATS.keys())}"
                }
            )
        
        # حفظ الملف مؤقتًا
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # معالجة الملف الصوتي (نفس المعالجة كـ upload)
        result = AudioInputProcessor.process_audio(
            file_path=temp_file_path,
            file_name=file.filename,
            content_type=file.content_type,
            user_id=user_id
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=result
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ خطأ في تسجيل الملف الصوتي: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "خطأ في الخادم",
                "message": "حدث خطأ أثناء تسجيل الملف"
            }
        )
    finally:
        # حذف الملف المؤقت
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"⚠️ فشل حذف الملف المؤقت: {e}")


@audio_input_router.get("/status/{uploaded_file_id}")
async def get_audio_status(uploaded_file_id: int):
    """
    الحصول على حالة معالجة الملف الصوتي
    
    Args:
        uploaded_file_id: معرف الملف المرفوع
        
    Returns:
        dict: حالة المعالجة
    """
    try:
        logger.info(f"📊 تم استقبال طلب جلب حالة الملف الصوتي: {uploaded_file_id}")
        
        result = AudioInputProcessor.get_audio_status(uploaded_file_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=404,
                detail=result
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ خطأ في جلب حالة الملف: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "خطأ في الخادم",
                "message": "حدث خطأ أثناء جلب حالة الملف"
            }
        )
