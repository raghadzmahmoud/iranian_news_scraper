"""
تخزين البيانات الخام في قاعدة البيانات مع الفلترة
"""
from datetime import datetime
from database.connection import db
from models.article import NewsArticle
from config.keywords import is_relevant_article, get_matching_keywords
from utils.logger import logger


def save_raw_data_to_db(articles: list[NewsArticle], source_id: int = 1, filter_enabled: bool = True) -> int:
    """
    حفظ البيانات الخام في جدول raw_data
    فقط الأخبار الجديدة والمتعلقة بإيران والتصعيد العسكري
    
    Args:
        articles: قائمة المقالات
        source_id: معرف المصدر في جدول sources
        filter_enabled: تفعيل الفلترة
    
    Returns:
        عدد المقالات المحفوظة بنجاح
    """
    saved_count = 0
    skipped_count = 0
    filtered_count = 0
    
    for article in articles:
        # التحقق من وجود المقالة بالفعل
        if db.url_exists(article.url):
            logger.info(f"⏭️  تخطي (موجودة): {article.url[:60]}...")
            skipped_count += 1
            continue
        
        # تطبيق الفلترة
        if filter_enabled:
            is_relevant = is_relevant_article(
                article.title,
                article.full_text or article.summary,
                language="he"
            )
            
            if not is_relevant:
                logger.info(f"🚫 فلترة (غير ذات صلة): {article.title[:50]}...")
                filtered_count += 1
                continue
            
            # الحصول على الكلمات المطابقة
            matched_keywords = get_matching_keywords(
                article.title,
                article.full_text or article.summary,
                language="he"
            )
            logger.info(f"✅ مطابقة: {article.title[:50]}... ({len(matched_keywords)} كلمات)")
        
        article_data = {
            "url": article.url,
            "full_text": article.full_text,
            "summary": article.summary,
            "pub_date": article.pub_date,
            "fetched_at": datetime.now().isoformat(),
            "image_url": article.image_url,
            "tags": article.tags,
        }
        
        result = db.insert_raw_data(source_id, article_data)
        if result:
            saved_count += 1
    
    logger.info(f"💾 النتائج: حفظ {saved_count} | تخطي {skipped_count} موجود | فلترة {filtered_count} غير ذات صلة")
    return saved_count
