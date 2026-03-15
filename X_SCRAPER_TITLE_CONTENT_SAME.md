# نفس النص للعنوان والمحتوى

## ✅ التغيير

تم تعديل الكود بحيث:
- `title_original` = النص المنظف
- `content_original` = النص المنظف

**نفس النص في الحقلين!**

## 🔧 التعديل

### قبل:
```python
# إنشاء عنوان مختلف (أول 100 حرف)
title = cleaned_text[:100] + "..." if len(cleaned_text) > 100 else cleaned_text

return NewsArticle(
    title=title,  # عنوان مختصر
    full_text=cleaned_text,  # نص كامل
)
```

### بعد:
```python
# نفس النص في الحقلين
return NewsArticle(
    title=cleaned_text,  # نفس النص المنظف
    full_text=cleaned_text,  # نفس النص المنظف
)
```

## 📊 النتيجة

### قبل:
```
title_original: "6.2 مليون دينار حجم التداول في بورصة عمان..."
content_original: "6.2 مليون دينار حجم التداول في بورصة عمان"
```

### بعد:
```
title_original: "6.2 مليون دينار حجم التداول في بورصة عمان"
content_original: "6.2 مليون دينار حجم التداول في بورصة عمان"
```

## ✅ الفوائد

1. **توحيد البيانات** - نفس النص في الحقلين
2. **بساطة** - لا حاجة لإنشاء عنوان منفصل
3. **وضوح** - النص كامل بدون قطع

## ✅ الخلاصة

الآن `title_original` و `content_original` يحتويان على نفس النص المنظف!
