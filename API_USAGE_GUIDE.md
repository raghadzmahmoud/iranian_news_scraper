# User Input APIs - دليل الاستخدام

## نظرة عامة
هذا الدليل يشرح كيفية استخدام APIs نظام إدخال البيانات من المستخدم (نص، صوت، فيديو).

---

## 1️⃣ إدخال النصوص اليدوية (Manual Text Input)

### Endpoint
```
POST /news/manual
```

### Request Body
```json
{
  "text": "نص الخبر الذي يريد المستخدم إدخاله",
  "source_id": 1
}
```

### Response (Success)
```json
{
  "success": true,
  "news_id": 123,
  "message": "تم حفظ الخبر بنجاح",
  "data": {
    "id": 123,
    "content": "نص الخبر",
    "title": "عنوان الخبر",
    "category": "عام",
    "tags": ["مستخدم", "إدخال يدوي"],
    "created_at": "2024-03-01T10:00:00"
  }
}
```

### Response (Error)
```json
{
  "detail": {
    "error": "النص فارغ",
    "message": "يجب إدخال نص غير فارغ"
  }
}
```

### cURL Example
```bash
curl -X POST "http://localhost:8000/news/manual" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "هذا خبر جديد من المستخدم",
    "source_id": 1
  }'
```

### Python Example
```python
import requests

url = "http://localhost:8000/news/manual"
data = {
    "text": "هذا خبر جديد من المستخدم",
    "source_id": 1
}

response = requests.post(url, json=data)
print(response.json())
```

---

## 2️⃣ إدخال الملفات الصوتية (Audio Input)

### Endpoints

#### أ) رفع ملف صوتي
```
POST /media/input/audio/upload
```

#### ب) تسجيل صوتي جديد
```
POST /media/input/audio/record
```

#### ج) التحقق من حالة المعالجة
```
GET /media/input/audio/status/{uploaded_file_id}
```

### Request (Upload/Record)
```
Content-Type: multipart/form-data
file: <audio file>
user_id: 1 (optional)
```

### Response (Success)
```json
{
  "success": true,
  "data": {
    "uploaded_file_id": 456,
    "raw_data_id": 789,
    "audio_url": "https://s3.amazonaws.com/audio/recording.mp3",
    "message": "تم رفع الملف بنجاح. سيتم معالجته في الخلفية."
  }
}
```

### Status Response (Processing)
```json
{
  "success": true,
  "data": {
    "uploaded_file_id": 456,
    "filename": "recording.mp3",
    "status": "processing",
    "transcription": null,
    "processed_at": null
  }
}
```

### Status Response (Completed)
```json
{
  "success": true,
  "data": {
    "uploaded_file_id": 456,
    "filename": "recording.mp3",
    "status": "completed",
    "transcription": "هذا نص الخبر المستخرج من الصوت",
    "processed_at": "2024-03-01T10:30:00"
  }
}
```

### Supported Audio Formats
- MP3 (`audio/mpeg`)
- WAV (`audio/wav`)
- WebM (`audio/webm`)
- OGG (`audio/ogg`)
- FLAC (`audio/flac`)

### Max File Size
- 50 MB

### cURL Examples

#### Upload Audio
```bash
curl -X POST "http://localhost:8000/media/input/audio/upload" \
  -F "file=@recording.mp3" \
  -F "user_id=1"
```

#### Record Audio
```bash
curl -X POST "http://localhost:8000/media/input/audio/record" \
  -F "file=@recording.mp3" \
  -F "user_id=1"
```

#### Check Status
```bash
curl "http://localhost:8000/media/input/audio/status/456"
```

### Python Examples

#### Upload Audio
```python
import requests

url = "http://localhost:8000/media/input/audio/upload"
files = {"file": open("recording.mp3", "rb")}
params = {"user_id": 1}

response = requests.post(url, files=files, params=params)
print(response.json())
```

