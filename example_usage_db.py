"""
أمثلة استخدام نظام السحب والمعالجة والتخزين والقراءة
"""
from scrapers.db_rss_scraper import smart_scrape_and_save, scrape_all_sources_and_save
from storage.news_reader import NewsReader


def example_1_scrape_filter_save_single():
    """مثال 1: سحب من مصدر واحد مع الفلترة والحفظ"""
    print("\n" + "="*60)
    print("مثال 1: سحب + فلترة + حفظ من مصدر واحد")
    print("="*60)
    
    stats = smart_scrape_and_save(source_id=1, max_items=5)
    
    print(f"\n📊 النتائج:")
    print(f"   المصدر: {stats['source_id']}")
    print(f"   تم السحب: {stats['total_scraped']}")
    print(f"   تم الفلترة: {stats['filtered']}")
    print(f"   تم الحفظ: {stats['saved']}")
    print(f"   موجودة: {stats['skipped']}")
    print(f"   مع أرقام: {stats['with_numbers']}")
    print(f"   حسب اللغة: {stats['by_language']}")


def example_2_scrape_filter_save_all():
    """مثال 2: سحب من جميع المصادر مع الفلترة والحفظ"""
    print("\n" + "="*60)
    print("مثال 2: سحب + فلترة + حفظ من جميع المصادر")
    print("="*60)
    
    stats = scrape_all_sources_and_save(max_items=3)
    
    print(f"\n📊 النتائج الشاملة:")
    print(f"   إجمالي المصادر: {stats['total_sources']}")
    print(f"   إجمالي المقالات: {stats['total_scraped']}")
    print(f"   تم الفلترة: {stats['total_filtered']}")
    print(f"   تم الحفظ: {stats['total_saved']}")
    print(f"   موجودة: {stats['total_skipped']}")
    print(f"   مع أرقام: {stats['total_with_numbers']}")
    print(f"   حسب اللغة: {stats['by_language']}")


def example_3_read_articles():
    """مثال 3: قراءة الأخبار المحفوظة"""
    print("\n" + "="*60)
    print("مثال 3: قراءة الأخبار المحفوظة")
    print("="*60)
    
    articles = NewsReader.get_by_source(source_id=1, limit=3)
    
    print(f"\n📰 أخبار من المصدر 1 ({len(articles)}):")
    for article in articles:
        print(f"\n   العنوان: {article['title'][:60]}")
        print(f"   اللغة: {article['language']}")
        print(f"   التاريخ: {article['published_at']}")


def example_4_read_unprocessed():
    """مثال 4: قراءة الأخبار غير المعالجة"""
    print("\n" + "="*60)
    print("مثال 4: قراءة الأخبار غير المعالجة")
    print("="*60)
    
    articles = NewsReader.get_unprocessed(limit=5)
    
    print(f"\n📰 أخبار غير معالجة ({len(articles)}):")
    for article in articles:
        print(f"\n   ID: {article['id']}")
        print(f"   العنوان: {article['title'][:60]}")
        print(f"   المصدر: {article['source_name']}")
        print(f"   اللغة: {article['language']}")


def example_5_read_by_language():
    """مثال 5: قراءة الأخبار بلغة معينة"""
    print("\n" + "="*60)
    print("مثال 5: قراءة الأخبار بلغة معينة")
    print("="*60)
    
    articles = NewsReader.get_by_language(language_code='ar', limit=3)
    
    print(f"\n📰 أخبار عربية ({len(articles)}):")
    for article in articles:
        print(f"\n   العنوان: {article['title'][:60]}")
        print(f"   المصدر: {article['source_name']}")


def example_6_search():
    """مثال 6: البحث عن أخبار"""
    print("\n" + "="*60)
    print("مثال 6: البحث عن أخبار")
    print("="*60)
    
    articles = NewsReader.search(query_text='إسرائيل', limit=5)
    
    print(f"\n🔍 نتائج البحث عن 'إسرائيل' ({len(articles)}):")
    for article in articles:
        print(f"\n   العنوان: {article['title'][:60]}")
        print(f"   المصدر: {article['source_name']}")


def example_7_stats():
    """مثال 7: الحصول على الإحصائيات"""
    print("\n" + "="*60)
    print("مثال 7: الحصول على الإحصائيات")
    print("="*60)
    
    stats = NewsReader.get_stats()
    
    print(f"\n📊 الإحصائيات:")
    print(f"   إجمالي الأخبار: {stats['total']}")
    print(f"   غير معالجة: {stats['unprocessed']}")
    
    print(f"\n   حسب اللغة:")
    for lang, count in stats['by_language'].items():
        print(f"      {lang}: {count}")
    
    print(f"\n   حسب المصدر:")
    for source, count in stats['by_source'].items():
        print(f"      {source}: {count}")


if __name__ == "__main__":
    print("\n🎯 أمثلة استخدام نظام السحب والمعالجة والتخزين والقراءة")
    
    # تشغيل الأمثلة
    # example_1_scrape_filter_save_single()
    # example_2_scrape_filter_save_all()
    # example_3_read_articles()
    # example_4_read_unprocessed()
    # example_5_read_by_language()
    # example_6_search()
    # example_7_stats()
    
    print("\n✅ الأمثلة جاهزة للاستخدام")
    print("قم بإلغاء التعليق عن الأمثلة التي تريد تشغيلها")
