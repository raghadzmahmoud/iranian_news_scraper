"""
Worker منفصل لمعالجة الـ Background Jobs
Separate Worker for Background Job Processing
"""
import time
from database.connection import db
from utils.logger import logger
from jobs.scheduler import JobScheduler


def main():
    """تشغيل الـ Worker"""
    logger.info("🚀 جاري بدء الـ Worker...")
    
    # الاتصال بقاعدة البيانات
    if not db.connect():
        logger.error("❌ فشل الاتصال بقاعدة البيانات")
        return
    
    logger.info("✅ تم الاتصال بقاعدة البيانات")
    
    # بدء جدولة الـ Background Jobs
    scheduler = JobScheduler()
    scheduler.start()
    
    try:
        logger.info("✅ الـ Worker يعمل الآن...")
        # الاستمرار في التشغيل
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 جاري إيقاف الـ Worker...")
        scheduler.stop()
        db.close()
        logger.info("✅ تم إيقاف الـ Worker")


if __name__ == "__main__":
    main()
