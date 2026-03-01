# Iran News Pipeline 📰

نظام متكامل لسحب الأخبار من مصادر RSS وتخزينها في قاعدة بيانات PostgreSQL.

## البنية المعمارية

```
iran_news_pipeline/
├── config/              # الإعدادات والمتغيرات
├── database/            # اتصال قاعدة البيانات والـ schema
├── models/              # نماذج البيانات
├── scrapers/            # وحدات السحب (RSS + المقالات الكاملة)
├── storage/             # وحدات التخزين (قاعدة البيانات)
├── utils/               # أدوات مساعدة (logging)
└── main.py              # البرنامج الرئيسي
```

## التثبيت

### 1. تثبيت المكتبات
```bash
pip install -r requirements.txt
```

### 2. إعداد متغيرات البيئة
عدّل ملف `.env` بإضافة بيانات الاتصال:
```env
DB_NAME=iran_news_pipeline
DB_HOST=dpg-d6hl9v7gi27c73ftat10-a.oregon-postgres.render.com
DB_USER=iran_news_pipeline_user
DB_PASSWORD=YalzyXWb1nYt3IQfyumiQa16r0HFrPta
DB_PORT=5432
```

### 3. إنشاء الجداول
قم بتشغيل ملف `database/schema.sql` على قاعدة البيانات:
```bash
psql -h dpg-d6hl9v7gi27c73ftat10-a.oregon-postgres.render.com \
     -U iran_news_pipeline_user \
     -d iran_news_pipeline \
     -f database/schema.sql
```

## الاستخدام

### تشغيل البرنامج الرئيسي
```bash
python main.py
```

### ماذا يفعل البرنامج؟
1. ✅ يقرأ RSS من المصادر الثلاثة (Ynet, Walla, Maariv)
2. ✅ يسحب النص الكامل لكل مقالة
3. ✅ يخزن البيانات الخام في جدول `raw_data`
4. ✅ يطبع عينات من المقالات

## هيكل جدول raw_data

| العمود | النوع | الوصف |
|--------|-------|-------|
| id | BIGSERIAL | المفتاح الأساسي |
| source_id | BIGINT | مفتاح أجنبي → sources |
| url | TEXT | رابط المحتوى الأصلي |
| content | TEXT | النص الخام المستخرج |
| published_at | TIMESTAMP | تاريخ النشر الأصلي |
| fetched_at | TIMESTAMP | وقت جلب البيانات |
| is_processed | BOOLEAN | هل تمت معالجته |
| media_url | TEXT | رابط الصورة/الفيديو |
| stt_status | VARCHAR | حالة Speech-to-Text |
| tags | TEXT | الوسوم المرتبطة |
| original_language | VARCHAR | اللغة الأصلية (he) |

## المصادر المدعومة

- **Ynet**: https://www.ynet.co.il/Integration/StoryRss2.xml
- **Walla**: https://rss.walla.co.il/feed/1
- **Maariv**: https://www.maariv.co.il/Rss/RssChadashot

## الإعدادات

عدّل ملف `.env` للتحكم في:
- `MAX_ITEMS_PER_SOURCE`: عدد المقالات لكل مصدر (افتراضي: 5)
- `FETCH_FULL_ARTICLE`: هل تسحب النص الكامل (افتراضي: true)
- `DELAY_BETWEEN_REQUESTS`: التأخير بين الطلبات بالثواني (افتراضي: 1.5)
- `LOG_LEVEL`: مستوى التسجيل (INFO, DEBUG, ERROR)

## الملفات المهمة

- `config/settings.py` - جميع الإعدادات والـ FEEDS
- `database/connection.py` - إدارة الاتصال بقاعدة البيانات
- `database/schema.sql` - هيكل الجداول
- `scrapers/rss_scraper.py` - قراءة RSS
- `scrapers/article_scraper.py` - سحب المقالات الكاملة
- `storage/database_storage.py` - حفظ البيانات في قاعدة البيانات

## ملاحظات

- البيانات تُخزن مباشرة في قاعدة البيانات (لا JSON)
- الحقول المتعلقة بالترجمة والمعالجة متروكة فارغة (للمراحل اللاحقة)
- يتم تجنب التكرار باستخدام `ON CONFLICT` في قاعدة البيانات
