# Multi-stage Dockerfile for Iran News Pipeline
# استخدام Python 3.11 slim image
FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# تعيين مجلد العمل
WORKDIR /app

# تثبيت المتطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المتطلبات Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# نسخ الكود
COPY . .

# إنشاء مجلدات ضرورية
RUN mkdir -p media logs

# تعيين المستخدم (للأمان)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# تعريض المنفذ
EXPOSE 8000

# الأمر الافتراضي (سيتم تجاوزه في docker-compose)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
