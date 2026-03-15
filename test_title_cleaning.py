"""
اختبار تنظيف العناوين من التغريدات
"""
import re


def clean_tweet_text(text: str) -> str:
    """تنظيف نص التغريدة"""
    if not text:
        return text
    
    text = re.sub(r'https?://t\.co/\w+', '', text)
    text = re.sub(r'https?://[^\s]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    text = re.sub(r'[.\s]*#[\w_]+(\s*#[\w_]+)*\s*$', '', text)
    text = text.strip()
    
    return text


def create_title(cleaned_text: str) -> str:
    """إنشاء عنوان من النص المنظف"""
    if len(cleaned_text) > 100:
        title = cleaned_text[:100]
        # نقطع عند آخر مسافة لتجنب قطع الكلمات
        last_space = title.rfind(' ')
        if last_space > 50:
            title = title[:last_space]
        title = title.strip() + "..."
    else:
        title = cleaned_text
    
    return title


def test_title_cleaning():
    """اختبار تنظيف العناوين"""
    print("=" * 80)
    print("🧪 اختبار تنظيف العناوين من التغريدات")
    print("=" * 80)
    
    test_cases = [
        {
            "original": "6.2 مليون دينار حجم التداول في بورصة عمان https://t.co/L17f8y6dKd #بترا #الأردن https://t.co/LmNlKtidjG",
            "expected_content": "6.2 مليون دينار حجم التداول في بورصة عمان",
            "expected_title": "6.2 مليون دينار حجم التداول في بورصة عمان"
        },
        {
            "original": "عاجل: إطلاق 50 صاروخ على المدينة مما أدى إلى دمار كبير وسقوط عشرات الضحايا في هجوم استهدف المنطقة السكنية https://t.co/abc123 #عاجل #أخبار",
            "expected_content": "عاجل: إطلاق 50 صاروخ على المدينة مما أدى إلى دمار كبير وسقوط عشرات الضحايا في هجوم استهدف المنطقة السكنية",
            "expected_title": "عاجل: إطلاق 50 صاروخ على المدينة مما أدى إلى دمار كبير وسقوط عشرات الضحايا في..."
        },
        {
            "original": "تصريح قصير #سياسة",
            "expected_content": "تصريح قصير",
            "expected_title": "تصريح قصير"
        }
    ]
    
    print("\n📋 اختبار الحالات:\n")
    
    passed = 0
    failed = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n[{i}] الأصلي:")
        print(f"    {case['original']}")
        
        # تنظيف النص
        cleaned = clean_tweet_text(case['original'])
        
        print(f"\n    المحتوى المنظف:")
        print(f"    {cleaned}")
        
        # إنشاء العنوان
        title = create_title(cleaned)
        
        print(f"\n    العنوان:")
        print(f"    {title}")
        
        print(f"\n    المتوقع (محتوى):")
        print(f"    {case['expected_content']}")
        
        print(f"\n    المتوقع (عنوان):")
        print(f"    {case['expected_title']}")
        
        # التحقق
        content_ok = cleaned == case['expected_content']
        title_ok = title == case['expected_title']
        
        if content_ok and title_ok:
            print(f"\n    ✅ النتيجة صحيحة")
            passed += 1
        else:
            print(f"\n    ❌ النتيجة مختلفة")
            if not content_ok:
                print(f"       المحتوى مختلف")
            if not title_ok:
                print(f"       العنوان مختلف")
            failed += 1
        
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("📊 النتائج:")
    print(f"   ✅ نجح: {passed}/{len(test_cases)}")
    print(f"   ❌ فشل: {failed}/{len(test_cases)}")
    print("=" * 80)


if __name__ == "__main__":
    test_title_cleaning()
