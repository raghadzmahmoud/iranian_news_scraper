# قائمة التحقق للنشر - X Scraper Integration

## ✅ التحقق قبل التشغيل

### 1. المتطلبات الأساسية

#### Python Packages
- [x] `twikit` موجود في `requirements.txt`
- [x] `apscheduler` موجود في `requirements.txt`
- [x] جميع المكتبات الأخرى موجودة

#### ملفات الإعدادات
- [ ] `.env` محدّث بالكوكيز الصحيحة
- [x] `.env.example` يحتوي على أمثلة
- [x] `.gitignore` يحتوي على ملفات X

### 2. الكوكيز (مهم جداً!)

افتح `.env` وتأكد من:
```env
X_AUTH_TOKEN=ضع_الكوكيز_الحقيقية_هنا
X_CT0_TOKEN=ضع_الكوكيز_الحقيقية_هنا
X_MAX_TWEETS_PER_ACCOUNT=20
X_DELAY_BETWEEN_ACCOUNTS=3
X_DEBUG=True
```

⚠️ **لا تنشر بدون كوكيز صحيحة!**

### 3. قاعدة البيانات

تأكد من وجود المصادر:
```sql
SELECT COUNT(*) FROM sources WHERE source_type_id = 7 AND is_active = true;
```

يجب أن يكون العدد > 0

### 4. الملفات المطلوبة

- [x] `scrapers/x_scraper.py`
- [x] `jobs/x_scraper_job.py`
- [x] `worker_parallel_advanced.py`
- [x] `storage/article_processor.py` (محدّث)
- [x] `config/settings.py` (محدّث)

## 🚀 التشغيل

### الطريقة 1: تشغيل محلي

```bash
# 1. تحديث الكوكيز في .env
nano .env

# 2. اختبار
python test_x_scraper.py
# اختر: 1 (اختبار تحميل المصادر)

# 3. تشغيل Worker
python worker_parallel_advanced.py
```

### الطريقة 2: Docker

```bash
# 1. بناء الصورة
docker build -t iranian-news-scraper .

# 2. تشغيل مع متغيرات البيئة
docker run -d \
  --name news-worker \
  --env-file .env \
  iranian-news-scraper
```

### الطريقة 3: Docker Compose

إذا كان عندك `docker-compose.yml`:
```bash
docker-compose up -d
```

## 📊 المراقبة

### السجلات (Logs)

```bash
# محلي
tail -f logs/app.log

# Docker
docker logs -f news-worker
```

### ما تتوقع تشوفه:

```
🚀 بدء الوركر المتوازي المتقدم
   عدد الوركرز: 3
   السحب RSS: كل 5 دقايق
   السحب X: كل 10 دقايق
   الترجمة: كل 10 دقايق
================================================================================
📅 تم جدولة السحب RSS: كل 5 دقايق (تشغيل فوري)
📅 تم جدولة السحب X: كل 10 دقايق (تشغيل فوري)
📅 تم جدولة الترجمة: كل 10 دقايق (تشغيل فوري)
✅ الوركر المتوازي يعمل الآن
```

بعد 10 دقايق:
```
🐦 [السحب X #1] بدء السحب من X في 2026-03-15 21:30:00
✅ [السحب X #1] انتهى: 450 تغريدة، 320 محفوظة، 50 مفلترة، 120 مع أرقام
```

## 🐛 استكشاف الأخطاء

### خطأ: "🔐 خطأ مصادقة"
**السبب:** الكوكيز غير صحيحة أو انتهت
**الحل:** حدّث الكوكيز في `.env`

### خطأ: "❌ twikit غير مثبت"
**السبب:** المكتبة غير مثبتة
**الحل:** 
```bash
pip install twikit
# أو
pip install -r requirements.txt
```

### خطأ: "لا توجد مصادر X"
**السبب:** لا توجد مصادر بـ source_type_id = 7
**الحل:** أضف مصادر في قاعدة البيانات

### خطأ: "ModuleNotFoundError: No module named 'jobs.x_scraper_job'"
**السبب:** الملف غير موجود
**الحل:** تأكد من وجود `jobs/x_scraper_job.py`

## 🔧 Dockerfile

الـ Dockerfile الحالي كويس ولا يحتاج تعديلات:

```dockerfile
FROM python:3.11.7-slim

WORKDIR /app

# تثبيت المتطلبات النظامية
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# تثبيت المتطلبات Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كود التطبيق
COPY . .

ENV PYTHONUNBUFFERED=1

# تشغيل Worker
CMD ["python", "worker_parallel_advanced.py"]
```

✅ **لا تعديلات مطلوبة على Dockerfile**

## 📋 متغيرات البيئة المطلوبة

### للـ Database:
```env
DB_NAME=war_news_intelligence
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_PORT=5432
```

### للـ X Scraper:
```env
X_AUTH_TOKEN=your_auth_token
X_CT0_TOKEN=your_ct0_token
X_MAX_TWEETS_PER_ACCOUNT=20
X_DELAY_BETWEEN_ACCOUNTS=3
X_DEBUG=True
```

### للـ Translation (إذا كان موجود):
```env
war_news_translation_api_key=your_api_key
open_ai_model=gpt-4o-mini
```

## 🔒 الأمان

### ملفات لا تُرفع إلى Git:
- `.env` - الإعدادات الحقيقية
- `x_cookies.json` - ملف الكوكيز
- `x_scraper_stats_*.json` - الإحصائيات
- `tweets_output.json` - التغريدات

### ملفات آمنة للمشاركة:
- `.env.example` - أمثلة الإعدادات
- `Dockerfile` - ملف Docker
- `requirements.txt` - المكتبات
- جميع ملفات الكود

## ✅ قائمة التحقق النهائية

قبل النشر، تأكد من:

- [ ] الكوكيز محدّثة في `.env`
- [ ] `twikit` موجود في `requirements.txt`
- [ ] المصادر موجودة في قاعدة البيانات (source_type_id = 7)
- [ ] الاتصال بقاعدة البيانات يعمل
- [ ] اختبار السحب نجح (`python test_x_scraper.py`)
- [ ] السجلات تظهر بشكل صحيح
- [ ] `.gitignore` يحتوي على ملفات X

## 🎯 الخلاصة

### نعم، worker_parallel_advanced جاهز للتشغيل! ✅

```bash
python worker_parallel_advanced.py
```

سيعمل:
- RSS Scraper كل 5 دقايق
- X Scraper كل 10 دقايق
- Translation كل 10 دقايق

### لا، Dockerfile لا يحتاج تعديلات! ✅

الـ Dockerfile الحالي يحتوي على كل شي:
- Python 3.11
- gcc (للمكتبات)
- postgresql-client
- ffmpeg
- جميع المكتبات من requirements.txt (بما فيها twikit)

## 📞 الدعم

إذا واجهت مشاكل:
1. تحقق من السجلات
2. تأكد من الكوكيز
3. تحقق من الاتصال بقاعدة البيانات
4. راجع ملفات التوثيق

---

**ملاحظة مهمة:** لا تنسى تحديث الكوكيز في `.env` قبل التشغيل!
