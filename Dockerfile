# استخدام صورة Python الرسمية
FROM python:3.11.7-slim

# تعيين مجلد العمل
WORKDIR /app

# تثبيت المتطلبات النظامية (محسّنة للـ Render)
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    libxkbcommon0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المتطلبات Python
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت Playwright مع الـ dependencies
RUN python -m playwright install chromium
RUN python -m playwright install-deps chromium

# نسخ كود التطبيق
COPY . .

# متغيرات البيئة الافتراضية
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# استخدم /tmp للـ Chrome profile (Render يحذفها بين الـ deploys)
ENV X_CHROME_PROFILE_DIR=/tmp/playwright_profile

# أمر التشغيل للـ Worker المتوازي
CMD ["python", "worker_parallel_improved.py"]
