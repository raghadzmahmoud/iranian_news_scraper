"""
Worker منفصل لمعالجة الـ Scraping Jobs
Scraper Worker - يعمل كل 10 دقايق
"""
import time
import threading
from datetime import datetime
from database.connection import DatabaseConnection
from utils.logger import logger
from main import scrape_all_news, scrape_telegram_sources, save_telegram_posts_to_db


class ScraperWorker:
    """Worker لمعالجة الـ Scraping Jobs"""
    
    def __init__(self, interval=600):  # 600 ثانية = 10 دقايق
        self.running = False
        self.thread = None
        self.interval = interval
        self.db = None  # سيتم إنشاؤه في الـ thread
    
    def start(self):
        """بدء الـ Worker"""
        if self.running:
            logger.warning("⚠️ Scraper Worker قيد التشغيل بالفعل")
            return
        
        self.running = True
        logger.info(f"✅ تم بدء Scraper Worker (كل {self.interval} ثانية)")
        self._run()
    
    def stop(self):
        """إيقاف الـ Worker"""
        self.running = False
        if self.db:
            self.db.close()
        logger.info("🛑 تم إيقاف Scraper Worker")
    
    def _run(self):
        """تشغيل الـ Worker"""
        logger.info("🚀 جاري تشغيل Scraper Worker...")
        
        # إنشاء connection منفصلة لهذا الـ thread
        self.db = DatabaseConnection()
        if not self.db.connect():
            logger.error("❌ فشل الاتصال بقاعدة البيانات")
            return
        
        while self.running:
            try:
                logger.info(f"📰 جاري تشغيل Scraper Job في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # ========================================
                # Step 1: سحب الأخبار من RSS
                # ========================================
                logger.info("📰 جاري سحب الأخبار من RSS...")
                try:
                    rss_articles = scrape_all_news(db_connection=self.db)
                    if rss_articles:
                        logger.info(f"✅ تم سحب {len(rss_articles)} مقالة من RSS")
                    else:
                        logger.info("ℹ️ لا توجد أخبار جديدة من RSS")
                except Exception as e:
                    logger.error(f"❌ خطأ في سحب أخبار RSS: {e}")
                
                # ========================================
                # Step 2: سحب البوستات من Telegram
                # ========================================
                logger.info("📱 جاري سحب البوستات من Telegram...")
                try:
                    telegram_posts = scrape_telegram_sources(max_posts=30, db_connection=self.db)
                    if telegram_posts:
                        logger.info(f"✅ تم سحب {len(telegram_posts)} بوست من Telegram")
                        # حفظ البوستات في قاعدة البيانات
                        save_telegram_posts_to_db(telegram_posts, filter_enabled=True, db_connection=self.db)
                    else:
                        logger.info("ℹ️ لا توجد بوستات جديدة من Telegram")
                except Exception as e:
                    logger.error(f"❌ خطأ في سحب بوستات Telegram: {e}")
                
                logger.info(f"✅ انتهت دورة الـ Scraping في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # الانتظار للـ interval المحدد
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"❌ خطأ في Scraper Worker: {e}")
                time.sleep(self.interval)


def main():
    """تشغيل الـ Scraper Worker"""
    logger.info("📰 جاري بدء Scraper Worker...")
    
    # بدء الـ Worker
    worker = ScraperWorker(interval=600)  # 10 دقايق
    worker.start()
    
    try:
        logger.info("✅ Scraper Worker يعمل الآن...")
        # الاستمرار في التشغيل
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 جاري إيقاف Scraper Worker...")
        worker.stop()
        logger.info("✅ تم إيقاف Scraper Worker")


if __name__ == "__main__":
    main()
