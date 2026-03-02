# Render Setup Instructions
# تعليمات إعداد Render



## 🚀 خطوات الدبلويمنت

### الخطوة 1: دفع الكود إلى GitHub

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### الخطوة 2: إنشاء API Service

1. اذهب إلى [render.com/dashboard](https://render.com/dashboard)
2. اضغط **"New +"** → **"Web Service"**
3. اختر repository الخاص بك
4. ملء البيانات:
   - **Name**: `iran-news-api`
   - **Environment**: `Python 3`
   - **Build Command**: `bash build.sh`
   - **Start Command**: `bash start_api.sh`
   - **Plan**: `Free`
5. اضغط **"Create Web Service"**

### الخطوة 3: إضافة متغيرات البيئة للـ API

1. اذهب إلى الخدمة `iran-news-api`
2. اضغط **"Environment"** من القائمة الجانبية
3. أضف المتغيرات التالية:

```

```

#### AWS S3 Variables
```
AWS_REGION = us-east-1
AWS_ACCESS_KEY_ID = [أدخل مفتاحك]
AWS_SECRET_ACCESS_KEY = [أدخل السر]
S3_BUCKET_NAME = [اسم الـ bucket]
```

#### Google Cloud Variables
```
GCS_BUCKET_NAME = [اسم الـ GCS bucket]
GOOGLE_APPLICATION_CREDENTIALS = [مسار الـ JSON]
```

#### Telegram Variables
```
TELEGRAM_API_ID = [أدخل API ID]
TELEGRAM_API_HASH = [أدخل API Hash]
TELEGRAM_PHONE = [رقم الهاتف]
```

### الخطوة 4: إنشاء Worker Service

1. اضغط **"New +"** → **"Background Worker"**
2. اختر repository الخاص بك
3. ملء البيانات:
   - **Name**: `iran-news-worker`
   - **Environment**: `Python 3`
   - **Build Command**: `bash build.sh`
   - **Start Command**: `bash start_worker.sh`
   - **Plan**: `Free`
4. اضغط **"Create Background Worker"**

### الخطوة 5: إضافة متغيرات البيئة للـ Worker

نفس المتغيرات من الخطوة 3 (Database, AWS, Google Cloud, Telegram)

---

## ✅ التحقق من الدبلويمنت

### اختبر الـ API

```bash
# اختبر الـ Health Check
curl https://iran-news-api.onrender.com/health

# يجب أن ترجع:
# {"status": "healthy", "message": "التطبيق يعمل بشكل صحيح"}
```

### اختبر الـ Worker

1. اذهب إلى `iran-news-worker` على Render
2. اضغط **"Logs"**
3. يجب أن ترى رسائل مثل:
   - `🚀 جاري بدء Main Worker...`
   - `✅ تم بدء Scraper Worker`
   - `✅ تم بدء Audio Worker`
   - `✅ تم بدء Video Worker`

---

## 🔍 استكشاف الأخطاء

### ❌ خطأ: "Cannot connect to database"

**الحل**:
1. تحقق من متغيرات البيانات:
   - `DB_HOST` صحيح
   - `DB_USER` صحيح
   - `DB_PASSWORD` صحيح
2. اختبر الاتصال محلياً:
   ```bash
   psql -h dpg-d6hl9v7gi27c73ftat10-a.oregon-postgres.render.com \
        -U iran_news_pipeline_user \
        -d iran_news_pipeline
   ```

### ❌ خطأ: "Worker not running"

**الحل**:
1. اذهب إلى `iran-news-worker`
2. اضغط **"Manual Deploy"**
3. شاهد الـ logs للأخطاء

### ❌ خطأ: "API timeout"

**الحل**:
- الخدمات المجانية قد تكون بطيئة
- انتظر 15 دقيقة وحاول مرة أخرى
- أو ترقية إلى Paid Plan

---

## 📊 مراقبة الخدمات

### عرض الـ Logs

#### للـ API:
1. اذهب إلى `iran-news-api`
2. اضغط **"Logs"**
3. شاهد الـ logs في الوقت الفعلي

#### للـ Worker:
1. اذهب إلى `iran-news-worker`
2. اضغط **"Logs"**
3. شاهد الـ logs في الوقت الفعلي

### الـ Health Check

```bash
# اختبر الـ API
curl https://iran-news-api.onrender.com/health

# اختبر الـ Swagger UI
https://iran-news-api.onrender.com/docs
```

---

## 🔄 تحديث الدبلويمنت

### تحديث الكود

```bash
# قم بالتغييرات المطلوبة
git add .
git commit -m "Update code"
git push origin main
```

Render سيقوم بـ redeploy تلقائياً!

### إعادة تشغيل يدوية

1. اذهب إلى الخدمة
2. اضغط **"Manual Deploy"**
3. اختر **"Deploy latest commit"**

---

## 📈 الأداء والموارد

### Free Plan
- **Web Service**: 750 ساعة/شهر
- **Background Worker**: 750 ساعة/شهر
- **Memory**: 512 MB
- **CPU**: مشترك

### Paid Plans
| الخطة | السعر | الموارد |
|------|------|--------|
| Starter | $7/شهر | 512 MB RAM |
| Standard | $25/شهر | 2 GB RAM |
| Pro | $100/شهر | 8 GB RAM |

---

## 🎯 الخطوات التالية

1. ✅ دفع الكود إلى GitHub
2. ✅ إنشاء API Service
3. ✅ إضافة متغيرات البيئة للـ API
4. ✅ إنشاء Worker Service
5. ✅ إضافة متغيرات البيئة للـ Worker
6. ✅ اختبار الـ API
7. ✅ مراقبة الـ logs

---

## 📞 الدعم

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [PostgreSQL Documentation](https://www.postgresql.org/docs)

---

**استمتع بالدبلويمنت! 🚀**
