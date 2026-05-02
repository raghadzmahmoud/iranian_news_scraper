"""
X Scraper Job - جدولة سحب X
"""
import asyncio
from scrapers.x_scraper import scrape_all_x_sources
from database.connection import db
from utils.logger import logger


async def run_x_scraper_job():
    """
    وظيفة سحب X - تُشغل بشكل دوري
    """
    logger.info("🐦 بدء وظيفة سحب X...")
    
    try:
        # الاتصال بقاعدة البيانات (بدون إغلاق في النهاية)
        db.ensure_connection()
        
        # سحب من جميع المصادر
        stats = await scrape_all_x_sources()
        
        logger.info(f"✅ انتهت وظيفة سحب X")
        logger.info(f"   تم حفظ: {stats.get('total_saved', 0)} تغريدة")
        
        return stats
    
    except Exception as e:
        logger.error(f"❌ خطأ في وظيفة سحب X: {e}")
        return None
    
    # لا نُغلق الاتصال هنا - يبقى مفتوح للـ workers الأخرى


def sync_run_x_scraper_job():
    """
    نسخة متزامنة من وظيفة سحب X
    للاستخدام مع APScheduler
    """
    return asyncio.run(run_x_scraper_job())


if __name__ == "__main__":
    # اختبار الوظيفة
    asyncio.run(run_x_scraper_job())
