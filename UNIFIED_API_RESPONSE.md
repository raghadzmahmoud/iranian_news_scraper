# Unified API Response Format

## Overview
جميع endpoints في النظام تستخدم نفس صيغة الـ Response الموحدة لضمان consistency وسهولة التعامل من الـ Frontend.

## Response Model Structure

```json
{
  "status": 200,
  "success": true,
  "message": "رسالة توضيحية",
  "error_code": null,
  "data": {},
  "details": null
}
```

### Fields Description

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | int | ✅ | HTTP Status Code (200, 400, 404, 500, etc.) |
| `success` | bool | ✅ | نجاح أو فشل العملية |
| `message` | string | ✅ | رسالة توضيحية للمستخدم (بالعربية) |
| `error_code` | string | ❌ | كود الخطأ (عند الفشل فقط) |
| `data` | object | ❌ | البيانات المرجعة (عند النجاح) |
| `details` | string | ❌ | تفاصيل إضافية عن الخطأ |

---

## Endpoints Using Unified Response

### 1. Manual Text Input
**Endpoint:** `POST /api/news/manual`

#### Success Response (201)
```json
{
  "status": 200,
  "success": true,
  "message": "تم قبول الخبر وحفظه بنجاح",
  "data": {
    "id": 42,
    "title": "عنوان الخبر",
    "content": "محتوى الخبر",
    "tags": ["إيران", "إسرائيل"],
    "created_at": "2026-03-03T10:30:45.123456"
  }
}
```

#### Error Response - Irrelevant News (422)
```json
{
  "status": 422,
  "success": false,
  "error_code": "IRRELEVANT_NEWS",
  "message": "تم رفض الخبر لأنه لا يندرج ضمن نطاق التغطية",
  "details": "الخبر لا يندرج ضمن نطاق التغطية (إيران – إسرائيل – التصعيد العسكري الحالي)"
}
```

---

### 2. Audio Upload
**Endpoint:** `POST /api/media/audio/upload`

#### Success Response (200)
```json
{
  "status": 200,
  "success": true,
  "message": "تم رفع الملف بنجاح. سيتم تحليل المحتوى في الخلفية للتحقق من ارتباطه بالأحداث الجارية. في حال عدم وجود صلة، لن يتم حفظه ضمن النظام.",
  "data": {
    "uploaded_file_id": 42,
    "audio_url": "s3://bucket/original_audios/audio.mp3"
  }
}
```

#### Error Response - Unsupported Format (400)
```json
{
  "status": 400,
  "success": false,
  "error_code": "UNSUPPORTED_FORMAT",
  "message": "نوع ملف غير مدعوم",
  "details": "الصيغ المدعومة: audio/mpeg, audio/wav, audio/webm, audio/ogg, audio/flac"
}
```

#### Error Response - File Too Large (400)
```json
{
  "status": 400,
  "success": false,
  "error_code": "FILE_TOO_LARGE",
  "message": "حجم الملف كبير جدًا",
  "details": "الحد الأقصى: 50 MB"
}
```

---

### 3. Audio Recording
**Endpoint:** `POST /api/media/audio/record`

نفس الـ Response كـ `/upload`

---

### 4. Audio Status
**Endpoint:** `GET /api/media/audio/status/{uploaded_file_id}`

#### Success Response (200)
```json
{
  "status": 200,
  "success": true,
  "message": "تم جلب حالة الملف بنجاح",
  "data": {
    "uploaded_file_id": 42,
    "filename": "audio.mp3",
    "status": "completed",
    "transcription": "النص المستخرج من الصوت",
    "processed_at": "2026-03-03T10:35:20.654321"
  }
}
```

#### Error Response - File Not Found (404)
```json
{
  "status": 404,
  "success": false,
  "error_code": "FILE_NOT_FOUND",
  "message": "الملف غير موجود",
  "details": "لم يتم العثور على الملف برقم 999"
}
```

---

### 5. Video Upload
**Endpoint:** `POST /api/media/video/upload`

