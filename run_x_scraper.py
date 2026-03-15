"""
تشغيل سكراب X بسرعة
"""
import asyncio
import sys
sys.path.insert(0, '.')

from scrapers.x_scraper import main

if __name__ == "__main__":
    print("🚀 بدء سكراب X...")
    asyncio.run(main())
