#!/bin/bash

# Build script for Render deployment
# سكريبت البناء لـ Render

set -e

echo "🔨 جاري بناء التطبيق..."

# تحديث pip
pip install --upgrade pip

# تثبيت المتطلبات
echo "📦 جاري تثبيت المتطلبات..."
pip install -r requirements.txt

# إنشاء مجلدات ضرورية
echo "📁 جاري إنشاء المجلدات..."
mkdir -p media
mkdir -p logs

# تشغيل migrations إذا لزم الأمر
echo "🗄️ جاري إعداد قاعدة البيانات..."
python setup_database.py || true

echo "✅ تم البناء بنجاح!"
