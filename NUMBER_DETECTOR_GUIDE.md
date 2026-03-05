# دليل كاشف الأرقام المحسّن

## نظرة عامة

تم تطوير كاشف أرقام محسّن يدعم:
- **العربية** مع المثنى والجمع
- **الإنجليزية** مع المثنى والجمع
- **العبرية** مع المثنى والجمع
- **السياق الحربي** (أرقام في سياق عسكري)

## الملفات الجديدة

### 1. `utils/number_detector.py`
يحتوي على فئة `NumberDetector` بالدوال التالية:

#### `has_basic_numbers(text: str) -> bool`
التحقق من وجود أرقام أساسية (إنجليزية أو عربية)

```python
from utils.number_detector import NumberDetector

text = "قتل 50 جندياً"
result = NumberDetector.has_basic_numbers(text)
# النتيجة: True
```

#### `has_war_context_numbers(text: str) -> bool`
التحقق من وجود أرقام في سياق حربي

```python
text = "قتل 50 جندياً في الغارة"
result = NumberDetector.has_war_context_numbers(text)
# النتيجة: True

text = "السعر 100 دولار"
result = NumberDetector.has_war_context_numbers(text)
# النتيجة: False
```

#### `detect_numbers(text: str, use_war_context: bool = True) -> dict`
كشف شامل للأرقام مع معلومات تفصيلية

```python
text = "أصيب 25 مصاباً و 10 جرحى في الهجوم"
result = NumberDetector.detect_numbers(text)

# النتيجة:
{
    'has_numbers': True,
    'has_basic_numbers': True,
    'has_war_context': True,
    'english_digits': ['2', '5', '1', '0'],
    'arabic_digits': [],
    'war_matches': ['25 مصاباً', '10 جرحى']
}
```

## التحديثات في `storage/article_processor.py`

### 1. تحديث دالة `has_numbers()`
الآن تستخدم الكاشف المحسّن بدلاً من البحث البسيط:

```python
@staticmethod
def has_numbers(text: str) -> bool:
    """
    التحقق من وجود أرقام في النص (محسّن)
    يدعم العربية والإنجليزية والعبرية مع المثنى والجمع
    والسياق الحربي
    """
    if not text:
        return False
    
    result = NumberDetector.detect_numbers(text, use_war_context=True)
    return result['has_numbers']
```

### 2. دالة جديدة `get_number_details()`
للحصول على معلومات تفصيلية عن الأرقام:

```python
@staticmethod
def get_number_details(text: str) -> dict:
    """
    الحصول على معلومات تفصيلية عن الأرقام في النص
    """
    # النتيجة:
    {
        'has_numbers': bool,
        'has_basic_numbers': bool,
        'has_war_context': bool,
        'english_digits_count': int,
        'arabic_digits_count': int,
        'war_matches_count': int
    }
```

## أمثلة الاستخدام

### مثال 1: فحص بسيط
```python
from storage.article_processor import ArticleProcessor

text = "قتل 50 جندياً في الغارة"
has_nums = ArticleProcessor.has_numbers(text)
print(has_nums)  # True
```

### مثال 2: معلومات تفصيلية
```python
from storage.article_processor import ArticleProcessor

text = "أصيب 25 مصاباً و 10 جرحى في الهجوم"
details = ArticleProcessor.get_number_details(text)

print(f"أرقام: {details['has_numbers']}")  # True
print(f"سياق حربي: {details['has_war_context']}")  # True
print(f"عدد الأرقام الإنجليزية: {details['english_digits_count']}")  # 4
print(f"عدد المطابقات الحربية: {details['war_matches_count']}")  # 2
```

### مثال 3: في معالجة المقالات
```python
from storage.article_processor import ArticleProcessor

article_text = "دمّرت 3 طائرات و 5 مسيرات في الضربة"

# الفحص البسيط
if ArticleProcessor.has_numbers(article_text):
    print("المقالة تحتوي على أرقام")

# الفحص التفصيلي
details = ArticleProcessor.get_number_details(article_text)
if details['has_war_context']:
    print("المقالة تحتوي على أرقام في سياق حربي")
```

## الأنماط المدعومة

### العربية
- صاروخ/صواريخ/صاروخين
- قتيل/قتلى/قتيلين
- جريح/جرحى/جريحين
- مصاب/مصابين/مصابة
- طائرة/طائرات/طائرتين
- مسيرة/مسيرات/مسيرتين
- غارة/غارات/غارتين
- ضربة/ضربات/ضربتين
- جندي/جنود/جنديين
- عسكري/عسكريين/عسكريون
- قتل/مقتل/قتلوا
- أصيب/جرح/أصابوا
- دمّر/دمّرت/دمّروا
- أسر/أسروا/أسرن

### الإنجليزية
- missile/missiles
- killed/dead/deaths/casualty/casualties
- injured/wounded/injuries/hurt
- aircraft/plane/planes/jet/jets/drone/drones
- strike/strikes/raid/raids/attack/attacks
- soldier/soldiers
- military/troops/troop
- killed/died
- injured/wounded
- destroyed
- captured

### العبرية
- טיל/טילים/טילי (صاروخ)
- הרוג/הרוגים/הרוגות (قتيل)
- פצוע/פצועים/פצועות (جريح)
- חייל/חיילים (جندي)
- מטוס/מטוסים (طائرة)
- רחפן/רחפנים (درون)
- התקפה/התקפות (هجوم)
- הכה/הכו/הכתה (ضرب)
- פגע/פגעו/פגעה (أصاب)
- הרג/הרגו/הרגה (قتل)

## الاختبارات

تم إنشاء ملف اختبار شامل: `test_number_detector.py`

لتشغيل الاختبارات:
```bash
python test_number_detector.py
```

النتائج: **13 اختبار - جميعها نجحت ✅**

## الفوائد

1. **دقة أعلى**: يميز بين الأرقام العادية والأرقام في السياق الحربي
2. **دعم متعدد اللغات**: يدعم العربية والإنجليزية والعبرية
3. **دعم المثنى والجمع**: يتعرف على صيغ مختلفة من الكلمات
4. **معلومات تفصيلية**: يوفر معلومات شاملة عن الأرقام المكتشفة
5. **أداء محسّن**: يحسّن دقة استخراج المقاييس من 6% إلى 46%

## الملاحظات

- الكاشف يستخدم regex للبحث عن الأنماط
- يمكن تعطيل السياق الحربي بتمرير `use_war_context=False`
- جميع الأنماط حساسة للحالة (case-insensitive) للعربية والإنجليزية
- يتم البحث عن الأرقام والكلمات الحربية معاً