#### Check Status
```python
import requests

url = "http://localhost:8000/media/input/audio/status/456"
response = requests.get(url)
print(response.json())
```

---

## 3️⃣ إدخال الملفات الفيديو (Video Input)

### Endpoints

#### أ) رفع ملف فيديو
```
POST /media/input/video/upload
```

#### ب) تسجيل فيديو جديد
```
POST /media/input/video/record
```

#### ج) التحقق من حالة المعالجة
```
GET /media/input/video/status/{uploaded_file_id}
```

### Request (Upload/Record)
```
Content-Type: multipart/form-data
file: <video file>
user_id: 1 (optional)
```

### Response (Success)
```json
{
  "success": true,
  "data": {
    "uploaded_file_id": 789,
    "raw_data_id": 1011,
    "video_url": "https://s3.amazonaws.com/video/recording.mp4",
    "audio_url": "https://s3.amazonaws.com/video/extracted_recording.wav",
    "message": "تم رفع الملف بنجاح. سيتم معالجته في الخلفية."
  }
}
```

### Status Response (Processing)
```json
{
  "success": true,
  "data": {
    "uploaded_file_id": 789,
    "filename": "recording.mp4",
    "status": "processing",
    "transcription": null,
    "processed_at": null
  }
}
```

### Status Response (Completed)
```json
{
  "success": true,
  "data": {
    "uploaded_file_id": 789,
    "filename": "recording.mp4",
    "status": "completed",
    "transcription": "هذا نص الخبر المستخرج من الفيديو",
    "processed_at": "2024-03-01T10:45:00"
  }
}
```

### Supported Video Formats
- MP4 (`video/mp4`)
- WebM (`video/webm`)
- MOV (`video/quicktime`)
- AVI (`video/x-msvideo`)
- MKV (`video/x-matroska`)

### Max File Size
- 500 MB

### cURL Examples

#### Upload Video
```bash
curl -X POST "http://localhost:8000/media/input/video/upload" \
  -F "file=@recording.mp4" \
  -F "user_id=1"
```

#### Record Video
```bash
curl -X POST "http://localhost:8000/media/input/video/record" \
  -F "file=@recording.mp4" \
  -F "user_id=1"
```

#### Check Status
```bash
curl "http://localhost:8000/media/input/video/status/789"
```

### Python Examples

#### Upload Video
```python
import requests

url = "http://localhost:8000/media/input/video/upload"
files = {"file": open("recording.mp4", "rb")}
params = {"user_id": 1}

response = requests.post(url, files=files, params=params)
print(response.json())
```

#### Check Status
```python
import requests

url = "http://localhost:8000/media/input/video/status/789"
response = requests.get(url)
print(response.json())
```

---

## 📊 مقارنة الطرق الثلاث

| الميزة | نص يدوي | صوت | فيديو |
|--------|--------|------|-------|
| **Endpoint** | `/news/manual` | `/media/input/audio/upload` أو `/record` | `/media/input/video/upload` أو `/record` |
| **Upload vs Record** | N/A | ✅ نفس المعالجة | ✅ نفس المعالجة |
| **معالجة فورية** | ✅ نعم | ❌ خلفية | ❌ خلفية |
| **STT** | ❌ لا | ✅ نعم | ✅ نعم |
| **استخراج الصوت** | ❌ لا | ❌ لا | ✅ نعم |
| **رفع S3** | ❌ لا | ✅ نعم | ✅ نعم |
| **Max Size** | N/A | 50 MB | 500 MB |

---

## 🔄 تدفق البيانات

### 1. إدخال نص يدوي
```
المستخدم يرسل نص
    ↓
معالجة بـ AI (تحسين + تصنيف)
    ↓
حفظ في raw_data
    ↓
إنشاء مجموعة (cluster)
    ↓
إنشاء محتوى مُنتج
```

