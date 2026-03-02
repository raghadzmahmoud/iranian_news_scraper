# Docker Quick Start
# البدء السريع مع Docker

## 🚀 3 خطوات فقط!

### 1️⃣ إعداد البيئة

```bash
# نسخ ملف البيئة
cp .env.example .env

# تعديل الملف بمتغيراتك
nano .env
```

أضف هذه المتغيرات:

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
```

### 2️⃣ بناء وتشغيل

```bash
# بناء الـ images
docker-compose build

# تشغيل الـ containers
docker-compose up -d
```

### 3️⃣ اختبر الـ API

```bash
# Health Check
curl http://localhost:8000/health

# Swagger UI
http://localhost:8000/docs
```

**تمام! الـ API والـ Worker يعملان الآن! ✅**

---

## 📊 الخدمات

### API Service
- **URL**: `http://localhost:8000`
- **Swagger**: `http://localhost:8000/docs`
- **Health**: `http://localhost:8000/health`

### Worker Service
- يعمل في الخلفية
- يقوم بـ Scraping والمعالجة

---

## 🔧 الأوامر المفيدة

```bash
# عرض الـ logs
docker-compose logs -f

# إيقاف الـ containers
docker-compose down

# إعادة تشغيل
docker-compose restart

# حذف كل شيء
docker-compose down -v
```

---

## 🌐 الدبلويمنت على Render

### الخطوة 1: دفع الكود

```bash
git add .
git commit -m "Add Docker deployment"
git push origin main
```

### الخطوة 2: إنشاء Blueprint

1. اذهب إلى render.com
2. اضغط "New +" → "Blueprint"
3. اختر repository
4. اضغط "Deploy"

### الخطوة 3: أضف المتغيرات

في كل خدمة، أضف متغيرات البيئة (نفس الـ .env)

### الخطوة 4: اختبر

```bash
curl https://iran-news-api.onrender.com/health
```

---

## 📚 للمزيد من المعلومات

اقرأ `DOCKER_DEPLOYMENT.md` للتفاصيل الكاملة

---

**استمتع! 🐳🚀**
