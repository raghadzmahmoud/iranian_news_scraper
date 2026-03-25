# تشغيل السحب من X محليًا

## المتطلبات
- Python 3.9+
- Chrome/Chromium browser (Playwright بيحمله تلقائيًا)
- Internet connection

## الخطوات السريعة

### على Linux/Mac:
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### على Windows:
```cmd
setup_and_run.bat
```

أو يدويًا:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python run_x_scraper_local.py
```

## ماذا يحدث؟

1. **التجهيز**:
   - إنشاء virtual environment
   - تثبيت المتطلبات
   - تحميل Playwright browsers

2. **التشغيل**:
   - تسجيل الدخول إلى X (أول مرة فقط)
   - سحب التغريدات من جميع المصادر المفعلة
   - حفظ المقالات في قاعدة البيانات
   - إنشاء ملف إحصائيات JSON

## الـ Output

### الـ Logs:
```
🐦 Playwright-only X scraper (incremental saves)
[1/5] @username1 (ID: 123)
  [username1] Scraping...
  [username1] 15 tweets scraped
  🟢 Batch 1: saved 10 articles (dup 2)
...
✅ Total saved: 45
⚠️ Total duplicates skipped: 8
🔢 Total number-filtered articles: 12
```

### ملف الإحصائيات:
```json
{
  "total_sources": 5,
  "total_articles_scraped": 150,
  "total_saved": 45,
  "total_duplicates": 8,
  "total_numbers_filtered": 12,
  "runtime_seconds": 125.5,
  "per_source": [...]
}
```

## المشاكل الشائعة

### ❌ "Page.wait_for_selector: Timeout"
**السبب**: X لم تحمل أو الـ account محجوب
**الحل**: 
- تأكد من الـ internet connection
- تأكد من صحة الـ credentials في `.env`
- جرب تسجيل الدخول يدويًا على X

### ❌ "Failed to launch browser"
**السبب**: مشكلة في تثبيت Playwright
**الحل**:
```bash
python -m playwright install chromium --with-deps
```

### ❌ "AuthChallengeError"
**السبب**: X طلبت verification
**الحل**:
- احذف مجلد `media/playwright_profile`
- شغّل الـ script مرة أخرى
- أكمل الـ verification يدويًا

### ❌ "No tweets found"
**السبب**: الـ account private أو معلق
**الحل**:
- تأكد من أن الـ accounts في قاعدة البيانات مفعلة
- تأكد من أن الـ accounts عامة (public)

## الـ Configuration

تعديل الـ settings في `.env`:

```env
# عدد الـ tweets المسحوبة من كل account
X_MAX_TWEETS=30

# عدد مرات الـ scroll
X_MAX_SCROLLS=10

# الـ headless mode (true = بدون واجهة)
X_PLAYWRIGHT_HEADLESS=true

# مجلد حفظ الـ Chrome profile
X_CHROME_PROFILE_DIR=media/playwright_profile
```

## نصائح

1. **أول مرة**: قد تحتاج 5-10 دقائق (تحميل Playwright)
2. **الـ Rate Limiting**: إذا حصلت مشاكل، زيادة الـ delays في الـ code
3. **الـ Database**: تأكد من الـ connection قبل التشغيل
4. **الـ Logs**: شوف `logs/app.log` للـ details

## الـ Headless Mode

### للـ GUI (شوف الـ browser):
```env
X_PLAYWRIGHT_HEADLESS=false
```

### للـ Headless (بدون GUI):
```env
X_PLAYWRIGHT_HEADLESS=true
```

## الـ Debugging

### لـ verbose logging:
```python
# في run_x_scraper_local.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### لـ screenshot على error:
```python
# في scrapers/x_playwright.py
await page.screenshot(path="error_screenshot.png")
```

## الـ Performance

- **الـ Runtime**: عادة 2-5 دقائق (حسب عدد الـ sources)
- **الـ Memory**: ~500MB-1GB
- **الـ CPU**: 20-40%

## الـ Next Steps

بعد التشغيل الناجح:
1. شوف الـ stats في الـ JSON file
2. تحقق من المقالات في قاعدة البيانات
3. عدّل الـ settings حسب احتياجاتك
4. استخدم `jobs/scheduler.py` للـ automated scheduling
