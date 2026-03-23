#!/usr/bin/env python
"""
تشغيل سحب X من أي مجلد
"""
import sys
import os
import asyncio

# أضف المجلد الجذر إلى المسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.x_scraper import main

if __name__ == "__main__":
    asyncio.run(main())
