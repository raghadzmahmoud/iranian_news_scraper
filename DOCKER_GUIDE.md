# دليل Docker للـ API

## المتطلبات
- Docker
- Docker Compose (اختياري)

## البناء والتشغيل

### الطريقة 1: استخدام Docker Compose (الموصى به)

```bash
# بناء الصورة وتشغيل الحاوية
docker-compose up -d

# عرض السجلات
docker-compose logs -f api

# إيقاف الخدمة
docker-compose down
```

### الطريقة 2: استخدام Docker مباشرة

```bash
# بناء الصورة
docker build -t user-input-api:latest .

# تشغيل الحاوية
docker run -d \
  --name user-input-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/logs:/app/logs \
  user-input-api:latest

# عرض السجلات
docker logs -f user-input-api

# إيقاف الحاوية
docker stop user-input-api
docker rm user-input-api
```

## الوصول للـ API

بعد التشغيل، يمكنك الوصول للـ API على:
- **الـ API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## متغيرات البيئة

تأكد من وجود ملف `.env` يحتوي على المتغيرات المطلوبة:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/dbname

# AWS Configuration
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your_bucket

# Google Cloud
GOOGLE_CREDENTIALS_JSON=your_credentials

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## الأوامر المفيدة

```bash
# عرض الصور المتاحة
docker images

# عرض الحاويات الجارية
docker ps

# عرض جميع الحاويات
docker ps -a

# حذف صورة
docker rmi user-input-api:latest

# حذف حاوية
docker rm user-input-api

# دخول الحاوية
docker exec -it user-input-api bash

# عرض استهلاك الموارد
docker stats user-input-api
```

## استكشاف الأخطاء

### المشكلة: الحاوية تتوقف فوراً
```bash
# عرض السجلات
docker logs user-input-api
```

### المشكلة: لا يمكن الاتصال بقاعدة البيانات
- تأكد من أن متغيرات البيئة صحيحة في `.env`
- تأكد من أن قاعدة البيانات متاحة وقابلة للوصول

### المشكلة: مشاكل في الذاكرة
```bash
# زيادة حد الذاكرة
docker run -d \
  --memory=2g \
  --memory-swap=2g \
  ...
```

## الإنتاج

للنشر في الإنتاج:

1. استخدم صورة أساسية أخف وزناً
2. أضف health checks
3. استخدم restart policies
4. قم بتعيين حدود الموارد
5. استخدم logging drivers مناسبة

مثال متقدم:

```yaml
services:
  api:
    image: user-input-api:latest
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```
