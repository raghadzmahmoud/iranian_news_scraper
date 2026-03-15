# X (Twitter) Scraper - دليل شامل

## ✅ الإجابة السريعة

### هل worker_parallel_advanced جاهز للتشغيل؟
**نعم! ✅** فقط حدّث الكوكيز في `.env` وشغّل:
```bash
python worker_parallel_advanced.py
```

### هل Dockerfile يحتاج تعديلات؟
**لا! ✅** الـ Dockerfile جاهز ولا يحتاج أي تعديلات.

---

## 📚 الملفات المنشأة

### الكود الرئيسي
1. `scrapers/x_scraper.py` - السكراب الرئيسي
2. `jobs/x_scraper_job.py` - وظيفة الجدولة
3. `storage/article_processor.py` - محدّث (إزالة warning للتغريدات + تنظيف النصوص)
4. `config/settings.py` - محدّث (قراءة من .env)
5. `worker_parallel_advanced.py` - محدّث (دمج X scraper)

### ملفات التشغيل والاختبار
6. `run_x_scraper.py` - تشغيل مرة واحدة
7. `run_x_scheduler.py` - تشغيل مجدول
8. `test_x_scraper.py` - اختبار
9. `test_tweet_cleaning.py` - اختبار التنظيف
10. `test_x_filtering.py` - اختبار الفلترة

### التوثيق (13 ملف)
11. `X_SCRAPER_GUIDE.md` - دليل مفصل
12. `X_SCRAPER_QUICKSTART.md` - دليل البدء السريع
13. `X_SCRAPER_SUMMARY.md` - ملخص شامل
14. `X_SCRAPER_ENV_UPDATE.md` - تحديثات .env
15. `X_SCRAPER_WORD_COUNT_FIX.md` - إصلاح عدد الكلمات
16. `X_SCRAPER_TEXT_CLEANING.md` - تنظيف النصوص
17. `X_SCRAPER_FINAL_SUMMARY.md` - ملخص نهائي
18. `WORKER_X_INTEGRATION.md` - دمج في Worker
19. `DEPLOYMENT_CHECKLIST.md` - قائمة التحقق للنشر
20. `تعليمات_سكراب_X.md` - تعليمات بالعربي
21. `README_X_SCRAPER.md` - هذا الملف

### التعديلات على الملفات الموجودة
22. `.env` - إضافة إعدادات X
23. `.env.example` - إضافة أمثلة
24. `.gitignore` - إضافة ملفات X
25. `x_twitter_scraper.py` - شيل اليوزرنيم والباسورد

---

## 🚀 التشغيل السريع

### 1. تحديث الكوكيز
```bash
# افتح .env
nano .env

# حدّث هذه السطور:
X_AUTH_TOKEN=ضع_الكوكيز_الحقيقية_هنا
X_CT0_TOKEN=ضع_الكوكيز_الحقيقية_هنا
```

### 2. اختبار
```bash
python test_x_scraper.py
# اختر: 1 (اختبار تحميل المصادر)
```

### 3. تشغيل
```bash
python worker_parallel_advanced.py
```

---

## 🎯 المميزات

### 1. قراءة من قاعدة البيانات
- يقرأ تلقائياً جميع المصادر التي `source_type_id = 7`
- 32 مصدر X جاهز

### 2. سحب التغريدات
- آخر 20 تغريدة من كل حساب
- يعمل بالتوازي مع RSS والترجمة

### 3. تنظيف النصوص
- إزالة الروابط (`https://t.co/...`)
- إزالة الهاشتاغات من النهاية (`#عاجل #أخبار`)
- الهاشتاغات في الوسط تبقى (`#ظفار`)

### 4. الفلترة الذكية
- فلترة بالكلمات المفتاحية
- كشف اللغة (عربي، عبري، إنجليزي)
- كشف الأرقام
- منع التكرار (URL)

### 5. التخزين
- يخزن في `raw_news` مثل RSS
- `content_original`: النص المنظف
- `url`: رابط التغريدة
- `has_numbers`: كشف الأرقام
- `processing_status`: 1 للعربي، 0 للأجنبي

