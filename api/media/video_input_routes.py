
"""
API Routes for Video Input
مسارات API لإدخال الملفات الفيديو
"""
import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from services.processing.video_input_processor import VideoInputProcessor
from utils.logger import logger


# إنشاء الـ Router
video_input_router = APIRouter()


@video_input_router.post("/upload")
async def upload_video(file: UploadFile = File(...), user_id: int = Query(None)):
    """
    رفع ملف فيديو
    
    Flow:
    1. رفع الفيديو إلى S3
    2. حفظ معلومات الملف في uploaded_files (status = pending)
    3. الـ job سيستخرج الصوت ويحوله لنص ويخزنه في transcripts
    4. بعد الفلترة، سينشئ صف في raw_data
    
    Args:
        file: الملف الفيديو
        user_id: معرف المستخدم (اختياري)
        
    Returns:
        dict: نتيجة الرفع
    """
    temp_file_path = None
    try:
        logger.info(f"🎥 تم استقبال طلب رفع ملف فيديو: {file.filename}")
        
        # التحقق من نوع الملف
        if file.content_type not in VideoInputProcessor.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "نوع ملف غير مدعوم",
                    "message": f"الصيغ المدعومة: {', '.join(VideoInputProcessor.SUPPORTED_FORMATS.keys())}"
                }
            )
        
        # حفظ الملف مؤقتًا
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # معالجة الملف الفيديو
        result = VideoInputProcessor.process_video(
            file_path=temp_file_path,
            file_name=file.filename,
            content_type=file.content_type,
            user_id=user_id
        )
        
        if result["success"]:
            # ملاحظة: raw_data سيتم إنشاؤه لاحقاً من الـ job بعد الفلترة
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=result
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ خطأ في رفع الملف الفيديو: {e}")
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


@video_input_router.post("/record")
async def record_video(file: UploadFile = File(...), user_id: int = Query(None)):
    """
    تسجيل فيديو جديد
    
    Flow:
    1. رفع الفيديو إلى S3
    2. حفظ معلومات الملف في uploaded_files (status = pending)
    3. الـ job سيستخرج الصوت ويحوله لنص ويخزنه في transcripts
    4. بعد الفلترة، سينشئ صف في raw_data
    
    Args:
        file: الملف الفيديو المسجل
        user_id: معرف المستخدم (اختياري)
        
    Returns:
        dict: نتيجة التسجيل
    """
    temp_file_path = None
    try:
        logger.info(f"🎥 تم استقبال طلب تسجيل فيديو: {file.filename}")
        
        # التحقق من نوع الملف
        if file.content_type not in VideoInputProcessor.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "نوع ملف غير مدعوم",
                    "message": f"الصيغ المدعومة: {', '.join(VideoInputProcessor.SUPPORTED_FORMATS.keys())}"
                }
            )
        
        # حفظ الملف مؤقتًا
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # معالجة الملف الفيديو (نفس المعالجة كـ upload)
        result = VideoInputProcessor.process_video(
            file_path=temp_file_path,
            file_name=file.filename,
            content_type=file.content_type,
            user_id=user_id
        )
        
        if result["success"]:
            # ملاحظة: raw_data سيتم إنشاؤه لاحقاً من الـ job بعد الفلترة
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=result
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ خطأ في تسجيل الملف الفيديو: {e}")
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


@video_input_router.get("/status/{uploaded_file_id}")
async def get_video_status(uploaded_file_id: int):
    """
    الحصول على حالة معالجة الملف الفيديو
    
    Args:
        uploaded_file_id: معرف الملف المرفوع
        
    Returns:
        dict: حالة المعالجة
    """
    try:
        logger.info(f"📊 تم استقبال طلب جلب حالة الملف الفيديو: {uploaded_file_id}")
        
        result = VideoInputProcessor.get_video_status(uploaded_file_id)
        
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
