"""
جدولة الـ Background Jobs
Job Scheduler
"""
import time
import threading
from datetime import datetime
from database.connection import DatabaseConnection
from utils.logger import logger
from jobs.audio_processing_job import AudioProcessingJob
from jobs.video_processing_job import VideoProcessingJob


class JobScheduler:
    """جدولة الـ Background Jobs"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.db = None  # سيتم إنشاؤه في الـ thread
    
    def start(self):
        """بدء جدولة الـ Jobs"""
        if self.running:
            logger.warning("⚠️ جدولة الـ Jobs قيد التشغيل بالفعل")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("✅ تم بدء جدولة الـ Jobs")
    
    def stop(self):
        """إيقاف جدولة الـ Jobs"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        if self.db:
            self.db.close()
        logger.info("🛑 تم إيقاف جدولة الـ Jobs")
    
    def _run_scheduler(self):
        """تشغيل جدولة الـ Jobs"""
        logger.info("🚀 جاري تشغيل جدولة الـ Jobs...")
        
        # إنشاء connection منفصلة لهذا الـ thread
        self.db = DatabaseConnection()
        if not self.db.connect():
            logger.error("❌ فشل الاتصال بقاعدة البيانات")
            return
        
        while self.running:
            try:
                # البحث عن الملفات المعلقة
                self._process_pending_files()
                
                # الانتظار 5 ثوان قبل الفحص التالي
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ خطأ في جدولة الـ Jobs: {e}")
                time.sleep(5)
    
    def _process_pending_files(self):
        """معالجة الملفات المعلقة"""
        try:
            # البحث عن الملفات بحالة pending
            query = """
                SELECT id, s3_url, content_type 
                FROM public.uploaded_files 
                WHERE status = 'pending'
                LIMIT 5
            """
            
            self.db.cursor.execute(query)
            pending_files = self.db.cursor.fetchall()
            
            if not pending_files:
                return
            
            logger.info(f"📋 وجدت {len(pending_files)} ملف معلق")
            
            for file_record in pending_files:
                file_id = file_record['id'] if isinstance(file_record, dict) else file_record[0]
                s3_url = file_record['s3_url'] if isinstance(file_record, dict) else file_record[1]
                content_type = file_record['content_type'] if isinstance(file_record, dict) else file_record[2]
                
                # تحديد نوع الملف ومعالجته
                if content_type and content_type.startswith('video/'):
                    logger.info(f"🎬 جاري معالجة ملف فيديو: {file_id}")
                    VideoProcessingJob.process_video_file(file_id, s3_url, db=self.db)
                elif content_type and content_type.startswith('audio/'):
                    logger.info(f"🎙️ جاري معالجة ملف صوتي: {file_id}")
                    AudioProcessingJob.process_audio_file(file_id, s3_url, db=self.db)
                else:
                    logger.warning(f"⚠️ نوع ملف غير معروف: {content_type} للملف: {file_id}")
                
        except Exception as e:
            logger.error(f"❌ خطأ في البحث عن الملفات المعلقة: {e}")


# إنشاء instance واحد من الجدولة
job_scheduler = JobScheduler()