### 6. التوازي
- 3 workers (RSS + X + Translation)
- RSS: كل 5 دقايق
- X: كل 10 دقايق
- Translation: كل 10 دقايق

---

## 📊 الجدولة

```
21:30:00 - RSS Scraper يبدأ (Thread 1)
21:30:00 - X Scraper يبدأ (Thread 2)
21:30:00 - Translation يبدأ (Thread 3)
21:35:00 - RSS Scraper يبدأ مرة أخرى
21:40:00 - X Scraper يبدأ مرة أخرى
21:40:00 - Translation يبدأ مرة أخرى
```

---

## 🐳 Docker

### لا تعديلات مطلوبة! ✅

الـ Dockerfile الحالي يحتوي على كل شي:
```dockerfile
FROM python:3.11.7-slim
WORKDIR /app

# تثبيت المتطلبات
RUN apt-get update && apt-get install -y gcc postgresql-client ffmpeg

# تثبيت Python packages (بما فيها twikit)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# تشغيل Worker
CMD ["python", "worker_parallel_advanced.py"]
```

### التشغيل
```bash
# بناء
docker build -t iranian-news-scraper .

# تشغيل
docker run -d --name news-worker --env-file .env iranian-news-scraper

# السجلات
docker logs -f news-worker
```

---

## 🔒 الأمان

### ملفات في .gitignore:
- `.env` - الإعدادات الحقيقية
- `x_cookies.json` - ملف الكوكيز
- `x_scraper_stats_*.json` - الإحصائيات
- `tweets_output.json` - التغريدات

### ملفات آمنة:
- `.env.example` - أمثلة
- جميع ملفات الكود
- Dockerfile

---

## 📈 مثال على النتائج

```
🐦 [السحب X #1] بدء السحب من X في 2026-03-15 21:30:00
   📡 @wamnews (ID: 20)
   👤 وكالة أنباء الإمارات (@wamnews) — 927,196 متابع
   [Search] وجدت 20 تغريدة
   ✅ نجح — 20 تغريدة
   
🔍 بدء معالجة 20 مقالة من المصدر 20
   🌐 اللغة المكتشفة: ar (ar:196, he:0, en:36)
   ✅ المقالة تمر الفلترة
   الكلمات: 45
   اللغة: ar
   أرقام: نعم
   المصدر: X (Twitter)
   ✅ تم حفظ المقالة برقم: 6789

✅ [السحب X #1] انتهى: 450 تغريدة، 320 محفوظة، 50 مفلترة، 120 مع أرقام
```

---

## 🐛 استكشاف الأخطاء

### "🔐 خطأ مصادقة"
**الحل:** حدّث الكوكيز في `.env`

### "❌ twikit غير مثبت"
**الحل:** `pip install twikit`

### "لا توجد مصادر X"
**الحل:** أضف مصادر في قاعدة البيانات

---

## 📚 التوثيق الكامل

- `X_SCRAPER_GUIDE.md` - دليل مفصل
- `X_SCRAPER_QUICKSTART.md` - دليل البدء السريع
- `DEPLOYMENT_CHECKLIST.md` - قائمة التحقق للنشر
- `WORKER_X_INTEGRATION.md` - دمج في Worker
- `تعليمات_سكراب_X.md` - تعليمات بالعربي

---

## ✅ الخلاصة

### نعم، كل شي جاهز! 🎉

1. **worker_parallel_advanced** جاهز للتشغيل ✅
2. **Dockerfile** لا يحتاج تعديلات ✅
3. **الفلترة** شغالة ✅
4. **كشف الأرقام** شغال ✅
5. **تنظيف النصوص** شغال ✅
6. **التخزين** في raw_news ✅
7. **التوازي** مع RSS والترجمة ✅

### فقط حدّث الكوكيز وشغّل:

```bash
# 1. حدّث الكوكيز في .env
nano .env

# 2. شغّل Worker
python worker_parallel_advanced.py
```

**كل شي شغال! 🚀**
