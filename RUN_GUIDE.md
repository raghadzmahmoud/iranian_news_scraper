# 🚀 Complete Run Guide - Iran News Pipeline

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Upload (API)                        │
│  POST /media/input/audio/upload  (Audio)                    │
│  POST /media/input/video/upload  (Video)                    │
│  POST /news/manual               (Text)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   S3 Upload (AWS)      │
        │ - original/audios/     │
        │ - original/videos/     │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Database (PostgreSQL) │
        │ - uploaded_files       │
        │ - raw_data             │
        └────────────┬───────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   ┌─────────────┐          ┌──────────────┐
   │Audio Worker │          │Video Worker  │
   │(Background) │          │(Background)  │
   └──────┬──────┘          └──────┬───────┘
          │                        │
          ▼                        ▼
   ┌─────────────────────────────────────┐
   │  STT Service (Google Cloud)         │
   │  - Arabic (ar-SA, ar-EG, ar-JO)    │
   │  - English (en-US, en-GB)          │
   │  - Hebrew (he-IL)                  │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │  Keyword Filtering (Iran-related)   │
   │  - Layer 1: Basic keywords          │
   │  - Layer 2: Operations              │
   │  - Layer 3: Context                 │
   └──────────────┬──────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
   ┌─────────────┐    ┌──────────────┐
   │  Relevant   │    │  Rejected    │
   │  (Save)     │    │  (Discard)   │
   └─────────────┘    └──────────────┘
```

---

## Prerequisites

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python setup_database.py
```

This will:
- Create required tables
- Populate source_type (user_input = 5)
- Populate sources (audio=5, video=6, text=7)

### 3. Configure Environment
Make sure `.env` file has:
- Database credentials
- AWS S3 credentials
- Google Cloud credentials (for STT)
- API configuration

---

## Running the System

### Terminal 1: Start API Server
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**API Endpoints:**
- Text: `POST /news/manual` (Form Data)
- Audio: `POST /media/input/audio/upload` (File)
- Video: `POST /media/input/video/upload` (File)
- Status: `GET /media/input/audio/status/{id}`

---

### Terminal 2: Start Audio Worker
```bash
python worker_audio.py
```

**Output:**
```
🎙️ جاري بدء Audio Worker...
✅ تم الاتصال بقاعدة البيانات
✅ Audio Worker يعمل الآن...
📋 وجدت 1 ملف صوتي معلق
🎙️ جاري معالجة الملف الصوتي: 1
🎤 جاري تحويل الصوت لنص...
✅ تم تحويل الصوت: كشف استطلاع رأي أجرته رويترز...
🔍 جاري فحص الصلة بالكلمات المفتاحية...
✅ الخبر ذو صلة - الكلمات المفتاحية: ['إيران', 'ضربات']
💾 جاري تحديث قاعدة البيانات...
✅ تمت معالجة الملف الصوتي بنجاح: 1
```

---

### Terminal 3: Start Video Worker
```bash
python worker_video.py
```

**Output:**
```
🎬 جاري بدء Video Worker...
✅ تم الاتصال بقاعدة البيانات
✅ Video Worker يعمل الآن...
📋 وجدت 1 ملف فيديو معلق
🎬 جاري معالجة الملف الفيديو: 1
🎵 جاري استخراج الصوت من الفيديو...
✅ تم استخراج الصوت: s3://media-automation-bucket/original/audios/extracted_video.wav
🎤 جاري تحويل الصوت لنص...
✅ تم تحويل الصوت: كشف استطلاع رأي أجرته رويترز...
🔍 جاري فحص الصلة بالكلمات المفتاحية...
✅ الخبر ذو صلة - الكلمات المفتاحية: ['إيران', 'ضربات']
💾 جاري تحديث قاعدة البيانات...
✅ تمت معالجة الملف الفيديو بنجاح: 1
```

---

## Testing the System

### 1. Upload Audio File
```bash
curl -X POST "http://localhost:8000/media/input/audio/upload" \
  -F "file=@audio.mp3"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "uploaded_file_id": 1,
    "raw_data_id": 1,
    "audio_url": "https://media-automation-bucket.s3.us-east-1.amazonaws.com/original/audios/audio.mp3",
    "message": "تم رفع الملف بنجاح. سيتم معالجته في الخلفية."
  }
}
```

### 2. Upload Video File
```bash
curl -X POST "http://localhost:8000/media/input/video/upload" \
  -F "file=@video.mp4"
```

### 3. Upload Text (Manual Input)
```bash
curl -X POST "http://localhost:8000/news/manual" \
  -F "source_id=7" \
  -F "text=كشف استطلاع رأي أجرته رويترز أن ربع الأمريكيين فقط يؤيدون الضربات الأمريكية على إيران"
```

### 4. Check Processing Status
```bash
curl "http://localhost:8000/media/input/audio/status/1"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "uploaded_file_id": 1,
    "filename": "audio.mp3",
    "status": "completed",
    "transcription": "كشف استطلاع رأي أجرته رويترز...",
    "processed_at": "2026-03-02T10:30:45.123456"
  }
}
```

---

## S3 Folder Structure

