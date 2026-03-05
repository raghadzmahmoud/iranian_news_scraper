"""
مثال عملي لاستخدام كاشف الأرقام المحسّن
"""
from utils.number_detector import NumberDetector
from storage.article_processor import ArticleProcessor


def example_1_basic_detection():
    """مثال 1: الكشف الأساسي"""
    print("\n" + "=" * 80)
    print("مثال 1: الكشف الأساسي للأرقام")
    print("=" * 80)
    
    texts = [
        "قتل 50 جندياً في الغارة الأخيرة",
        "السعر هو 100 دولار",
        "الأخبار العاجلة من المنطقة",
    ]
    
    for text in texts:
        has_nums = NumberDetector.has_basic_numbers(text)
        print(f"\nالنص: {text}")
        print(f"يحتوي على أرقام: {has_nums}")


def example_2_war_context():
    """مثال 2: الكشف عن السياق الحربي"""
    print("\n" + "=" * 80)
    print("مثال 2: الكشف عن السياق الحربي")
    print("=" * 80)
    
    texts = [
        "قتل 50 جندياً في الغارة",
        "أصيب 25 مصاباً و 10 جرحى",
        "السعر 100 دولار",
        "50 soldiers killed in the strike",
        "The price is 100 dollars",
    ]
    
    for text in texts:
        has_war = NumberDetector.has_war_context_numbers(text)
        print(f"\nالنص: {text}")
        print(f"سياق حربي: {has_war}")


def example_3_detailed_detection():
    """مثال 3: الكشف التفصيلي"""
    print("\n" + "=" * 80)
    print("مثال 3: الكشف التفصيلي")
    print("=" * 80)
    
    text = "دمّرت 3 طائرات و 5 مسيرات في الضربة، وأصيب 20 جندياً"
    
    result = NumberDetector.detect_numbers(text)
    
    print(f"\nالنص: {text}")
    print(f"\nالنتائج:")
    print(f"  - يحتوي على أرقام: {result['has_numbers']}")
    print(f"  - أرقام أساسية: {result['has_basic_numbers']}")
    print(f"  - سياق حربي: {result['has_war_context']}")
    print(f"  - عدد الأرقام الإنجليزية: {len(result['english_digits'])}")
    print(f"  - عدد الأرقام العربية: {len(result['arabic_digits'])}")
    print(f"  - عدد المطابقات الحربية: {len(result['war_matches'])}")
    
    if result['war_matches']:
        print(f"  - المطابقات الحربية:")
        for match in result['war_matches']:
            print(f"    • {match}")


def example_4_article_processor():
    """مثال 4: استخدام ArticleProcessor"""
    print("\n" + "=" * 80)
    print("مثال 4: استخدام ArticleProcessor")
    print("=" * 80)
    
    articles = [
        {
            'title': 'غارة عسكرية تقتل 50 جندياً',
            'content': 'في عملية عسكرية، قتل 50 جندياً و أصيب 25 آخرين في الغارة الجوية'
        },
        {
            'title': 'أسعار السلع ترتفع',
            'content': 'ارتفعت أسعار السلع بنسبة 100% في السوق'
        },
        {
            'title': 'أخبار عاجلة',
            'content': 'تطورات جديدة في الأحداث الجارية'
        },
    ]
    
    for i, article in enumerate(articles, 1):
        full_text = f"{article['title']} {article['content']}"
        
        has_nums = ArticleProcessor.has_numbers(full_text)
        details = ArticleProcessor.get_number_details(full_text)
        
        print(f"\nالمقالة {i}:")
        print(f"  العنوان: {article['title']}")
        print(f"  يحتوي على أرقام: {has_nums}")
        print(f"  التفاصيل:")
        print(f"    - أرقام أساسية: {details['has_basic_numbers']}")
        print(f"    - سياق حربي: {details['has_war_context']}")
        print(f"    - عدد الأرقام الإنجليزية: {details['english_digits_count']}")
        print(f"    - عدد الأرقام العربية: {details['arabic_digits_count']}")
        print(f"    - عدد المطابقات الحربية: {details['war_matches_count']}")


def example_5_multilingual():
    """مثال 5: دعم متعدد اللغات"""
    print("\n" + "=" * 80)
    print("مثال 5: دعم متعدد اللغات")
    print("=" * 80)
    
    texts = [
        ("عربي", "قتل 50 جندياً في الهجوم"),
        ("إنجليزي", "50 soldiers killed in the attack"),
        ("عبري", "50 חיילים הרוגים בהתקפה"),
        ("مختلط", "قتل 50 soldiers و 25 חיילים"),
    ]
    
    for lang, text in texts:
        result = NumberDetector.detect_numbers(text)
        print(f"\n{lang}:")
        print(f"  النص: {text}")
        print(f"  أرقام: {result['has_numbers']}")
        print(f"  سياق حربي: {result['has_war_context']}")


def example_6_comparison():
    """مثال 6: مقارنة بين الطريقة القديمة والجديدة"""
    print("\n" + "=" * 80)
    print("مثال 6: مقارنة بين الطريقة القديمة والجديدة")
    print("=" * 80)
    
    import re
    
    def old_has_numbers(text):
        """الطريقة القديمة"""
        if not text:
            return False
        has_english = bool(re.search(r'\d', text))
        has_arabic = bool(re.search(r'[٠-٩]', text))
        return has_english or has_arabic
    
    test_cases = [
        "قتل 50 جندياً",
        "السعر 100 دولار",
        "أخبار عاجلة",
    ]
    
    print("\nمقارنة النتائج:")
    print(f"{'النص':<30} {'القديمة':<15} {'الجديدة':<15} {'السياق الحربي':<15}")
    print("-" * 75)
    
    for text in test_cases:
        old_result = old_has_numbers(text)
        new_result = NumberDetector.has_basic_numbers(text)
        war_context = NumberDetector.has_war_context_numbers(text)
        
        print(f"{text:<30} {str(old_result):<15} {str(new_result):<15} {str(war_context):<15}")


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("أمثلة عملية لاستخدام كاشف الأرقام المحسّن")
    print("=" * 80)
    
    example_1_basic_detection()
    example_2_war_context()
    example_3_detailed_detection()
    example_4_article_processor()
    example_5_multilingual()
    example_6_comparison()
    
    print("\n" + "=" * 80)
    print("انتهت الأمثلة")
    print("=" * 80 + "\n")
