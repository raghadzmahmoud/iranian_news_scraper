"""
اختبار تنظيف نصوص التغريدات
"""
import re


def clean_tweet_text(text: str) -> str:
    """
    تنظيف نص التغريدة من الروابط والهاشتاغات الزائدة
    """
    if not text:
        return text
    
    # إزالة الروابط (https://t.co/...)
    text = re.sub(r'https?://t\.co/\w+', '', text)
    
    # إزالة الروابط العادية
    text = re.sub(r'https?://[^\s]+', '', text)
    
    # إزالة المسافات الزائدة (قبل حذف الهاشتاغات)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # إزالة جميع الهاشتاغات من نهاية النص (واحد أو أكثر، مع أو بدون مسافات أو علامات ترقيم)
    # مثال: .#نشرة_المحافظات#العُمانية أو #عاجل #أخبار
    text = re.sub(r'[.\s]*#[\w_]+(\s*#[\w_]+)*\s*$', '', text)
    
    # إزالة المسافات من البداية والنهاية مرة أخرى
    text = text.strip()
    
    return text


def test_cleaning():
    """اختبار التنظيف"""
    print("=" * 80)
    print("🧪 اختبار تنظيف نصوص التغريدات")
    print("=" * 80)
    
    test_cases = [
        {
            "original": 'إنجاز مشروع تأهيل وصيانة طريق "طوي اعتير – وادي ركح – جبجات" في ولايتي طاقة ومرباط بمحافظة #ظفار بتكلفة إجمالية بلغت أكثر من مليون و800 ألف ريال عُماني.https://t.co/jIVRVCfvQz#نشرة_المحافظات#العُمانية https://t.co/YkmCMij2hf',
            "expected": 'إنجاز مشروع تأهيل وصيانة طريق "طوي اعتير – وادي ركح – جبجات" في ولايتي طاقة ومرباط بمحافظة #ظفار بتكلفة إجمالية بلغت أكثر من مليون و800 ألف ريال عُماني.'
        },
        {
            "original": "عاجل: مقتل 10 جنود في هجوم https://t.co/abc123 #عاجل #أخبار",
            "expected": "عاجل: مقتل 10 جنود في هجوم"
        },
        {
            "original": "الطقس اليوم في #دبي جميل https://example.com/weather",
            "expected": "الطقس اليوم في #دبي جميل"
        },
        {
            "original": "تصريح هام من الرئيس #سياسة",
            "expected": "تصريح هام من الرئيس"
        }
    ]
    
    print("\n📋 اختبار الحالات:\n")
    
    passed = 0
    failed = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n[{i}] الأصلي:")
        print(f"    {case['original']}")
        
        cleaned = clean_tweet_text(case['original'])
        
        print(f"\n    المنظف:")
        print(f"    {cleaned}")
        
        print(f"\n    المتوقع:")
        print(f"    {case['expected']}")
        
        if cleaned == case['expected']:
            print(f"\n    ✅ النتيجة صحيحة")
            passed += 1
        else:
            print(f"\n    ❌ النتيجة مختلفة")
            failed += 1
        
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("📊 النتائج:")
    print(f"   ✅ نجح: {passed}/{len(test_cases)}")
    print(f"   ❌ فشل: {failed}/{len(test_cases)}")
    print("=" * 80)


if __name__ == "__main__":
    test_cleaning()
