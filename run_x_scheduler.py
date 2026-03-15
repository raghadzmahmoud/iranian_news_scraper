"""
جدولة سحب X - يشغل السحب كل ساعة
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from jobs.x_scraper_job import sync_run_x_scraper_job
from utils.logger import logger


def main():
    """الدالة الرئيسية"""
    logger.info("=" * 60)
    logger.info("🐦 X Scraper Scheduler")
    logger.info("=" * 60)
    
    # إنشاء الجدولة
    scheduler = BlockingScheduler()
    
    # إضافة وظيفة سحب X - كل ساعة
    scheduler.add_job(
        sync_run_x_scraper_job,
        trigger=IntervalTrigger(hours=1),
        id='x_scraper_job',
        name='X Scraper Job',
        replace_existing=True,
        max_instances=1
    )
    
    logger.info("✅ تم جدولة وظيفة سحب X - كل ساعة")
    logger.info("🚀 بدء الجدولة...")
    
    try:
        # تشغيل مرة واحدة عند البدء
        logger.info("\n🔄 تشغيل أول مرة...")
        sync_run_x_scraper_job()
        
        # بدء الجدولة
        scheduler.start()
    
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n🛑 إيقاف الجدولة...")
        scheduler.shutdown()
        logger.info("✅ تم إيقاف الجدولة")


if __name__ == "__main__":
    main()
