"""
وركر متوازي للسحب والترجمة
يشغل السحب كل 5 دقايق والترجمة كل 10 دقايق بشكل متوازي
"""
import asyncio
import threading
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from scrapers.db_rss_scraper import scrape_all_sources_and_save, load_rss_sources_from_db
from jobs.translation_job import run_translation_job
from utils.logger import logger


class ParallelWorker:
    """وركر متوازي للسحب والترجمة"""
    
    def __init__(self, num_workers: int = 2):
        self.num_workers = num_workers
        self.scheduler = BackgroundScheduler()
        self.scraping_thread = None
        self.translation_thread = None
        self.is_running = False
    
    def run_scraping(self):
        """تشغيل السحب في thread منفصل"""
        try:
            logger.info(f"🔄 بدء السحب في الوقت: {datetime.now()}")
            
            # طباعة المصادر قبل السحب
            sources = load_rss_sources_from_db()
            if sources:
                logger.info("="*80)
                logger.info(f"📋 المصادر المتاحة للسحب ({len(sources)} مصدر):")
                logger.info("="*80)
                for source_id, source_info in sources.items():
                    logger.info(f"   🔹 [{source_id}] {source_info['name']}")
                    logger.info(f"      URL: {source_info['url']}")
                    logger.info(f"      النوع: {source_info['type']}")
                    logger.info(f"      نشط: {'✅' if source_info['active'] else '❌'}")
                    logger.info("-"*80)
                logger.info("="*80)
            
            result = scrape_all_sources_and_save(max_items=10)
            logger.info(f"✅ انتهى السحب: {result}")
        except Exception as e:
            logger.error(f"❌ خطأ في السحب: {e}")
    
    def run_translation(self):
        """تشغيل الترجمة في thread منفصل"""
        try:
            logger.info(f"🔄 بدء الترجمة في الوقت: {datetime.now()}")
            result = asyncio.run(run_translation_job())
            logger.info(f"✅ انتهت الترجمة: {result}")
        except Exception as e:
            logger.error(f"❌ خطأ في الترجمة: {e}")
    
    def schedule_scraping(self):
        """جدولة السحب كل 10 دقايق"""
        self.scheduler.add_job(
            self.run_scraping,
            'interval',
            minutes=10,
            id='scraping_job',
            name='سحب الأخبار',
            max_instances=1
        )
        logger.info("📅 تم جدولة السحب كل 10 دقايق")
    
    def schedule_translation(self):
        """جدولة الترجمة كل 15 دقايق"""
        self.scheduler.add_job(
            self.run_translation,
            'interval',
            minutes=15,
            id='translation_job',
            name='ترجمة الأخبار',
            max_instances=1
        )
        logger.info("📅 تم جدولة الترجمة كل 15 دقايق")
    
    def start(self):
        """بدء الوركر"""
        if self.is_running:
            logger.warning("⚠️  الوركر يعمل بالفعل")
            return
        
        logger.info(f"🚀 بدء الوركر المتوازي مع {self.num_workers} وركر")
        
        # جدولة المهام
        self.schedule_scraping()
        self.schedule_translation()
        
        # بدء الجدولة
        self.scheduler.start()
        self.is_running = True
        
        logger.info("✅ الوركر المتوازي يعمل الآن")
        logger.info("   📊 السحب: كل 5 دقايق")
        logger.info("   📊 الترجمة: كل 10 دقايق")
        
        # الاحتفاظ بالبرنامج مشغول
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("⏹️  إيقاف الوركر...")
            self.stop()
    
    def stop(self):
        """إيقاف الوركر"""
        if not self.is_running:
            logger.warning("⚠️  الوركر لم يكن يعمل")
            return
        
        logger.info("🛑 إيقاف الوركر المتوازي...")
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("✅ تم إيقاف الوركر")


def main():
    """نقطة الدخول الرئيسية"""
    logger.info("="*80)
    logger.info("🚀 وركر متوازي للسحب والترجمة")
    logger.info("="*80)
    
    # إنشاء الوركر مع عدد الوركرز
    worker = ParallelWorker(num_workers=2)
    
    # بدء الوركر
    worker.start()


if __name__ == "__main__":
    main()
