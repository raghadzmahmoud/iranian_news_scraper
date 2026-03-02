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

# تعريض المنفذ
EXPOSE 8000

# متغيرات البيئة الافتراضية
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# أمر التشغيل
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
