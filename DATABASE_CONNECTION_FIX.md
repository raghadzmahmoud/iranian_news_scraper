# إصلاح مشكلة "connection already closed"

## المشكلة
كانت المشكلة أن الاتصال بقاعدة البيانات يُغلق تلقائياً بعد فترة من عدم الاستخدام، والكود كان يتحقق فقط من `if not db.conn` لكن لا يتحقق إذا كان الاتصال مغلق فعلياً.

## الحل
تم إضافة دالة `ensure_connection()` في ملف `database/connection.py` التي:
1. تتحقق من وجود الاتصال
2. تتحقق من أن الاتصال ليس مغلق (`conn.closed`)
3. تختبر صحة الاتصال بتنفيذ استعلام بسيط (`SELECT 1`)
4. تعيد الاتصال تلقائياً إذا كان الاتصال مغلق أو غير صالح

## الملفات المعدلة

### 1. database/connection.py
- ✅ إضافة دالة `ensure_connection()`
- ✅ تحديث جميع الدوال لاستخدام `ensure_connection()` بدلاً من التحقق اليدوي

### 2. scrapers/db_rss_scraper.py
- ✅ استبدال `if not db.conn: db.connect()` بـ `db.ensure_connection()`
- ✅ في الدوال: `load_rss_sources_from_db()`, `load_source_by_id()`, `get_source_type_id_from_db()`

### 3. jobs/translation_job.py
- ✅ استخدام `db.ensure_connection()` بدلاً من `if not db.conn`
- ✅ إنشاء cursor جديد لكل استعلام وإغلاقه بعد الاستخدام

### 4. services/translation/translator.py
- ✅ استخدام الاتصال المشترك `from database.connection import db`
- ✅ استخدام `db.ensure_connection()`
- ✅ إنشاء cursor جديد لكل استعلام وإغلاقه بعد الاستخدام

### 5. storage/news_storage.py
- ✅ استبدال 7 تطابقات من `if not db.conn` إلى `db.ensure_connection()`

### 6. storage/news_reader.py
- ✅ استبدال 6 تطابقات

### 7. storage/article_processor.py
- ✅ استبدال 1 تطابق

### 8. scrapers/x_scraper.py
- ✅ استبدال 2 تطابقات

### 9. scrapers/x_playwright.py
- ✅ استبدال 1 تطابق

### 10. jobs/x_scraper_job.py
- ✅ استبدال 1 تطابق

### 11. apply_numbers_detection.py
- ✅ استبدال 4 تطابقات

### 12. worker_parallel.py
- ✅ إضافة طباعة المصادر قبل السحب
- ✅ استيراد `load_rss_sources_from_db`

## النتيجة
الآن عند تشغيل الـ workers:
- ✅ لن تحدث مشكلة "connection already closed"
- ✅ لن تحدث مشكلة "cursor already closed"
- ✅ سيتم إعادة الاتصال تلقائياً عند الحاجة
- ✅ سيتم طباعة جميع المصادر قبل كل عملية سحب

## الاستخدام
```bash
# تشغيل الوركر البسيط
python worker_parallel.py

# تشغيل الوركر المتقدم
python worker_parallel_advanced.py
```
