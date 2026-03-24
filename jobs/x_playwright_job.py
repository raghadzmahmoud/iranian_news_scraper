"""
X Playwright Job - runs the Playwright-only scraper via APScheduler.
"""
import asyncio
from run_x_playwright import run as run_playwright_scraper
from utils.logger import logger


async def run_x_playwright_job():
    """
    Job wrapper that executes the Playwright scraper and logs stats.
    """
    logger.info("🐦 Starting Playwright-only X scraping job...")

    try:
        stats = await run_playwright_scraper()
        logger.info("✅ Playwright X scraping job completed.")
        logger.info(f"   Total saved: {stats.get('total_saved', 0)}")
        logger.info(f"   Duplicates skipped: {stats.get('total_duplicates', 0)}")
        logger.info(f"   Number-filtered articles: {stats.get('total_numbers_filtered', 0)}")
        return stats

    except Exception as exc:
        logger.error(f"❌ Playwright X scraping job failed: {exc}")
        return None


def sync_run_x_playwright_job():
    """
    Synchronous entrypoint for scheduler integration.
    """
    return asyncio.run(run_x_playwright_job())


if __name__ == "__main__":
    asyncio.run(run_x_playwright_job())
