"""
اختبار نظام ضمان تفرد الـ URLs
Test Unique URL System
"""

import sys
from datetime import datetime
from storage.news_storage import NewsStorage
from utils.article_error_handler import ArticleErrorHandler, ArticleSaveStatus
from utils.logger import logger


def test_single_article_save():
    """اختبار حفظ مقالة واحدة"""
    print("\n" + "="*60)
    print("اختبار 1: حفظ مقالة واحدة")
    print("="*60)
    
    article_data = {
        'title': 'خبر اختبار 1',
        'url': f'https://example.com/test/{datetime.now().timestamp()}',
        'content': 'محتوى الخبر الاختباري',
        'language': 'ar',
        'published_at': datetime.now().isoformat()
    }
    
    result = NewsStorage.save_article(source_id=1, article_data=article_data)
    status = ArticleErrorHandler.handle_save_result(result, article_data['url'])
    
    assert status == ArticleSaveStatus.SUCCESS, f"❌ فشل الاختبار: {status.value}"
    print(f"✅ نجح الاختبار - معرّف المقالة: {result}")
    
    return article_data['url']


def test_duplicate_url():
    """اختبار محاولة إدراج نفس URL مرتين"""
    print("\n" + "="*60)
    print("اختبار 2: محاولة إدراج نفس URL مرتين")
    print("="*60)
    
    article_data = {
        'title': 'خبر اختبار 2',
        'url': f'https://example.com/test/duplicate/{datetime.now().timestamp()}',
        'content': 'محتوى الخبر الاختباري',
        'language': 'ar',
        'published_at': datetime.now().isoformat()
    }
    
    # الإدراج الأول
    result1 = NewsStorage.save_article(source_id=1, article_data=article_data)
    status1 = ArticleErrorHandler.handle_save_result(result1, article_data['url'])
    
    assert status1 == ArticleSaveStatus.SUCCESS, f"❌ فشل الإدراج الأول: {status1.value}"
    print(f"✅ الإدراج الأول نجح - معرّف المقالة: {result1}")
    
    # الإدراج الثاني (يجب أن يكون مكرراً)
    result2 = NewsStorage.save_article(source_id=1, article_data=article_data)
    status2 = ArticleErrorHandler.handle_save_result(result2, article_data['url'])
    
    assert status2 == ArticleSaveStatus.DUPLICATE, f"❌ فشل الاختبار: {status2.value}"
    print(f"✅ نجح الاختبار - تم اكتشاف المقالة المكررة")


def test_batch_save():
    """اختبار حفظ مجموعة من المقالات"""
    print("\n" + "="*60)
    print("اختبار 3: حفظ مجموعة من المقالات")
    print("="*60)
    
    # إنشاء مقالات اختبارية
    articles_data = [
        {
            'title': f'خبر اختبار {i}',
            'url': f'https://example.com/test/batch/{datetime.now().timestamp()}/{i}',
            'content': f'محتوى الخبر الاختباري {i}',
            'language': 'ar',
            'published_at': datetime.now().isoformat()
        }
        for i in range(3)
    ]
    
    # حفظ المقالات
    saved_count = 0
    for article_data in articles_data:
        result = NewsStorage.save_article(source_id=1, article_data=article_data)
        status = ArticleErrorHandler.handle_save_result(result, article_data['url'])
        
        if status == ArticleSaveStatus.SUCCESS:
            saved_count += 1
    
    assert saved_count == 3, f"❌ فشل الاختبار: تم حفظ {saved_count} مقالات فقط"
    print(f"✅ نجح الاختبار - تم حفظ {saved_count} مقالات")


