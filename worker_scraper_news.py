"""
Worker لسحب الأخبار من RSS مع الفلترة والتخزين في raw_news
"""
import time
from scrapers.db_rss_scraper import scrape_all_sources_and_save
from config.settings import SCRAPER_MAX_ITEMS, DELAY_BETWEEN_REQUESTS
from utils.logger import logger


def scrape_news_worker():
    """
    Worker يقوم بـ:
    1. سحب من جميع المصادر (SCRAPER_MAX_ITEMS من كل مصدر)
    2. فلترة بناءً على الكلمات المفتاحية
    3. كشف اللغة
    4. التحقق من وجود أرقام
    5. تخزين في raw_news مع processing_status = 0
    """
    logger.info("="*70)
    logger.info("🚀 بدء Worker سحب الأخبار")
    logger.info("="*70)
    logger.info(f"📊 الإعدادات:")
    logger.info(f"   عدد المقالات من كل مصدر: {SCRAPER_MAX_ITEMS}")
    logger.info(f"   التأخير بين الطلبات: {DELAY_BETWEEN_REQUESTS} ثانية")
    
    try:
        # السحب والمعالجة والتخزين
        stats = scrape_all_sources_and_save(max_items=SCRAPER_MAX_ITEMS)
        
        # طباعة النتائج
        logger.info("\n" + "="*70)
        logger.info("📊 ملخص النتائج")
        logger.info("="*70)
        
        logger.info(f"\n📈 الإحصائيات الشاملة:")
        logger.info(f"   إجمالي المصادر: {stats.get('total_sources', 0)}")
        logger.info(f"   إجمالي المقالات المسحوبة: {stats.get('total_scraped', 0)}")
        logger.info(f"   تم الفلترة (لم تمر): {stats.get('total_filtered', 0)}")
        logger.info(f"   تم الحفظ: {stats.get('total_saved', 0)}")
        logger.info(f"   موجودة بالفعل: {stats.get('total_skipped', 0)}")
        logger.info(f"   أخطاء: {stats.get('total_errors', 0)}")
        
        logger.info(f"\n🔢 المقالات مع أرقام: {stats.get('total_with_numbers', 0)}")
        
        logger.info(f"\n🌐 توزيع حسب اللغة:")
        for lang, count in stats.get('by_language', {}).items():
            lang_name = {
                'ar': 'عربي',
                'en': 'إنجليزي',
                'he': 'عبري'
            }.get(lang, lang)
            logger.info(f"   {lang_name}: {count}")
        
        logger.info(f"\n📡 توزيع حسب المصدر:")
        for source_id, source_stats in stats.get('by_source', {}).items():
            logger.info(f"   المصدر {source_id}:")
            logger.info(f"      مسحوب: {source_stats.get('total_scraped', 0)}")
            logger.info(f"      محفوظ: {source_stats.get('saved', 0)}")
            logger.info(f"      مع أرقام: {source_stats.get('with_numbers', 0)}")
        
        logger.info("\n" + "="*70)
        logger.info("✅ انتهى Worker بنجاح")
        logger.info("="*70)
        
        return stats
    
    except Exception as e:
        logger.error(f"❌ خطأ في Worker: {e}")
        logger.error("="*70)
        return None


if __name__ == "__main__":
    logger.info(f"⏰ بدء Worker في: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # تشغيل Worker
    result = scrape_news_worker()
    
    if result:
        logger.info(f"✅ Worker انتهى بنجاح")
    else:
        logger.error(f"❌ Worker فشل")
    
    logger.info(f"⏰ انتهى Worker في: {time.strftime('%Y-%m-%d %H:%M:%S')}")
