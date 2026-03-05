"""
اختبار كاشف الأرقام المحسّن
"""
from utils.number_detector import NumberDetector


def test_number_detector():
    """اختبار شامل لكاشف الأرقام"""
    
    test_cases = [
        # حالات عربية
        {
            'text': 'قتل 50 جندياً في الغارة الأخيرة',
            'expected_has_numbers': True,
            'expected_war_context': True,
            'description': 'عربي - أرقام مع سياق حربي'
        },
        {
            'text': 'أصيب 25 مصاباً و 10 جرحى في الهجوم',
            'expected_has_numbers': True,
            'expected_war_context': True,
            'description': 'عربي - أرقام متعددة مع جمع'
        },
        {
            'text': 'دمّرت 3 طائرات و 5 مسيرات في الضربة',
            'expected_has_numbers': True,
            'expected_war_context': True,
            'description': 'عربي - أرقام مع مثنى وجمع'
        },
        {
            'text': 'استخدموا ٢٠ صاروخاً في الهجوم',
            'expected_has_numbers': True,
            'expected_war_context': True,
            'description': 'عربي - أرقام عربية مع سياق حربي'
        },
        
        # حالات إنجليزية
        {
            'text': '50 soldiers killed in the strike',
            'expected_has_numbers': True,
            'expected_war_context': True,
            'description': 'إنجليزي - أرقام مع سياق حربي'
        },
        {
            'text': '25 injured and 10 wounded in the attack',
            'expected_has_numbers': True,
            'expected_war_context': True,
            'description': 'إنجليزي - أرقام متعددة'
        },
        {
            'text': '3 aircraft and 5 drones destroyed',
            'expected_has_numbers': True,
            'expected_war_context': True,
            'description': 'إنجليزي - أرقام مع جمع'
        },
        
        # حالات عبرية
        {
            'text': '50 חיילים הרוגים בהתקפה',
            'expected_has_numbers': True,
            'expected_war_context': True,
            'description': 'عبري - أرقام مع سياق حربي'
        },
        {
            'text': '25 פצועים ו-10 הרוגים',
            'expected_has_numbers': True,
            'expected_war_context': True,
            'description': 'عبري - أرقام متعددة'
        },
        
        # حالات بدون أرقام
        {
            'text': 'الأخبار العاجلة من المنطقة',
            'expected_has_numbers': False,
            'expected_war_context': False,
            'description': 'عربي - بدون أرقام'
        },
        {
            'text': 'Breaking news from the region',
            'expected_has_numbers': False,
            'expected_war_context': False,
            'description': 'إنجليزي - بدون أرقام'
        },
        
        # حالات أرقام بدون سياق حربي
        {
            'text': 'السعر هو 100 دولار',
            'expected_has_numbers': True,
            'expected_war_context': False,
            'description': 'عربي - أرقام بدون سياق حربي'
        },
        {
            'text': 'The price is 100 dollars',
            'expected_has_numbers': True,
            'expected_war_context': False,
            'description': 'إنجليزي - أرقام بدون سياق حربي'
        },
    ]
    
    print("=" * 80)
    print("اختبار كاشف الأرقام المحسّن")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        result = NumberDetector.detect_numbers(test['text'], use_war_context=True)
        
        has_numbers_ok = result['has_numbers'] == test['expected_has_numbers']
        war_context_ok = result['has_war_context'] == test['expected_war_context']
        
        status = "✅ نجح" if (has_numbers_ok and war_context_ok) else "❌ فشل"
        
        if has_numbers_ok and war_context_ok:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{i}. {test['description']}")
        print(f"   النص: {test['text'][:60]}...")
        print(f"   {status}")
        print(f"   - أرقام: {result['has_numbers']} (متوقع: {test['expected_has_numbers']})")
        print(f"   - سياق حربي: {result['has_war_context']} (متوقع: {test['expected_war_context']})")
        print(f"   - أرقام إنجليزية: {len(result['english_digits'])}")
        print(f"   - أرقام عربية: {len(result['arabic_digits'])}")
        print(f"   - مطابقات حربية: {len(result['war_matches'])}")
    
    print("\n" + "=" * 80)
    print(f"النتائج: {passed} نجح، {failed} فشل من {len(test_cases)} اختبار")
    print("=" * 80)


if __name__ == '__main__':
    test_number_detector()
