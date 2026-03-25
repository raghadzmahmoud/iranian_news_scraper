#!/usr/bin/env python
"""
Local X Scraper Runner - تشغيل السحب من X محليًا
"""
import asyncio
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, '.')

from run_x_playwright import run
from utils.logger import logger


async def main():
    """Run the X scraper locally"""
    logger.info("=" * 60)
    logger.info("🚀 Starting Local X Scraper")
    logger.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        stats = await run()
        
        logger.info("=" * 60)
        logger.info("✅ Scraping completed successfully!")
        logger.info("=" * 60)
        
        if stats:
            logger.info(f"📊 Summary:")
            logger.info(f"   Total sources: {stats.get('total_sources', 0)}")
            logger.info(f"   Total articles scraped: {stats.get('total_articles_scraped', 0)}")
            logger.info(f"   Total saved: {stats.get('total_saved', 0)}")
            logger.info(f"   Total duplicates: {stats.get('total_duplicates', 0)}")
            logger.info(f"   Total filtered: {stats.get('total_numbers_filtered', 0)}")
            logger.info(f"   Total errors: {stats.get('total_errors', 0)}")
            logger.info(f"   Runtime: {stats.get('runtime_seconds', 0):.2f} seconds")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Scraper failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
