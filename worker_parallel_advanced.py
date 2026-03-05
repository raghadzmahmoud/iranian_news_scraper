"""
وركر متوازي متقدم للسحب والترجمة
يستخدم ThreadPoolExecutor و APScheduler
السحب: كل 5 دقايق
الترجمة: كل 10 دقايق
عدد الوركرز: 2
"""
import asyncio
import threading
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor as APSchedulerThreadPoolExecutor
from scrapers.db_rss_scraper import scrape_all_sources_and_save
from jobs.translation_job import run_translation_job
from utils.logger import logger


class AdvancedParallelWorker:
    """وركر متوازي متقدم مع ThreadPoolExecutor"""
    
    def __init__(self, num_workers: int = 2):
        self.num_workers = num_workers
        self.is_running = False
        
        # إعداد الجدولة مع ThreadPoolExecutor
        executors = {
            'default': APSchedulerThreadPoolExecutor(max_workers=num_workers)
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 1
        }
        
        self.scheduler = BackgroundScheduler(
            executors=executors,
            job_defaults=job_defaults
        )
        
        # عداد للمهام
        self.scraping_count = 0
        self.translation_count = 0
        self.scraping_lock = threading.Lock()
        self.translation_lock = threading.Lock()
    
    def run_scraping(self):
        """تشغيل السحب"""
        with self.scraping_lock:
            self.scraping_count += 1
            count = self.scraping_count
        
        try:
            logger.info(f"🔄 [السحب #{count}] بدء السحب في {datetime.now()}")
            result = scrape_all_sources_and_save(max_items=10)
            
            total_scraped = result.get('total_scraped', 0)
            total_saved = result.get('total_saved', 0)
            
            logger.info(f"✅ [السحب #{count}] انتهى: {total_scraped} مقالة، {total_saved} محفوظة")
            
        except Exception as e:
            logger.error(f"❌ [السحب #{count}] خطأ: {e}")
    
    def run_translation(self):
        """تشغيل الترجمة"""
        with self.translation_lock:
            self.translation_count += 1
            count = self.translation_count
        
        try:
            logger.info(f"🔄 [الترجمة #{count}] بدء الترجمة في {datetime.now()}")
            result = asyncio.run(run_translation_job())
            
            success = result.get('success', 0)
            failed = result.get('failed', 0)
            
            logger.info(f"✅ [الترجمة #{count}] انتهت: {success} نجح، {failed} فشل")
            
        except Exception as e:
            logger.error(f"❌ [الترجمة #{count}] خطأ: {e}")
    
    def start(self):
        """بدء الوركر"""
        if self.is_running:
            logger.warning("⚠️  الوركر يعمل بالفعل")
            return
        
        logger.info("="*80)
        logger.info(f"🚀 بدء الوركر المتوازي المتقدم")
        logger.info(f"   عدد الوركرز: {self.num_workers}")
        logger.info(f"   السحب: كل 5 دقايق")
        logger.info(f"   الترجمة: كل 10 دقايق")
        logger.info("="*80)
        
        # جدولة السحب كل 5 دقايق
        self.scheduler.add_job(
            self.run_scraping,
            'interval',
            minutes=5,
            id='scraping_job',
            name='سحب الأخبار',
            next_run_time=datetime.now()  # تشغيل فوري
        )
        logger.info("📅 تم جدولة السحب: كل 5 دقايق (تشغيل فوري)")
        
        # جدولة الترجمة كل 10 دقايق
        self.scheduler.add_job(
            self.run_translation,
            'interval',
            minutes=10,
            id='translation_job',
            name='ترجمة الأخبار',
            next_run_time=datetime.now()  # تشغيل فوري
        )
        logger.info("📅 تم جدولة الترجمة: كل 10 دقايق (تشغيل فوري)")
        
        # بدء الجدولة
        self.scheduler.start()
        self.is_running = True
        
        logger.info("✅ الوركر المتوازي يعمل الآن")
        logger.info("   اضغط Ctrl+C للإيقاف")
        
        # الاحتفاظ بالبرنامج مشغول
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n⏹️  إيقاف الوركر...")
            self.stop()
    
    def stop(self):
        """إيقاف الوركر"""
        if not self.is_running:
            logger.warning("⚠️  الوركر لم يكن يعمل")
            return
        
        logger.info("🛑 إيقاف الوركر المتوازي...")
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        
        logger.info("="*80)
        logger.info("✅ تم إيقاف الوركر")
        logger.info(f"   إجمالي عمليات السحب: {self.scraping_count}")
        logger.info(f"   إجمالي عمليات الترجمة: {self.translation_count}")
        logger.info("="*80)
    
    def get_status(self):
        """الحصول على حالة الوركر"""
        return {
            'is_running': self.is_running,
            'num_workers': self.num_workers,
            'scraping_count': self.scraping_count,
            'translation_count': self.translation_count,
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': str(job.next_run_time)
                }
                for job in self.scheduler.get_jobs()
            ] if self.is_running else []
        }


def main():
    """نقطة الدخول الرئيسية"""
    logger.info("🚀 وركر متوازي متقدم للسحب والترجمة")
    
    # إنشاء الوركر مع 2 وركر
    worker = AdvancedParallelWorker(num_workers=2)
    
    # بدء الوركر
    worker.start()


if __name__ == "__main__":
    main()
