# استخدام صورة Python الرسمية
FROM python:3.11.7-slim

# تعيين مجلد العمل
WORKDIR /app

# تثبيت المتطلبات النظامية
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    ffmpeg \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    libasound2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المتطلبات Python
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install chromium

# نسخ كود التطبيق
COPY . .

# متغيرات البيئة الافتراضية
ENV PYTHONUNBUFFERED=1

# نجهز مجلد ملف جلسة Playwright ونخليه
RUN mkdir -p /app/media/playwright_profile
ENV X_CHROME_PROFILE_DIR=/app/media/playwright_profile

# أمر التشغيل للـ Worker المتوازي
CMD ["python", "worker_parallel_advanced.py"]
