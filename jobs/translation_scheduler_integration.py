"""
تكامل Translation Job مع Scheduler الموجود
Integration of Translation Job with existing Scheduler
"""

import asyncio
import threading
import time
from datetime import datetime
from utils.logger import logger
from jobs.translation_job import TranslationJob


class TranslationSchedulerIntegration:
    """تكامل وظيفة الترجمة مع جدولة الـ Jobs"""

    def __init__(self, interval_seconds: int = 300, batch_size: int = 50):
        """
        Initialize translation scheduler integration
        
        Args:
            interval_seconds: Interval between translation runs (default: 5 minutes)
            batch_size: Number of articles to translate per run (default: 50)
        """
        self.interval_seconds = interval_seconds
        self.batch_size = batch_size
        self.running = False
        self.thread = None
        self.translation_job = TranslationJob(max_concurrent=5)

    def start(self):
        """Start translation scheduler"""
        if self.running:
            logger.warning("⚠️ Translation scheduler already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info(
            f"✅ Translation scheduler started (interval: {self.interval_seconds}s)"
        )

    def stop(self):
        """Stop translation scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("🛑 Translation scheduler stopped")

    def _run_scheduler(self):
        """Run translation scheduler loop"""
        logger.info("🚀 Translation scheduler running...")

        while self.running:
            try:
                # Run translation job
                logger.info(f"📝 Starting translation job at {datetime.now()}")
                result = asyncio.run(
                    self.translation_job.run(batch_size=self.batch_size)
                )

                # Log result
                if result.get("status") == "success":
                    logger.info(
                        f"✅ Translation job completed: "
                        f"{result.get('success', 0)} translated, "
                        f"{result.get('failed', 0)} failed"
                    )
                else:
                    logger.error(f"❌ Translation job failed: {result.get('message')}")

                # Wait for next interval
                logger.info(
                    f"⏳ Next translation job in {self.interval_seconds} seconds"
                )
                time.sleep(self.interval_seconds)

            except Exception as e:
                logger.error(f"❌ Translation scheduler error: {e}")
                time.sleep(self.interval_seconds)


# Global instance
translation_scheduler = TranslationSchedulerIntegration(
    interval_seconds=300,  # 5 minutes
    batch_size=50,
)


def start_translation_scheduler():
    """Start the translation scheduler"""
    translation_scheduler.start()


def stop_translation_scheduler():
    """Stop the translation scheduler"""
    translation_scheduler.stop()
