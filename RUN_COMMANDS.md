# أوامر التشغيل - Run Commands

## 🚀 تشغيل النظام

### Terminal 1: تشغيل الـ API
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

**الـ API سيكون متاح على:**
- http://localhost:8000/
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

---

### Terminal 2: تشغيل الـ Worker (Background Jobs)
```bash
python worker.py
```

**الـ Worker سيبدأ معالجة الملفات المعلقة تلقائياً**

---

## 📊 تدفق العمل

```
┌─────────────────────────────────────────────────────────────┐
│                    المستخدم (Frontend)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   API (Terminal 1)     │
        │  uvicorn app:app       │
        ├────────────────────────┤
        │ POST /news/manual      │
        │ POST /media/input/...  │
        │ GET /media/input/...   │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   قاعدة البيانات       │
        │   PostgreSQL           │
        └────────────────────────┘
                     ▲
                     │
        ┌────────────────────────┐
        │  Worker (Terminal 2)   │
        │   python worker.py     │
        ├────────────────────────┤
        │ • فحص الملفات المعلقة  │
        │ • تحويل الصوت لنص      │
        │ • فحص الكلمات المفتاحية│
        │ • تحديث قاعدة البيانات │
        └────────────────────────┘
```

---

## 🔄 مثال على الاستخدام

### 1. رفع ملف صوتي (من الـ Frontend)
```bash
curl -X POST "http://localhost:8000/media/input/audio/upload" \
  -F "file=@recording.mp3"
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "uploaded_file_id": 1,
    "raw_data_id": 1,
    "audio_url": "https://s3.amazonaws.com/audio/recording.mp3",
    "message": "تم رفع الملف بنجاح. سيتم معالجته في الخلفية."
  }
}
```

### 2. التحقق من الحالة (من الـ Frontend)
```bash
curl "http://localhost:8000/media/input/audio/status/1"
```

**الاستجابة (أثناء المعالجة):**
```json
{
  "success": true,
  "data": {
    "uploaded_file_id": 1,
    "filename": "recording.mp3",
    "status": "processing",
    "transcription": null,
    "processed_at": null
  }
}
```

**الاستجابة (بعد الانتهاء):**
```json
{
  "success": true,
  "data": {
    "uploaded_file_id": 1,
    "filename": "recording.mp3",
    "status": "completed",
    "transcription": "كشف استطلاع رأي أجرته رويترز...",
    "processed_at": "2026-03-01T23:30:00"
  }
}
```

---

## 📝 ملاحظات مهمة

### ✅ المميزات
- **API سريع**: يرجع 200 فوراً بدون انتظار
- **Worker منفصل**: يعالج الملفات في الخلفية
- **لا تحتاج Terminal ثانية**: كل شيء في process واحد
- **قابل للتوسع**: يمكن تشغيل عدة Workers

### ⚠️ ملاحظات
- تأكد من تشغيل **كلا الـ Terminals** (API و Worker)
- الـ Worker يفحص الملفات المعلقة كل 5 ثوان
- إذا أغلقت الـ Worker، لن تتم معالجة الملفات الجديدة

---

## 🛑 إيقاف النظام

### إيقاف الـ API (Terminal 1)
```bash
CTRL+C
```

### إيقاف الـ Worker (Terminal 2)
```bash
CTRL+C
```

---

## 🔧 استكشاف الأخطاء

### المشكلة: الملفات لا تتم معالجتها
**الحل**: تأكد من تشغيل الـ Worker في Terminal 2

### المشكلة: خطأ في الاتصال بقاعدة البيانات
**الحل**: تحقق من إعدادات `.env`

### المشكلة: الـ API بطيء
**الحل**: تأكد من أن الـ Worker يعمل بشكل صحيح

---

## 📊 مراقبة الـ Logs

### Logs الـ API
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Logs الـ Worker
```
✅ تم الاتصال بقاعدة البيانات
✅ الـ Worker يعمل الآن...
🎙️ جاري معالجة الملف الصوتي: 1
```

---

## 🎯 الخلاصة

**شغل في Terminal 1:**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

**شغل في Terminal 2:**
```bash
python worker.py
```

**وخلاص! النظام يعمل بكامل طاقته!** 🚀
