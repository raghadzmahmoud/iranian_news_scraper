"""
Worker منفصل لمعالجة الملفات الصوتية فقط
Audio Processing Worker - يعمل كل 2 دقيقة
"""
import time
import threading
from datetime import datetime
from database.connection import DatabaseConnection
from utils.logger import logger
from jobs.audio_processing_job import AudioProcessingJob


class AudioWorker:
    """Worker لمعالجة الملفات الصوتية"""
    
    def __init__(self, interval=120):  # 120 ثانية = 2 دقيقة
        self.running = False
        self.thread = None
        self.interval = interval
        self.db = None  # سيتم إنشاؤه في الـ thread
    
    def start(self):
        """بدء الـ Worker"""
        if self.running:
            logger.warning("⚠️ Audio Worker قيد التشغيل بالفعل")
            return
        
        self.running = True
        logger.info(f"✅ تم بدء Audio Worker (كل {self.interval} ثانية)")
        self._run()
    
    def stop(self):
        """إيقاف الـ Worker"""
        self.running = False
        if self.db:
            self.db.close()
        logger.info("🛑 تم إيقاف Audio Worker")
    
    def _run(self):
        """تشغيل الـ Worker"""
        logger.info("🚀 جاري تشغيل Audio Worker...")
        
        # إنشاء connection منفصلة لهذا الـ thread
        self.db = DatabaseConnection()
        if not self.db.connect():
            logger.error("❌ فشل الاتصال بقاعدة البيانات")
            return
        
        while self.running:
            try:
                logger.info(f"🎙️ جاري معالجة الملفات الصوتية في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # البحث عن الملفات الصوتية المعلقة
                self._process_pending_audios()
                
                # الانتظار للـ interval المحدد
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"❌ خطأ في Audio Worker: {e}")
                time.sleep(self.interval)
    
    def _process_pending_audios(self):
        """معالجة الملفات الصوتية المعلقة"""
        try:
            # البحث عن الملفات الصوتية بحالة pending
            query = """
                SELECT id, s3_url, content_type 
                FROM public.uploaded_files 
                WHERE status = 'pending' AND content_type LIKE 'audio/%'
                LIMIT 5
            """
            
            self.db.cursor.execute(query)
            pending_audios = self.db.cursor.fetchall()
            
            if not pending_audios:
                logger.info("ℹ️ لا توجد ملفات صوتية معلقة")
                return
            
            logger.info(f"📋 وجدت {len(pending_audios)} ملف صوتي معلق")
            
            for audio_record in pending_audios:
                file_id = audio_record['id'] if isinstance(audio_record, dict) else audio_record[0]
                s3_url = audio_record['s3_url'] if isinstance(audio_record, dict) else audio_record[1]
                
                try:
                    logger.info(f"🎙️ جاري معالجة ملف صوتي: {file_id}")
                    AudioProcessingJob.process_audio_file(file_id, s3_url, db=self.db)
                except Exception as e:
                    logger.error(f"❌ خطأ في معالجة الملف {file_id}: {e}")
                
        except Exception as e:
            logger.error(f"❌ خطأ في البحث عن الملفات الصوتية المعلقة: {e}")


def main():
    """تشغيل الـ Audio Worker"""
    logger.info("🎙️ جاري بدء Audio Worker...")
    
    # بدء الـ Worker
    worker = AudioWorker(interval=120)  # 2 دقيقة
    worker.start()
    
    try:
        logger.info("✅ Audio Worker يعمل الآن...")
        # الاستمرار في التشغيل
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 جاري إيقاف Audio Worker...")
        worker.stop()
        logger.info("✅ تم إيقاف Audio Worker")


if __name__ == "__main__":
    main()