def test_batch_with_duplicates():
    """اختبار حفظ مجموعة تحتوي على مقالات مكررة"""
    print("\n" + "="*60)
    print("اختبار 4: حفظ مجموعة تحتوي على مقالات مكررة")
    print("="*60)
    
    base_url = f'https://example.com/test/batch-dup/{datetime.now().timestamp()}'
    
    # إنشاء مقالات (بعضها مكرر)
    articles_data = [
        {
            'title': 'خبر اختبار 1',
            'url': f'{base_url}/1',
            'content': 'محتوى الخبر الاختباري 1',
            'language': 'ar',
            'published_at': datetime.now().isoformat()
        },
        {
            'title': 'خبر اختبار 2',
            'url': f'{base_url}/2',
            'content': 'محتوى الخبر الاختباري 2',
            'language': 'ar',
            'published_at': datetime.now().isoformat()
        },
        {
            'title': 'خبر اختبار 1 (مكرر)',
            'url': f'{base_url}/1',  # نفس URL
            'content': 'محتوى مختلف',
            'language': 'ar',
            'published_at': datetime.now().isoformat()
        },
    ]
    
    # حفظ المقالات
    saved_count = 0
    duplicate_count = 0
    
    for article_data in articles_data:
        result = NewsStorage.save_article(source_id=1, article_data=article_data)
        status = ArticleErrorHandler.handle_save_result(result, article_data['url'])
        
        if status == ArticleSaveStatus.SUCCESS:
            saved_count += 1
        elif status == ArticleSaveStatus.DUPLICATE:
            duplicate_count += 1
    
    assert saved_count == 2, f"❌ فشل الاختبار: تم حفظ {saved_count} مقالات فقط"
    assert duplicate_count == 1, f"❌ فشل الاختبار: تم اكتشاف {duplicate_count} مقالات مكررة فقط"
    print(f"✅ نجح الاختبار - تم حفظ {saved_count} مقالات واكتشاف {duplicate_count} مقالات مكررة")


def test_error_handler():
    """اختبار معالج الأخطاء"""
    print("\n" + "="*60)
    print("اختبار 5: معالج الأخطاء")
    print("="*60)
    
    # اختبار معالجة النتائج
    results = {
        'saved': 5,
        'duplicates': 2,
        'errors': 1
    }
    
    message = ArticleErrorHandler.handle_batch_results(results)
    
    assert 'saved' in message.lower() or '5' in message, "❌ فشل الاختبار: الرسالة لا تحتوي على عدد المقالات المحفوظة"
    print(f"✅ نجح الاختبار - معالج الأخطاء يعمل بشكل صحيح")


def test_should_retry():
    """اختبار تحديد ما إذا كان يجب إعادة المحاولة"""
    print("\n" + "="*60)
    print("اختبار 6: تحديد ما إذا كان يجب إعادة المحاولة")
    print("="*60)
    
    # يجب إعادة محاولة الأخطاء
    assert ArticleErrorHandler.should_retry(ArticleSaveStatus.ERROR) == True, "❌ فشل الاختبار"
    
    # لا يجب إعادة محاولة المقالات المكررة
    assert ArticleErrorHandler.should_retry(ArticleSaveStatus.DUPLICATE) == False, "❌ فشل الاختبار"
    
    # لا يجب إعادة محاولة المقالات الناجحة
    assert ArticleErrorHandler.should_retry(ArticleSaveStatus.SUCCESS) == False, "❌ فشل الاختبار"
    
    print(f"✅ نجح الاختبار - منطق إعادة المحاولة صحيح")


def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("\n" + "="*60)
    print("🧪 تشغيل اختبارات نظام ضمان تفرد الـ URLs")
    print("="*60)
    
    tests = [
        ("حفظ مقالة واحدة", test_single_article_save),
        ("محاولة إدراج نفس URL مرتين", test_duplicate_url),
        ("حفظ مجموعة من المقالات", test_batch_save),
        ("حفظ مجموعة تحتوي على مقالات مكررة", test_batch_with_duplicates),
        ("معالج الأخطاء", test_error_handler),
        ("تحديد ما إذا كان يجب إعادة المحاولة", test_should_retry),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ فشل الاختبار: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ خطأ في الاختبار: {e}")
            failed += 1
    
    # ملخص النتائج
    print("\n" + "="*60)
    print("📊 ملخص النتائج")
    print("="*60)
    print(f"✅ نجح: {passed}")
    print(f"❌ فشل: {failed}")
    print(f"📈 الإجمالي: {passed + failed}")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
