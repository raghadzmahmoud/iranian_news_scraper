"""
وركر متوازي محسّن للسحب والترجمة
يشغل السحب كل 10 دقايق والترجمة كل 15 دقيقة بشكل متوازي حقيقي
"""
import asyncio
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from scrapers.db_rss_scraper import scrape_all_sources_and_save, load_rss_sources_from_db
from jobs.translation_job import run_translation_job
from utils.logger import logger


class ParallelWorker:
    """وركر متوازي للسحب والترجمة"""
    
    def __init__(self, 
                 scraping_interval: int = 10,
                 translation_interval: int = 15,
                 print_sources: bool = False,
                 max_workers: int = 2):
        """
        Args:
            scraping_interval: فترة السحب بالدقائق (افتراضي: 10)
            translation_interval: فترة الترجمة بالدقائق (افتراضي: 15)
            print_sources: طباعة المصادر في كل دورة (افتراضي: False)
            max_workers: عدد الـ threads المتوازية (افتراضي: 2)
        """
        self.scraping_interval = scraping_interval
        self.translation_interval = translation_interval
        self.print_sources = print_sources
        self.max_workers = max_workers
        
        # إعداد الجدولة مع ThreadPoolExecutor للتشغيل المتوازي
        executors = {
            'default': ThreadPoolExecutor(max_workers=max_workers)
        }
        
        job_defaults = {
            'coalesce': False,  # لا تدمج المهام المتأخرة
            'max_instances': 1  # مهمة واحدة من كل نوع في نفس الوقت
        }
        
        self.scheduler = BackgroundScheduler(
            executors=executors,
            job_defaults=job_defaults
        )
        self.is_running = False
        
        # إحصائيات
        self.scraping_count = 0
        self.translation_count = 0
        self.last_scraping_time = None
        self.last_translation_time = None
        self.scraping_errors = 0
        self.translation_errors = 0
    
    def run_scraping(self):
        """تشغيل السحب"""
        self.scraping_count += 1
        try:
            logger.info(f"🔄 [السحب #{self.scraping_count}] بدء السحب في {datetime.now()}")
            
            # طباعة المصادر إذا كان مفعّل
            if self.print_sources:
                sources = load_rss_sources_from_db()
                if sources:
                    logger.info("="*80)
                    logger.info(f"📋 المصادر المتاحة ({len(sources)} مصدر):")
                    for source_id, source_info in sources.items():
                        logger.info(f"   🔹 [{source_id}] {source_info['name']} - {source_info['url']}")
                    logger.info("="*80)
            
            result = scrape_all_sources_and_save(max_items=10)
            self.last_scraping_time = datetime.now()
            
            # طباعة ملخص النتائج
            total_scraped = result.get('total_scraped', 0)
            total_saved = result.get('total_saved', 0)
            logger.info(f"✅ [السحب #{self.scraping_count}] انتهى: {total_scraped} مقالة، {total_saved} محفوظة")
            
        except Exception as e:
            self.scraping_errors += 1
            logger.error(f"❌ [السحب #{self.scraping_count}] خطأ: {e}")
    
    def run_translation(self):
        """تشغيل الترجمة"""
        self.translation_count += 1
        try:
            logger.info(f"🔄 [الترجمة #{self.translation_count}] بدء الترجمة في {datetime.now()}")
            result = asyncio.run(run_translation_job())
            self.last_translation_time = datetime.now()
            
            # طباعة ملخص النتائج
            success = result.get('success', 0)
            failed = result.get('failed', 0)
            logger.info(f"✅ [الترجمة #{self.translation_count}] انتهت: {success} نجح، {failed} فشل")
            
        except Exception as e:
            self.translation_errors += 1
            logger.error(f"❌ [الترجمة #{self.translation_count}] خطأ: {e}")
    
    def print_initial_sources(self):
        """طباعة المصادر عند البدء"""
        try:
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
            else:
                logger.warning("⚠️  لا توجد مصادر متاحة")
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل المصادر: {e}")
    
    def start(self):
        """بدء الوركر"""
        if self.is_running:
            logger.warning("⚠️  الوركر يعمل بالفعل")
            return
        
        logger.info("="*80)
        logger.info("🚀 بدء الوركر المتوازي")
        logger.info(f"   � عدد الـ Workers: {self.max_workers}")
        logger.info(f"   �📊 السحب: كل {self.scraping_interval} دقيقة")
        logger.info(f"   📊 الترجمة: كل {self.translation_interval} دقيقة")
        logger.info(f"   ⚡ التشغيل: متوازي (يمكن تشغيل السحب والترجمة معاً)")
        logger.info("="*80)
        
        # طباعة المصادر عند البدء
        self.print_initial_sources()
        
        # جدولة السحب مع تشغيل فوري
        self.scheduler.add_job(
            self.run_scraping,
            'interval',
            minutes=self.scraping_interval,
            id='scraping_job',
            name='سحب الأخبار',
            max_instances=1,
            next_run_time=datetime.now()  # تشغيل فوري
        )
        logger.info(f"📅 تم جدولة السحب: كل {self.scraping_interval} دقيقة (تشغيل فوري)")
        
        # جدولة الترجمة مع تشغيل فوري
        self.scheduler.add_job(
            self.run_translation,
            'interval',
            minutes=self.translation_interval,
            id='translation_job',
            name='ترجمة الأخبار',
            max_instances=1,
            next_run_time=datetime.now()  # تشغيل فوري
        )
        logger.info(f"📅 تم جدولة الترجمة: كل {self.translation_interval} دقيقة (تشغيل فوري)")
        
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
        
        # طباعة الإحصائيات
        logger.info("="*80)
        logger.info("📊 إحصائيات الوركر:")
        logger.info(f"   🔄 عمليات السحب: {self.scraping_count} (أخطاء: {self.scraping_errors})")
        logger.info(f"   🔄 عمليات الترجمة: {self.translation_count} (أخطاء: {self.translation_errors})")
        if self.last_scraping_time:
            logger.info(f"   ⏰ آخر سحب: {self.last_scraping_time}")
        if self.last_translation_time:
            logger.info(f"   ⏰ آخر ترجمة: {self.last_translation_time}")
        logger.info("="*80)
        logger.info("✅ تم إيقاف الوركر")
    
    def get_status(self):
        """الحصول على حالة الوركر"""
        return {
            'is_running': self.is_running,
            'max_workers': self.max_workers,
            'scraping_interval': self.scraping_interval,
            'translation_interval': self.translation_interval,
            'scraping_count': self.scraping_count,
            'translation_count': self.translation_count,
            'scraping_errors': self.scraping_errors,
            'translation_errors': self.translation_errors,
            'last_scraping_time': str(self.last_scraping_time) if self.last_scraping_time else None,
            'last_translation_time': str(self.last_translation_time) if self.last_translation_time else None,
        }


def main():
    """نقطة الدخول الرئيسية"""
    logger.info("="*80)
    logger.info("🚀 وركر متوازي محسّن للسحب والترجمة")
    logger.info("="*80)
    
    # إنشاء الوركر
    # يمكنك تغيير الإعدادات هنا:
    # - scraping_interval: فترة السحب بالدقائق
    # - translation_interval: فترة الترجمة بالدقائق
    # - print_sources: طباعة المصادر في كل دورة
    # - max_workers: عدد الـ threads المتوازية (2 = يمكن تشغيل السحب والترجمة معاً)
    worker = ParallelWorker(
        scraping_interval=10,
        translation_interval=15,
        print_sources=False,  # غيّر إلى True لطباعة المصادر في كل دورة
        max_workers=2  # 2 threads = يمكن تشغيل مهمتين معاً
    )
    
    # بدء الوركر
    worker.start()


if __name__ == "__main__":
    main()
