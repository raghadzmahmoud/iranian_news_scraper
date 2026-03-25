# 🚀 Quick Start - تشغيل السحب من X

## الخطوة 1️⃣: التحقق من الإعدادات

```bash
python quick_test.py
```

هذا بيتحقق من:
- ✅ Python packages
- ✅ .env file
- ✅ Database connection
- ✅ X sources في قاعدة البيانات

## الخطوة 2️⃣: التشغيل

### الطريقة الأسهل (One-liner):

**Linux/Mac:**
```bash
chmod +x setup_and_run.sh && ./setup_and_run.sh
```

**Windows:**
```cmd
setup_and_run.bat
```

### الطريقة اليدوية:

```bash
# 1. إنشاء virtual environment
python -m venv venv

# 2. تفعيل virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. تثبيت Playwright
python -m playwright install chromium

# 5. تشغيل السحب
python run_x_scraper_local.py
```

## الخطوة 3️⃣: مراقبة التقدم

ستشوف output مثل:

```
🐦 Playwright-only X scraper (incremental saves)
[1/5] @username1 (ID: 123)
  [username1] Scraping...
  [username1] 15 tweets scraped
  🟢 Batch 1: saved 10 articles (dup 2)
  
[2/5] @username2 (ID: 124)
  [username2] Scraping...
  [username2] 20 tweets scraped
  🟢 Batch 1: saved 15 articles (dup 3)
  
✅ Total saved: 25
⚠️ Total duplicates skipped: 5
🔢 Total number-filtered articles: 3
```

## الخطوة 4️⃣: النتائج

بعد الانتهاء:
- 📊 ملف JSON بالإحصائيات: `x_playwright_stats_YYYYMMDD_HHMMSS.json`
- 💾 المقالات محفوظة في قاعدة البيانات
- 📝 الـ logs في `logs/app.log`

## ⚠️ أول مرة؟

أول مرة تشغيل:
1. قد تحتاج 5-10 دقائق (تحميل Playwright)
2. قد تحتاج تسجيل دخول يدوي إلى X
3. قد تظهر نافذة browser (اتركها تشتغل)

## 🆘 مشاكل شائعة

### ❌ "Timeout 30000ms exceeded"
```bash
# الحل: تأكد من الـ internet connection
# أو جرب مرة أخرى
```

### ❌ "Failed to launch browser"
```bash
# الحل:
python -m playwright install chromium --with-deps
```

### ❌ "Database connection failed"
```bash
# الحل: تأكد من الـ .env file
# وتأكد من الـ database credentials
```

## 📊 الإحصائيات

كل تشغيل بينتج ملف JSON مثل:

```json
{
  "total_sources": 5,
  "total_articles_scraped": 150,
  "total_saved": 45,
  "total_duplicates": 8,
  "total_numbers_filtered": 12,
  "total_errors": 0,
  "runtime_seconds": 125.5,
  "per_source": [
    {
      "source_id": 123,
      "username": "username1",
      "scraped": 30,
      "new": 10,
      "saved": 10,
      "duplicates": 2,
      "errors": 0
    }
  ]
}
```

## 🎯 الخطوات التالية

بعد التشغيل الناجح:

1. **للـ Automated Scheduling**:
   ```bash
   python jobs/scheduler.py
   ```

2. **للـ Render Deployment**:
   - اتبع `RENDER_DEPLOYMENT.md`

3. **للـ Customization**:
   - عدّل الـ settings في `.env`
   - عدّل الـ sources في قاعدة البيانات

## 💡 نصائح

- **للـ GUI**: غيّر `X_PLAYWRIGHT_HEADLESS=false` في `.env`
- **للـ Debugging**: شوف `logs/app.log`
- **للـ Performance**: قلل `X_MAX_TWEETS` أو `X_MAX_SCROLLS`

---

**Ready?** 🚀

```bash
python quick_test.py
```

ثم:

```bash
python run_x_scraper_local.py
```
