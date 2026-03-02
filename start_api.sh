#!/bin/bash

# Start script for API service on Render
# سكريبت تشغيل خدمة API على Render

set -e

echo "🚀 جاري بدء خدمة API..."

# الحصول على المتغيرات من البيئة
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

echo "📡 تشغيل API على $HOST:$PORT"

# تشغيل التطبيق
exec uvicorn app:app \
    --host $HOST \
    --port $PORT \
    --workers 4 \
    --loop uvloop \
    --log-level info
