"""
تشغيل Video Processing Job مباشرة
Run Video Processing Job Directly
"""
import sys
from database.connection import db
from jobs.video_processing_job import VideoProcessingJob
from utils.logger import logger


def main():
    """تشغيل الـ job على ملف فيديو معين"""
    
    # الاتصال بقاعدة البيانات
    if not db.connect():
        logger.error("❌ فشل الاتصال بقاعدة البيانات")
        return
    
    # البحث عن أول ملف فيديو pending
    try:
        query = """
            SELECT id, s3_url, content_type 
            FROM public.uploaded_files 
            WHERE status = 'pending' AND content_type LIKE 'video/%'
            LIMIT 1
        """
        
        db.cursor.execute(query)
        file_record = db.cursor.fetchone()
        
        if not file_record:
            logger.warning("⚠️ لا توجد ملفات فيديو pending للمعالجة")
            db.close()
            return
        
        uploaded_file_id = file_record['id'] if isinstance(file_record, dict) else file_record[0]
        s3_url = file_record['s3_url'] if isinstance(file_record, dict) else file_record[1]
        
        logger.info(f"🎬 جاري معالجة الملف الفيديو: {uploaded_file_id}")
        logger.info(f"   S3 URL: {s3_url}")
        
        # تشغيل الـ job
        VideoProcessingJob.process_video_file(uploaded_file_id, s3_url)
        
        logger.info("✅ انتهت معالجة الملف الفيديو")
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
