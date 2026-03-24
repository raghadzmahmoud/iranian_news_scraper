"""
Job scheduler for running the Playwright-only X scraper every hour.
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from jobs.x_playwright_job import sync_run_x_playwright_job
from utils.logger import logger


def main():
    """Entry point for the scheduler."""
    logger.info("=" * 60)
    logger.info("🐦 Playwright X Scraper Scheduler")
    logger.info("=" * 60)

    scheduler = BlockingScheduler()

    scheduler.add_job(
        sync_run_x_playwright_job,
        trigger=IntervalTrigger(hours=1),
        id="x_playwright_job",
        name="Playwright X Scraper Job",
        replace_existing=True,
        max_instances=1,
    )

    logger.info("✔️ تم جدولة وظيفة سحب X عبر Playwright - كل ساعة")
    logger.info("🕓 جاري تشغيل الجولة الأولى...")

    try:
        sync_run_x_playwright_job()
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):
        logger.info("⏸️ إيقاف الجدولة...")
        scheduler.shutdown()
        logger.info("✔️ تم إيقاف الجدولة")


if __name__ == "__main__":
    main()
