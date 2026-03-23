# نظام ضمان تفرد الـ URLs

## نظرة عامة
هذا النظام يضمن أن كل خبر يُخزّن مرة واحدة فقط في قاعدة البيانات، حيث يكون الـ URL فريداً (Unique).

## المكونات الرئيسية

### 1. قاعدة البيانات (Database Constraint)
- جدول `raw_news` يحتوي على constraint `UNIQUE` على عمود `url`
- هذا يضمن أن لا يمكن إدراج نفس الـ URL مرتين

### 2. معالجة الأخطاء (Error Handling)
عند محاولة إدراج خبر بـ URL موجود بالفعل:

#### في `database/connection.py`:
```python
def insert_raw_data(self, source_id: int, article_data: dict):
    # يرجع:
    # - معرّف المقالة (int) إذا تم الإدراج بنجاح
    # - None إذا كانت المقالة موجودة (Duplicate URL)
    # - False إذا حدث خطأ آخر
```

#### في `storage/news_storage.py`:
```python
def save_article(source_id: int, article_data: dict):
    # يرجع:
    # - معرّف المقالة (int) إذا تم الحفظ بنجاح
    # - None إذا كانت المقالة موجودة (Duplicate URL)
    # - False إذا حدث خطأ في قاعدة البيانات
```

### 3. معالج الأخطاء الموحد (Unified Error Handler)
ملف `utils/article_error_handler.py` يوفر:

```python
from utils.article_error_handler import ArticleErrorHandler, ArticleSaveStatus

# معالجة نتيجة حفظ مقالة واحدة
result = NewsStorage.save_article(source_id, article_data)
status = ArticleErrorHandler.handle_save_result(result, article_url)

if status == ArticleSaveStatus.SUCCESS:
    print("✅ تم الحفظ بنجاح")
elif status == ArticleSaveStatus.DUPLICATE:
    print("⏭️  المقالة موجودة بالفعل")
elif status == ArticleSaveStatus.ERROR:
    print("❌ حدث خطأ في قاعدة البيانات")

# معالجة نتائج حفظ مجموعة من المقالات
results = NewsStorage.save_articles_batch(source_id, articles)
# النتيجة: {'saved': 5, 'duplicates': 2, 'errors': 1}
message = ArticleErrorHandler.handle_batch_results(results)
```

## أمثلة الاستخدام

### مثال 1: حفظ مقالة واحدة
```python
from storage.news_storage import NewsStorage
from utils.article_error_handler import ArticleErrorHandler, ArticleSaveStatus

article_data = {
    'title': 'عنوان الخبر',
    'url': 'https://example.com/news/123',
    'content': 'محتوى الخبر',
    'language': 'ar',
    'published_at': '2024-03-23'
}

result = NewsStorage.save_article(source_id=1, article_data=article_data)
status = ArticleErrorHandler.handle_save_result(result, article_data['url'])

if status == ArticleSaveStatus.SUCCESS:
    print(f"✅ تم حفظ المقالة برقم: {result}")
elif status == ArticleSaveStatus.DUPLICATE:
    print("⏭️  المقالة موجودة بالفعل - سيتم تخطيها")
elif status == ArticleSaveStatus.ERROR:
    print("❌ حدث خطأ - يمكن إعادة المحاولة لاحقاً")
```

### مثال 2: حفظ مجموعة من المقالات
```python
from storage.news_storage import NewsStorage
from utils.article_error_handler import ArticleErrorHandler

articles = [article1, article2, article3, ...]

results = NewsStorage.save_articles_batch(source_id=1, articles=articles)
# النتيجة: {'saved': 5, 'duplicates': 2, 'errors': 0}

message = ArticleErrorHandler.handle_batch_results(results)
print(message)
```

### مثال 3: في سكريبت الـ Scraper
```python
from scrapers.x_scraper import XScraper
from storage.news_storage import NewsStorage
from utils.article_error_handler import ArticleErrorHandler

scraper = XScraper()
articles = scraper.scrape()

results = NewsStorage.save_articles_batch(source_id=1, articles=articles)

# معالجة النتائج
if results['errors'] > 0:
    logger.warning(f"⚠️  حدثت {results['errors']} أخطاء أثناء الحفظ")

if results['duplicates'] > 0:
    logger.info(f"⏭️  تم تخطي {results['duplicates']} مقالة مكررة")

logger.info(f"✅ تم حفظ {results['saved']} مقالة جديدة")
```

## حالات الاستخدام

### ✅ النجاح
- الخبر جديد وتم حفظه بنجاح
- يتم إرجاع معرّف المقالة

### ⏭️ المقالة موجودة (Duplicate)
- الخبر موجود بالفعل في قاعدة البيانات
- يتم تخطيه بدون رسالة خطأ
- يتم إرجاع `None`

### ❌ خطأ في قاعدة البيانات
- مشكلة في الاتصال أو البيانات
- يتم تسجيل الخطأ
- يتم إرجاع `False`

## الفوائد

1. **منع التكرار**: لا يمكن حفظ نفس الخبر مرتين
2. **معالجة أخطاء واضحة**: يمكن التمييز بين الحالات المختلفة
3. **سهولة التتبع**: تسجيل واضح لكل عملية
4. **قابلية إعادة المحاولة**: يمكن معرفة أي الأخطاء يمكن إعادة محاولتها

## ملاحظات مهمة

- تأكد من أن جدول `raw_news` يحتوي على constraint `UNIQUE` على عمود `url`
- الـ URL يجب أن يكون دقيقاً (بما فيه المعاملات والـ fragments)
- في حالة الحاجة لتنظيف الـ URLs، استخدم دالة `url_exists` في `NewsStorage`
