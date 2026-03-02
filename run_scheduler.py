"""
تشغيل الـ Background Job Scheduler
Run Background Job Scheduler
"""
from jobs.scheduler import job_scheduler
import time
import signal
from utils.logger import logger


def signal_handler(sig, frame):
    """معالج إشارة الإيقاف"""
    logger.info('\n🛑 إيقاف الـ scheduler...')
    job_scheduler.stop()
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("🚀 بدء الـ scheduler...")
    job_scheduler.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        job_scheduler.stop()
