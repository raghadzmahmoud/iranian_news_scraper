"""
Worker منفصل لمعالجة الملفات الفيديو فقط
Video Processing Worker
"""
import time
from database.connection import db
from utils.logger import logger
from jobs.video_processing_job import VideoProcessingJob


def main():
    """تشغيل الـ Video Worker"""
    logger.info("🎬 جاري بدء Video Worker...")
    
    # الاتصال بقاعدة البيانات
    if not db.connect():
        logger.error("❌ فشل الاتصال بقاعدة البيانات")
        return
    
    logger.info("✅ تم الاتصال بقاعدة البيانات")
    logger.info("✅ Video Worker يعمل الآن...")
    
    try:
        while True:
            try:
                # البحث عن الملفات الفيديو المعلقة
                query = """
                    SELECT id, s3_url 
                    FROM public.uploaded_files 
                    WHERE status = 'pending' AND file_type = 'video'
                    LIMIT 5
                """
                
                db.cursor.execute(query)
                pending_files = db.cursor.fetchall()
                
                if pending_files:
                    logger.info(f"📋 وجدت {len(pending_files)} ملف فيديو معلق")
                    
                    for file_record in pending_files:
                        file_id = file_record['id'] if isinstance(file_record, dict) else file_record[0]
                        s3_url = file_record['s3_url'] if isinstance(file_record, dict) else file_record[1]
                        
                        # البحث عن السجل المرتبط في raw_data
                        raw_data_query = """
                            SELECT id FROM public.raw_data 
                            WHERE media_url = %s
                            LIMIT 1
                        """
                        db.cursor.execute(raw_data_query, (s3_url,))
                        raw_data_result = db.cursor.fetchone()
                        
                        if not raw_data_result:
                            logger.warning(f"⚠️ لم يتم العثور على سجل raw_data للملف: {file_id}")
                            continue
                        
                        raw_data_id = raw_data_result['id'] if isinstance(raw_data_result, dict) else raw_data_result[0]
                        
                        # معالجة الملف الفيديو
                        logger.info(f"🎬 جاري معالجة الملف الفيديو: {file_id}")
                        VideoProcessingJob.process_video_file(file_id, raw_data_id, s3_url)
                
                # الانتظار 5 ثوان قبل الفحص التالي
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ خطأ في معالجة الملفات: {e}")
                time.sleep(5)
                
    except KeyboardInterrupt:
        logger.info("🛑 جاري إيقاف Video Worker...")
        db.close()
        logger.info("✅ تم إيقاف Video Worker")


if __name__ == "__main__":
    main()
