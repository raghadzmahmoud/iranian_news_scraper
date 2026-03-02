"""
Worker منفصل لمعالجة الملفات الفيديو فقط
Video Processing Worker - يعمل كل 2 دقيقة
"""
import time
import threading
import random
from datetime import datetime
from database.connection import DatabaseConnection
from utils.logger import logger
from jobs.video_processing_job import VideoProcessingJob


class VideoWorker:
    """Worker لمعالجة الملفات الفيديو"""
    
    def __init__(self, interval=120):  # 120 ثانية = 2 دقيقة
        self.running = False
        self.thread = None
        self.interval = interval
        self.db = None  # سيتم إنشاؤه في الـ thread
    
    def start(self):
        """بدء الـ Worker"""
        if self.running:
            logger.warning("⚠️ Video Worker قيد التشغيل بالفعل")
            return
        
        self.running = True
        logger.info(f"✅ تم بدء Video Worker (كل {self.interval} ثانية)")
        self._run()
    
    def stop(self):
        """إيقاف الـ Worker"""
        self.running = False
        if self.db:
            self.db.close()
        logger.info("🛑 تم إيقاف Video Worker")
    
    def run_once(self):
        """تشغيل دورة واحدة من معالجة الملفات الفيديو"""
        try:
            # إنشاء connection منفصلة
            db = DatabaseConnection()
            if not db.connect():
                logger.error("❌ فشل الاتصال بقاعدة البيانات")
                return False
            
            logger.info(f"🎬 جاري معالجة الملفات الفيديو في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # البحث عن الملفات الفيديو المعلقة
            result = self._process_pending_videos_once(db)
            
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"❌ خطأ في Video run_once: {e}")
            return False
    
    def _process_pending_videos_once(self, db):
        """معالجة الملفات الفيديو المعلقة - دورة واحدة"""
        try:
            # البحث عن الملفات الفيديو بحالة pending
            query = """
                SELECT id, s3_url, content_type 
                FROM public.uploaded_files 
                WHERE status = 'pending' AND content_type LIKE 'video/%'
                LIMIT 5
            """
            
            db.cursor.execute(query)
            pending_videos = db.cursor.fetchall()
            
            if not pending_videos:
                logger.info("ℹ️ لا توجد ملفات فيديو معلقة")
                return True
            
            logger.info(f"📋 وجدت {len(pending_videos)} ملف فيديو معلق")
            
            for video_record in pending_videos:
                file_id = video_record['id'] if isinstance(video_record, dict) else video_record[0]
                s3_url = video_record['s3_url'] if isinstance(video_record, dict) else video_record[1]
                
                try:
                    logger.info(f"🎬 جاري معالجة ملف فيديو: {file_id}")
                    VideoProcessingJob.process_video_file(file_id, s3_url, db=db)
                except Exception as e:
                    logger.error(f"❌ خطأ في معالجة الملف {file_id}: {e}")
            
            return True
                
        except Exception as e:
            logger.error(f"❌ خطأ في البحث عن الملفات الفيديو المعلقة: {e}")
            return False
    
    def _process_pending_videos(self):
        """معالجة الملفات الفيديو المعلقة"""
        try:
            # البحث عن الملفات الفيديو بحالة pending
            query = """
                SELECT id, s3_url, content_type 
                FROM public.uploaded_files 
                WHERE status = 'pending' AND content_type LIKE 'video/%'
                LIMIT 5
            """
            
            self.db.cursor.execute(query)
            pending_videos = self.db.cursor.fetchall()
            
            if not pending_videos:
                logger.info("ℹ️ لا توجد ملفات فيديو معلقة")
                return
            
            logger.info(f"📋 وجدت {len(pending_videos)} ملف فيديو معلق")
            
            for video_record in pending_videos:
                file_id = video_record['id'] if isinstance(video_record, dict) else video_record[0]
                s3_url = video_record['s3_url'] if isinstance(video_record, dict) else video_record[1]
                
                try:
                    logger.info(f"🎬 جاري معالجة ملف فيديو: {file_id}")
                    VideoProcessingJob.process_video_file(file_id, s3_url, db=self.db)
                except Exception as e:
                    logger.error(f"❌ خطأ في معالجة الملف {file_id}: {e}")
                
        except Exception as e:
            logger.error(f"❌ خطأ في البحث عن الملفات الفيديو المعلقة: {e}")


def main():
    """تشغيل الـ Video Worker"""
    logger.info("🎬 جاري بدء Video Worker...")
    
    # بدء الـ Worker
    worker = VideoWorker(interval=120)  # 2 دقيقة
    worker.start()
    
    try:
        logger.info("✅ Video Worker يعمل الآن...")
        # الاستمرار في التشغيل
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 جاري إيقاف Video Worker...")
        worker.stop()
        logger.info("✅ تم إيقاف Video Worker")


if __name__ == "__main__":
    main()