### 2. إدخال صوت
```
المستخدم يرفع/يسجل ملف صوتي
    ↓
رفع إلى S3
    ↓
حفظ بيانات الملف
    ↓
Background Job:
  - تحويل الصوت لنص (STT)
  - تحسين النص
  - تصنيف الخبر
  - حفظ في raw_data
    ↓
إنشاء مجموعة (cluster)
    ↓
إنشاء محتوى مُنتج
```

### 3. إدخال فيديو
```
المستخدم يرفع/يسجل ملف فيديو
    ↓
رفع الفيديو إلى S3
    ↓
استخراج الصوت من الفيديو
    ↓
رفع الصوت المستخرج إلى S3
    ↓
حفظ بيانات الملف
    ↓
Background Job:
  - تحويل الصوت لنص (STT)
  - تحسين النص
  - تصنيف الخبر
  - حفظ في raw_data
    ↓
إنشاء مجموعة (cluster)
    ↓
إنشاء محتوى مُنتج
```

---

## 🗄️ جداول قاعدة البيانات

### raw_data
يحفظ الأخبار والمحتوى المدخل من المستخدم

| Column | Type | الوصف |
|--------|------|-------|
| `id` | bigint | معرف السجل |
| `source_id` | bigint | معرف المصدر (5=صوت، 6=فيديو، 7=نص) |
| `source_type_id` | integer | نوع المصدر (5=user_input) |
| `url` | text | رابط أو مسار الملف |
| `content` | text | محتوى النص |
| `media_url` | text | رابط الملف الأصلي |
| `stt_status` | text | حالة STT (pending, processing, completed, failed) |
| `is_processed` | boolean | هل تمت المعالجة |
| `processed_at` | timestamp | تاريخ انتهاء المعالجة |
| `tags` | text | الوسوم المستخرجة |
| `created_at` | timestamp | تاريخ الإنشاء |

### uploaded_files
يحفظ بيانات الملفات المرفوعة

| Column | Type | الوصف |
|--------|------|-------|
| `id` | bigint | معرف الملف |
| `filename` | varchar | اسم الملف |
| `s3_url` | text | رابط الملف على S3 |
| `audio_s3_url` | text | رابط الصوت المستخرج (للفيديو) |
| `content_type` | varchar | نوع المحتوى |
| `file_size` | bigint | حجم الملف |
| `user_id` | integer | معرف المستخدم |
| `status` | varchar | حالة المعالجة |
| `transcription` | text | النص المستخرج |
| `processed_at` | timestamp | تاريخ انتهاء المعالجة |
| `created_at` | timestamp | تاريخ الإنشاء |

---

## ⚙️ معالجة الأخطاء

### أنواع الأخطاء الشائعة

| الخطأ | السبب | الحل |
|------|------|------|
| `النص فارغ` | لم يتم إدخال نص | تأكد من إدخال نص غير فارغ |
| `نوع ملف غير مدعوم` | صيغة الملف غير صحيحة | استخدم صيغة مدعومة |
| `حجم الملف كبير جدًا` | الملف يتجاوز الحد الأقصى | استخدم ملف أصغر |
| `فشل الرفع إلى S3` | مشكلة في الاتصال بـ AWS | تحقق من إعدادات AWS |
| `فشل في حفظ البيانات` | مشكلة في قاعدة البيانات | تحقق من الاتصال بـ DB |

---

## 🚀 البدء السريع

### 1. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 2. تشغيل الخادم
```bash
uvicorn main:app --reload
```

### 3. اختبار الـ APIs
```bash
# إدخال نص يدوي
curl -X POST "http://localhost:8000/news/manual" \
  -H "Content-Type: application/json" \
  -d '{"text": "خبر جديد"}'

# رفع ملف صوتي
curl -X POST "http://localhost:8000/media/input/audio/upload" \
  -F "file=@audio.mp3"

# رفع ملف فيديو
curl -X POST "http://localhost:8000/media/input/video/upload" \
  -F "file=@video.mp4"
```

---

## 📚 المراجع

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
