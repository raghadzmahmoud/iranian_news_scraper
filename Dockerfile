# استخدام صورة Python الرسمية
FROM python:3.11.7-slim

# تعيين مجلد العمل
WORKDIR /app

# تثبيت المتطلبات النظامية
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المتطلبات Python
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كود التطبيق
COPY . .

# متغيرات البيئة الافتراضية
ENV PYTHONUNBUFFERED=1

# أمر التشغيل للـ Worker المتوازي
CMD ["python", "worker_parallel_advanced.py"]
