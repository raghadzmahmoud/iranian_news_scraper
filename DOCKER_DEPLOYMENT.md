# Docker Deployment Guide
# دليل الدبلويمنت مع Docker

## 🐳 الدبلويمنت مع Docker

### الخيار 1: تشغيل محلي مع Docker Compose

#### الخطوة 1: تثبيت Docker

```bash
# على Ubuntu/Debian
sudo apt install docker.io docker-compose -y

# على macOS
brew install docker docker-compose

# على Windows
# حمّل Docker Desktop من https://www.docker.com/products/docker-desktop
```

#### الخطوة 2: إعداد متغيرات البيئة

```bash
# نسخ ملف البيئة
cp .env.example .env

# تعديل الملف
nano .env
```

أضف المتغيرات:

```
DB_NAME=iran_news_pipeline
DB_HOST=dpg-d6hl9v7gi27c73ftat10-a.oregon-postgres.render.com
DB_USER=iran_news_pipeline_user
DB_PASSWORD=YalzyXWb1nYt3IQfyumiQa16r0HFrPta
DB_PORT=5432
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=media-automation-bucket
GCS_BUCKET_NAME=your_gcs_bucket
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
TELEGRAM_API_ID=your_id
TELEGRAM_API_HASH=your_hash
TELEGRAM_PHONE=your_phone
```

#### الخطوة 3: بناء وتشغيل الـ Containers

```bash
# بناء الـ images
docker-compose build

# تشغيل الـ containers
docker-compose up -d

# عرض الـ logs
docker-compose logs -f

# إيقاف الـ containers
docker-compose down
```

#### الخطوة 4: اختبر الـ API

```bash
# Health Check
curl http://localhost:8000/health

# Swagger UI
http://localhost:8000/docs
```

---

### الخيار 2: الدبلويمنت على Render مع Docker (Blueprint)

#### الخطوة 1: دفع الكود إلى GitHub

```bash
git add .
git commit -m "Add Docker deployment configuration"
git push origin main
```

#### الخطوة 2: إنشاء Blueprint على Render

1. اذهب إلى [render.com/dashboard](https://render.com/dashboard)
2. اضغط **"New +"** → **"Blueprint"**
3. اختر repository الخاص بك
4. اختر branch (`main`)
5. اضغط **"Deploy"**

#### الخطوة 3: تعيين متغيرات البيئة

1. بعد إنشاء Blueprint، اذهب إلى كل خدمة
2. اضغط **"Environment"**
3. أضف المتغيرات:

```
DB_NAME = iran_news_pipeline
DB_HOST = dpg-d6hl9v7gi27c73ftat10-a.oregon-postgres.render.com
DB_USER = iran_news_pipeline_user
DB_PASSWORD = YalzyXWb1nYt3IQfyumiQa16r0HFrPta
DB_PORT = 5432
AWS_REGION = us-east-1
AWS_ACCESS_KEY_ID = [مفتاحك]
AWS_SECRET_ACCESS_KEY = [السر]
S3_BUCKET_NAME = media-automation-bucket
GCS_BUCKET_NAME = [الـ GCS bucket]
GOOGLE_APPLICATION_CREDENTIALS = [مسار JSON]
TELEGRAM_API_ID = [API ID]
TELEGRAM_API_HASH = [API Hash]
TELEGRAM_PHONE = [الهاتف]
```

#### الخطوة 4: اختبر الدبلويمنت

```bash
# اختبر الـ API
curl https://iran-news-api.onrender.com/health

# شاهد الـ logs
# اذهب إلى الخدمة واضغط "Logs"
```

---

## 📊 هيكل Docker

### Dockerfile
- يبني image واحد يستخدم لكل من API و Worker
- يثبت جميع المتطلبات
- يعيّن المستخدم للأمان

### docker-compose.yml
- يشغل خدمتين:
  - **API**: على المنفذ 8000
  - **Worker**: بدون منفذ (background)
- يستخدم نفس الـ image لكليهما
- يشارك الـ volumes (media, logs)

### render-docker.yaml
- Blueprint لـ Render
- يعرّف خدمتين (Web + Background Worker)
- يستخدم Docker

---

## 🔧 الأوامر المفيدة

### بناء الـ Image

```bash
# بناء image واحد
docker build -t iran-news-api .

# بناء مع tag
docker build -t iran-news-api:latest .
```

### تشغيل الـ Container

```bash
# تشغيل API
docker run -p 8000:8000 --env-file .env iran-news-api

# تشغيل Worker
docker run --env-file .env iran-news-api python worker.py
```

### Docker Compose

```bash
# بناء وتشغيل
docker-compose up -d

# عرض الـ logs
docker-compose logs -f api
docker-compose logs -f worker

# إيقاف
docker-compose down

# حذف الـ volumes
docker-compose down -v
```

### تنظيف Docker

```bash
# حذف الـ images غير المستخدمة
docker image prune

# حذف الـ containers غير المستخدمة
docker container prune

# حذف كل شيء
docker system prune -a
```

---

## 📈 الأداء والموارد

### حدود Docker على Render (Free Plan)
- **Memory**: 512 MB
- **CPU**: مشترك
- **Disk**: 100 GB

### تحسينات الأداء

```dockerfile
# استخدام slim image (أخف)
FROM python:3.11-slim

# تقليل حجم الـ image
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# استخدام multi-stage build
FROM python:3.11-slim as builder
# ... build stage ...

FROM python:3.11-slim
# ... runtime stage ...
```

---

## 🔍 استكشاف الأخطاء

### ❌ خطأ: "Cannot connect to database"

```bash
# اختبر الاتصال من داخل الـ container
docker-compose exec api psql -h dpg-d6hl9v7gi27c73ftat10-a.oregon-postgres.render.com \
    -U iran_news_pipeline_user \
    -d iran_news_pipeline
```

### ❌ خطأ: "Port already in use"

```bash
# ابحث عن الـ container الذي يستخدم المنفذ
docker ps

# اقتل الـ container
docker kill container_id
```

### ❌ خطأ: "Out of memory"

```bash
# قلل استهلاك الذاكرة
# أو ترقية الـ plan على Render
```

### عرض الـ logs

```bash
# الـ API logs
docker-compose logs -f api

# الـ Worker logs
docker-compose logs -f worker

# آخر 100 سطر
docker-compose logs --tail=100 api
```

---

## 🔄 تحديث الكود

### محلياً

```bash
# سحب آخر التحديثات
git pull origin main

# إعادة بناء الـ image
docker-compose build

# إعادة تشغيل الـ containers
docker-compose up -d
```

### على Render

```bash
# دفع الكود إلى GitHub
git push origin main

# Render سيقوم بـ redeploy تلقائياً
```

---

## ✅ Checklist

- [ ] تثبيت Docker
- [ ] إعداد متغيرات البيئة
- [ ] بناء الـ image
- [ ] تشغيل docker-compose
- [ ] اختبار الـ API محلياً
- [ ] دفع الكود إلى GitHub
- [ ] إنشاء Blueprint على Render
- [ ] تعيين متغيرات البيئة على Render
- [ ] اختبار الـ API على Render

---

## 📞 الدعم

- [Docker Documentation](https://docs.docker.com)
- [Docker Compose Documentation](https://docs.docker.com/compose)
- [Render Docker Documentation](https://render.com/docs/docker)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

---

**استمتع بالدبلويمنت مع Docker! 🐳🚀**