```
media-automation-bucket/
├── original/
│   ├── audios/
│   │   ├── audio1.mp3
│   │   ├── audio2.wav
│   │   └── extracted_video1.wav
│   └── videos/
│       ├── video1.mp4
│       └── video2.mov
└── generated/
    ├── audios/
    ├── images/
    └── videos/
```

**Configuration in `.env`:**
```
S3_ORIGINAL_AUDIOS_FOLDER=original/audios/
S3_ORIGINAL_VIDEOS_FOLDER=original/videos/
S3_GENERATED_AUDIOS_FOLDER=generated/audios/
S3_GENERATED_VIDEOS_FOLDER=generated/videos/
```

---

## Database Schema

### uploaded_files
```sql
id              BIGSERIAL PRIMARY KEY
filename        VARCHAR(255)
s3_url          TEXT
audio_s3_url    TEXT (for videos)
content_type    VARCHAR(50)
file_size       BIGINT
user_id         INTEGER
status          VARCHAR(50) -- pending, processing, completed, rejected, failed
transcription   TEXT
processed_at    TIMESTAMP
created_at      TIMESTAMP
```

### raw_data
```sql
id              BIGSERIAL PRIMARY KEY
source_id       BIGINT (5=audio, 6=video, 7=text)
source_type_id  INTEGER (5=user_input)
url             TEXT
content         TEXT (transcription)
media_url       TEXT (S3 URL)
published_at    TIMESTAMP
fetched_at      TIMESTAMP
is_processed    BOOLEAN
processed_at    TIMESTAMP
stt_status      VARCHAR(50)
tags            TEXT (comma-separated keywords)
```

---

## Supported Languages

### STT Service
- 🇸🇦 **Arabic** (ar): ar-SA, ar-EG, ar-JO, ar-PS, ar-AE
- 🇺🇸 **English** (en): en-US, en-GB, en-AU
- 🇮🇱 **Hebrew** (he): he-IL

### Usage
```python
# Transcribe in specific language
result = stt_service.transcribe_audio(s3_url, language='ar')  # Arabic
result = stt_service.transcribe_audio(s3_url, language='en')  # English
result = stt_service.transcribe_audio(s3_url, language='he')  # Hebrew
```

---

## Keyword Filtering

### 3-Layer System
1. **Layer 1 (Basic)**: Direct Iran-related keywords
   - إيران, Iran, Israel, إسرائيل, etc.

2. **Layer 2 (Operations)**: Military/political operations
   - ضربات, strikes, هجوم, attack, etc.

3. **Layer 3 (Context)**: Contextual keywords
   - الشرق الأوسط, Middle East, etc.

### Filtering Logic
- **Relevant**: Contains keywords from Layer 1 + (Layer 2 OR Layer 3)
- **Rejected**: Doesn't meet relevance criteria
- **Status**: "completed" (relevant) or "rejected" (not relevant)

---

## Troubleshooting

### Audio Worker Not Processing
```bash
# Check if worker is running
ps aux | grep worker_audio.py

# Check database connection
python -c "from database.connection import db; print(db.connect())"

# Check logs
tail -f logs/app.log
```

### STT Service Errors
```
❌ google-cloud-speech not installed
→ pip install google-cloud-speech

❌ Google credentials not found
→ Set GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_CREDENTIALS_JSON in .env

❌ Audio too long
→ Using async recognition (automatic)
```

### S3 Upload Errors
```
❌ AWS credentials invalid
→ Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env

❌ Bucket not found
→ Verify S3_BUCKET_NAME exists in us-east-1
```

---

## Performance Tips

1. **Increase Worker Polling Frequency**
   - Edit `worker_audio.py` line: `time.sleep(5)` → `time.sleep(2)`

2. **Process Multiple Files**
   - Edit `worker_audio.py` line: `LIMIT 5` → `LIMIT 10`

3. **Optimize STT**
   - Use WAV format (faster than MP3)
   - Keep audio under 1 minute for sync recognition

4. **Database Optimization**
   - Add indexes on `status` and `media_url` columns
   - Archive old records regularly

---

## Quick Start (One Command)

Run all three components in one terminal (not recommended for production):
```bash
# Terminal 1
uvicorn app:app --host 0.0.0.0 --port 8000 --reload &

# Terminal 2
python worker_audio.py &

# Terminal 3
python worker_video.py &

# Wait for all to start
sleep 5

# Test
curl -X POST "http://localhost:8000/media/input/audio/upload" -F "file=@test.mp3"
```

---

## Production Deployment

### Using systemd (Linux)
```bash
# Create service file
sudo nano /etc/systemd/system/iran-news-api.service

[Unit]
Description=Iran News Pipeline API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable iran-news-api.service
sudo systemctl start iran-news-api.service
```

### Using Docker
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Monitoring

### Check System Status
```bash
# API health
curl http://localhost:8000/docs

# Database connection
python -c "from database.connection import db; print('✅ Connected' if db.connect() else '❌ Failed')"

# S3 access
python -c "import boto3; s3 = boto3.client('s3'); print(s3.list_buckets())"

# Worker processes
ps aux | grep worker
```

### View Logs
```bash
# API logs
tail -f logs/app.log

# System logs
journalctl -u iran-news-api.service -f
```

---

## Support

For issues or questions:
1. Check logs in `logs/app.log`
2. Verify `.env` configuration
3. Test database connection
4. Verify AWS S3 credentials
5. Check Google Cloud credentials
