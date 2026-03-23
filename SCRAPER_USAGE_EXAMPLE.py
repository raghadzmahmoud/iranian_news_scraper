"""
مثال عملي: كيفية استخدام نظام ضمان تفرد الـ URLs في الـ Scrapers
Practical Example: Using Unique URL System in Scrapers
"""

from storage.news_storage import NewsStorage
from utils.article_error_handler import ArticleErrorHandler, ArticleSaveStatus
from utils.logger import logger


def scrape_and_save_articles(scraper, source_id: int):
    """
    سحب المقالات وحفظها مع معالجة الأخطاء
    
    Args:
        scraper: كائن الـ scraper (مثل XScraper أو DBRSSScraper)
        source_id: معرّف المصدر في قاعدة البيانات
    """
    
    logger.info(f"🚀 جاري سحب المقالات من المصدر {source_id}...")
    
    try:
        # سحب المقالات
        articles = scraper.scrape()
        
        if not articles:
            logger.warning("⚠️  لم يتم العثور على أي مقالات")
            return
        
        logger.info(f"📰 تم سحب {len(articles)} مقالة")
        
        # حفظ المقالات
        results = NewsStorage.save_articles_batch(source_id, articles)
        
        # معالجة النتائج
        message = ArticleErrorHandler.handle_batch_results(results)
        logger.info(message)
        
        # إذا كان هناك أخطاء، يمكن تسجيلها للمراجعة
        if results['errors'] > 0:
            logger.warning(f"⚠️  حدثت {results['errors']} أخطاء - قد تحتاج للمراجعة")
        
        # إذا كانت جميع المقالات مكررة
        if results['saved'] == 0 and results['duplicates'] > 0:
            logger.info("ℹ️  جميع المقالات موجودة بالفعل")
        
        return results
    
    except Exception as e:
        logger.error(f"❌ خطأ في سحب وحفظ المقالات: {e}")
        return None


def scrape_and_save_single_article(scraper, source_id: int, article_url: str):
    """
    سحب مقالة واحدة وحفظها مع معالجة الأخطاء
    
    Args:
        scraper: كائن الـ scraper
        source_id: معرّف المصدر
        article_url: رابط المقالة
    """
    
    logger.info(f"🔍 جاري سحب المقالة: {article_url[:60]}")
    
    try:
        # سحب المقالة
        article = scraper.scrape_single(article_url)
        
        if not article:
            logger.warning("⚠️  لم يتم العثور على المقالة")
            return None
        
        # تحضير بيانات المقالة
        article_data = {
            'title': article.title,
            'url': article.url,
            'content': article.full_text or article.summary,
            'language': getattr(article, 'language', 'ar'),
            'published_at': article.pub_date
        }
        
        # حفظ المقالة
        result = NewsStorage.save_article(source_id, article_data)
        
        # معالجة النتيجة
        status = ArticleErrorHandler.handle_save_result(result, article_url)
        
        if status == ArticleSaveStatus.SUCCESS:
            logger.info(f"✅ تم حفظ المقالة برقم: {result}")
            return result
        
        elif status == ArticleSaveStatus.DUPLICATE:
            logger.info(f"⏭️  المقالة موجودة بالفعل - سيتم تخطيها")
            return None
        
        elif status == ArticleSaveStatus.ERROR:
            logger.error(f"❌ حدث خطأ في حفظ المقالة")
            return False
        
    except Exception as e:
        logger.error(f"❌ خطأ في سحب وحفظ المقالة: {e}")
        return False


def batch_scrape_with_retry(scraper, source_id: int, max_retries: int = 3):
    """
    سحب مجموعة من المقالات مع إعادة محاولة الأخطاء
    
    Args:
        scraper: كائن الـ scraper
        source_id: معرّف المصدر
        max_retries: عدد محاولات إعادة المحاولة
    """
    
    logger.info(f"🚀 جاري سحب المقالات (مع إعادة محاولة الأخطاء)...")
    
    for attempt in range(1, max_retries + 1):
        logger.info(f"📍 محاولة {attempt}/{max_retries}")
        
        try:
            articles = scraper.scrape()
            
            if not articles:
                logger.warning("⚠️  لم يتم العثور على أي مقالات")
                return
            
            # حفظ المقالات
            results = NewsStorage.save_articles_batch(source_id, articles)
            
            # معالجة النتائج
            message = ArticleErrorHandler.handle_batch_results(results)
            logger.info(message)
            
            # إذا لم تكن هناك أخطاء، نتوقف
            if results['errors'] == 0:
                logger.info("✅ انتهت العملية بنجاح بدون أخطاء")
                return results
            
            # إذا كانت هناك أخطاء وهذه ليست آخر محاولة
            if attempt < max_retries:
                logger.warning(f"⚠️  سيتم إعادة المحاولة...")
                continue
            else:
                logger.error(f"❌ فشلت جميع المحاولات - {results['errors']} أخطاء متبقية")
                return results
        
        except Exception as e:
            logger.error(f"❌ خطأ في المحاولة {attempt}: {e}")
            
            if attempt < max_retries:
                logger.info(f"⏳ سيتم إعادة المحاولة...")
                continue
            else:
                logger.error(f"❌ فشلت جميع المحاولات")
                return None


# ============================================================================
# أمثلة الاستخدام
# ============================================================================

if __name__ == "__main__":
    from scrapers.x_scraper import XScraper
    from scrapers.db_rss_scraper import DBRSSScraper
    
    # مثال 1: سحب وحفظ مجموعة من المقالات
    print("\n" + "="*60)
    print("مثال 1: سحب وحفظ مجموعة من المقالات")
    print("="*60)
    
    scraper = XScraper()
    results = scrape_and_save_articles(scraper, source_id=1)
    
    # مثال 2: سحب وحفظ مقالة واحدة
    print("\n" + "="*60)
    print("مثال 2: سحب وحفظ مقالة واحدة")
    print("="*60)
    
    article_id = scrape_and_save_single_article(
        scraper,
        source_id=1,
        article_url="https://example.com/news/123"
    )
    
    # مثال 3: سحب مع إعادة محاولة الأخطاء
    print("\n" + "="*60)
    print("مثال 3: سحب مع إعادة محاولة الأخطاء")
    print("="*60)
    
    rss_scraper = DBRSSScraper()
    results = batch_scrape_with_retry(rss_scraper, source_id=2, max_retries=3)
