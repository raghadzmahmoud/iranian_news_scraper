"""
Main Worker - يشغل جميع الـ Workers بـ Multi-Threading
Main Worker - Runs all workers in parallel using threads
"""
import time
import threading
from utils.logger import logger
from worker_scraper import ScraperWorker
from worker_audio import AudioWorker
from worker_video import VideoWorker


def main():
    """تشغيل جميع الـ Workers بـ Multi-Threading"""
    logger.info("🚀 جاري بدء Main Worker...")
    
    # قائمة الـ Workers
    workers_config = [
        {
            "name": "Scraper Worker",
            "worker_class": ScraperWorker,
            "interval": 600,  # 10 دقايق
            "emoji": "📰"
        },
        {
            "name": "Audio Worker",
            "worker_class": AudioWorker,
            "interval": 120,  # 2 دقيقة
            "emoji": "🎙️"
        },
        {
            "name": "Video Worker",
            "worker_class": VideoWorker,
            "interval": 120,  # 2 دقيقة
            "emoji": "🎬"
        }
    ]
    
    # طباعة معلومات الـ Workers
    logger.info("=" * 60)
    logger.info("📋 الـ Workers المتاحة:")
    for config in workers_config:
        interval_minutes = config['interval'] // 60
        logger.info(f"  {config['emoji']} {config['name']} - كل {interval_minutes} دقايق")
    logger.info("=" * 60)
    
    # إنشاء وتشغيل الـ Workers
    workers = []
    threads = []
    
    try:
        for config in workers_config:
            logger.info(f"🚀 جاري بدء {config['name']}...")
            
            # إنشاء instance من الـ Worker
            worker = config['worker_class'](interval=config['interval'])
            workers.append(worker)
            
            # إنشاء thread للـ Worker
            thread = threading.Thread(
                target=worker.start,
                name=config['name'],
                daemon=False
            )
            threads.append(thread)
            
            # بدء الـ Thread
            thread.start()
            logger.info(f"✅ تم بدء {config['name']} (Thread ID: {thread.ident})")
        
        logger.info("=" * 60)
        logger.info("✅ جميع الـ Workers تعمل الآن في نفس الـ Process...")
        logger.info(f"📊 عدد الـ Threads: {threading.active_count()}")
        logger.info("=" * 60)
        
        # الانتظار حتى يتم إيقاف البرنامج
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 جاري إيقاف جميع الـ Workers...")
        
        # إيقاف جميع الـ Workers
        for worker in workers:
            try:
                worker.stop()
                logger.info(f"✅ تم إيقاف {worker.__class__.__name__}")
            except Exception as e:
                logger.error(f"❌ خطأ في إيقاف {worker.__class__.__name__}: {e}")
        
        # انتظار انتهاء جميع الـ Threads
        for thread in threads:
            thread.join(timeout=5)
        
        logger.info("✅ تم إيقاف جميع الـ Workers")


if __name__ == "__main__":
    main()
