#!/bin/bash

# Start script for Worker service on Render
# سكريبت تشغيل خدمة Worker على Render

set -e

echo "🚀 جاري بدء خدمة Worker..."

# تشغيل الـ Worker الرئيسي
# يقوم بتشغيل جميع الـ Workers (Scraper, Audio, Video) بـ Multi-Threading
exec python worker.py
