# Render Deployment Guide

## المشاكل المتوقعة عند الـ Deploy على Render

### 1. **مشاكل الـ Browser (Playwright)**
- ❌ **المشكلة**: Chrome بيحتاج memory كتير على Render
- ✅ **الحل**: 
  - استخدم `--disable-dev-shm-usage` (critical)
  - استخدم `--single-process` لتقليل الـ memory
  - استخدم `/tmp` للـ Chrome profile (يُحذف بين الـ deploys)

### 2. **مشاكل الـ Authentication**
- ❌ **المشكلة**: الـ Chrome profile بتنتهي صلاحيتها بين الـ deploys
- ✅ **الحل**:
  - الـ profile بتُحفظ في `/tmp/playwright_profile`
  - عند كل deploy جديد، بتحتاج تسجيل دخول جديد
  - استخدم environment variables للـ credentials

### 3. **مشاكل الـ Rate Limiting من X**
- ❌ **المشكلة**: X بتحجب requests من Render IPs (معروفة إنها data center)
- ✅ **الحل**:
  - زيادة الـ delays بين الـ accounts (`X_DELAY_BETWEEN_ACCOUNTS = 5`)
  - تقليل عدد الـ tweets المسحوبة (`X_MAX_TWEETS = 20`)
  - استخدام proxy service (اختياري)

### 4. **مشاكل الـ Timeout**
- ❌ **المشكلة**: Render بتقطع الـ processes بعد 30 دقيقة
- ✅ **الحل**:
  - استخدم Background Workers (لا توقت محدد)
  - قسّم الـ scraping إلى batches صغيرة
  - استخدم `render.yaml` للـ job scheduling

## خطوات الـ Deployment

### 1. إضافة `render.yaml`
```bash
# الملف موجود بالفعل - يحتوي على:
# - Web service (API)
# - Background workers (X scraper, translation, audio)
```

### 2. تحديث الـ Environment Variables على Render
```
DATABASE_URL=postgresql://...
X_USERNAME=your_x_username
X_PASSWORD=your_x_password
RENDER=true
```

### 3. أول مرة تشغيل
- الـ X scraper بيحتاج تسجيل دخول يدوي أول مرة
- قد تحتاج تفعيل الـ 2FA يدويًا

### 4. مراقبة الـ Logs
```bash
# على Render dashboard:
# - اذهب إلى Background Workers
# - اختر x-scraper-worker
# - شوف الـ logs
```

## الـ Optimizations المطبقة

| الإعداد | Local | Render |
|--------|-------|--------|
| Batch Size | 10 | 5 |
| Delay بين الـ Accounts | 2s | 5s |
| Max Scrolls | 5 | 3 |
| Max Tweets | 50 | 20 |
| Timeout | 30s | 60s |

## نصائح إضافية

### إذا استمرت مشاكل الـ Rate Limiting:
1. استخدم proxy service (Bright Data, Oxylabs)
2. قلل عدد الـ sources المسحوبة
3. زيادة الـ delays أكثر

### إذا استمرت مشاكل الـ Memory:
1. استخدم Render's Pro plan (أكثر memory)
2. قسّم الـ scraping إلى عدة workers
3. استخدم headless mode بدون GUI

### إذا انقطعت الـ Session:
1. تأكد من صحة الـ credentials
2. فعّل 2FA على X account
3. استخدم app passwords بدل الـ main password

## Troubleshooting

### Error: "Page.wait_for_selector: Timeout"
```python
# الحل: زيادة الـ timeout
await page.wait_for_selector(selector, timeout=60000)  # 60 seconds
```

### Error: "Failed to launch browser"
```python
# الحل: استخدم الـ args الصحيحة
"args": ["--disable-dev-shm-usage", "--single-process"]
```

### Error: "Session expired"
```python
# الحل: إعادة تسجيل الدخول تلقائيًا
# الكود بالفعل يعيد المحاولة تلقائيًا
```

## الـ Monitoring

### استخدم Render's Metrics:
- CPU usage
- Memory usage
- Disk usage
- Network I/O

### استخدم الـ Logs:
- تحقق من الـ errors
- تحقق من الـ rate limiting
- تحقق من الـ authentication issues