#### Success Response (200)
```json
{
  "status": 200,
  "success": true,
  "message": "تم رفع الملف بنجاح. سيتم تحليل المحتوى في الخلفية للتحقق من ارتباطه بالأحداث الجارية. في حال عدم وجود صلة، لن يتم حفظه ضمن النظام.",
  "data": {
    "uploaded_file_id": 43,
    "video_url": "s3://bucket/original_videos/video.mp4"
  }
}
```

#### Error Response - Unsupported Format (400)
```json
{
  "status": 400,
  "success": false,
  "error_code": "UNSUPPORTED_FORMAT",
  "message": "نوع ملف غير مدعوم",
  "details": "الصيغ المدعومة: video/mp4, video/webm, video/quicktime, video/x-msvideo, video/x-matroska"
}
```

---

### 6. Video Recording
**Endpoint:** `POST /api/media/video/record`

نفس الـ Response كـ `/upload`

---

### 7. Video Status
**Endpoint:** `GET /api/media/video/status/{uploaded_file_id}`

#### Success Response (200)
```json
{
  "status": 200,
  "success": true,
  "message": "تم جلب حالة الملف بنجاح",
  "data": {
    "uploaded_file_id": 43,
    "filename": "video.mp4",
    "status": "completed",
    "transcription": "النص المستخرج من صوت الفيديو",
    "processed_at": "2026-03-03T10:40:15.987654"
  }
}
```

---

## Frontend Implementation Guide

### 1. Check Success/Failure
```javascript
if (response.success) {
  // Handle success
  console.log(response.message);
  const data = response.data;
} else {
  // Handle error
  console.error(response.error_code, response.message);
  if (response.details) {
    console.error("Details:", response.details);
  }
}
```

### 2. Display Messages
```javascript
// Show user-friendly message
showNotification(response.message, response.success ? 'success' : 'error');
```

### 3. Handle Specific Errors
```javascript
switch (response.error_code) {
  case 'IRRELEVANT_NEWS':
    showAlert('الخبر لا يندرج ضمن نطاق التغطية');
    break;
  case 'UNSUPPORTED_FORMAT':
    showAlert('صيغة الملف غير مدعومة');
    break;
  case 'FILE_TOO_LARGE':
    showAlert('حجم الملف كبير جدًا');
    break;
  case 'FILE_NOT_FOUND':
    showAlert('الملف غير موجود');
    break;
  default:
    showAlert('حدث خطأ غير متوقع');
}
```

### 4. Extract Data
```javascript
if (response.success && response.data) {
  const { id, uploaded_file_id, filename, status } = response.data;
  // Use the data
}
```

---

## Key Changes Made

### ✅ Removed
- `matched_keywords` field من جميع الـ responses
- Inconsistent message formats

### ✅ Added
- Unified `APIResponse` model لجميع الـ endpoints
- Consistent `error_code` field للأخطاء
- Standardized message format

### ✅ Standardized
- جميع الـ endpoints تستخدم نفس الـ response structure
- جميع الرسائل بالعربية
- جميع الأخطاء لها `error_code` واضح

---

## Supported File Formats

### Audio
- `audio/mpeg` (.mp3)
- `audio/wav` (.wav)
- `audio/webm` (.webm)
- `audio/ogg` (.ogg)
- `audio/flac` (.flac)

### Video
- `video/mp4` (.mp4)
- `video/webm` (.webm)
- `video/quicktime` (.mov)
- `video/x-msvideo` (.avi)
- `video/x-matroska` (.mkv)

---

## Processing Flow

### Manual Text Input
1. User submits text
2. System checks relevance against keywords
3. If relevant → Save to database → Return success
4. If not relevant → Return error with `IRRELEVANT_NEWS` code

### Audio/Video Upload
1. User uploads file
2. System validates format and size
3. File uploaded to S3
4. Metadata saved to database with `status: pending`
5. Background job processes the file
6. Job extracts audio (for video) and converts to text
7. Job checks relevance against keywords
8. If relevant → Save to database
9. If not relevant → Mark as rejected

---

## Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful operation |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input, unsupported format, file too large |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Valid format but content rejected (e.g., irrelevant news) |
| 500 | Server Error | Internal server error |
