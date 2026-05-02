"""
تطبيق كشف الأرقام المحسّن على آخر 200 خبر من قاعدة البيانات
"""
import psycopg2
from datetime import datetime
from database.connection import db
from utils.number_detector import NumberDetector
from utils.logger import logger


def get_recent_articles(limit: int = 200) -> list:
    """الحصول على آخر N خبر من قاعدة البيانات"""
    try:
        db.ensure_connection()
        
        cursor = db.conn.cursor()
        query = """
            SELECT id, title_original, content_original
            FROM public.raw_news
            ORDER BY fetched_at DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        cursor.close()
        
        logger.info(f"✅ تم جلب {len(results)} خبر من قاعدة البيانات")
        return results
    
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الأخبار: {e}")
        if db.conn:
            db.conn.rollback()
        return []


def update_has_numbers_batch(updates: list) -> int:
    """تحديث حقول has_numbers بشكل دفعي (batch)"""
    try:
        db.ensure_connection()
        
        cursor = db.conn.cursor()
        
        # استخدام executemany لتحديث دفعي
        query = """
            UPDATE public.raw_news 
            SET has_numbers = %s
            WHERE id = %s
        """
        
        cursor.executemany(query, updates)
        db.conn.commit()
        
        updated_count = cursor.rowcount
        cursor.close()
        
        return updated_count
    
    except Exception as e:
        logger.error(f"❌ خطأ في التحديث الدفعي: {e}")
        if db.conn:
            db.conn.rollback()
        return 0


def apply_numbers_detection(limit: int = 200, batch_size: int = 50) -> dict:
    """
    تطبيق كشف الأرقام على آخر N خبر
    
    Args:
        limit: عدد الأخبار (الافتراضي: 200)
        batch_size: حجم الدفعة للتحديث (الافتراضي: 50)
    
    Returns:
        إحصائيات التطبيق
    """
    logger.info(f"🚀 بدء تطبيق كشف الأرقام على آخر {limit} خبر")
    
    # جلب الأخبار
    articles = get_recent_articles(limit)
    
    if not articles:
        logger.warning(f"⚠️  لا توجد أخبار في قاعدة البيانات")
        return {
            'total': 0,
            'processed': 0,
            'with_numbers': 0,
            'without_numbers': 0,
            'errors': 0,
            'updated': 0
        }
    
    stats = {
        'total': len(articles),
        'processed': 0,
        'with_numbers': 0,
        'without_numbers': 0,
        'errors': 0,
        'updated': 0
    }
    
    logger.info(f"📰 معالجة {len(articles)} خبر...")
    
    # معالجة الأخبار على دفعات
    updates = []
    
    for i, article in enumerate(articles, 1):
        try:
            article_id = article[0]
            title = article[1] or ""
            content = article[2] or ""
            
            # دمج العنوان والمحتوى
            full_text = f"{title} {content}"
            
            # كشف الأرقام
            result = NumberDetector.detect_numbers(full_text, use_war_context=True)
            has_numbers = result['has_numbers']
            
            # إضافة إلى قائمة التحديثات
            updates.append((has_numbers, article_id))
            
            # تحديث الإحصائيات
            stats['processed'] += 1
            
            if has_numbers:
                stats['with_numbers'] += 1
            else:
                stats['without_numbers'] += 1
            
            # تنفيذ التحديث الدفعي عند الوصول لحجم الدفعة أو نهاية القائمة
            if len(updates) >= batch_size or i == len(articles):
                updated = update_has_numbers_batch(updates)
                stats['updated'] += updated
                
                logger.info(f"✅ تم تحديث {updated} أخبار (معالج: {i}/{len(articles)})")
                
                updates = []
        
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الخبر {i}: {e}")
            stats['errors'] += 1
    
    # طباعة الملخص
    logger.info(f"\n" + "=" * 80)
    logger.info(f"📊 ملخص التطبيق:")
    logger.info(f"   إجمالي الأخبار: {stats['total']}")
    logger.info(f"   تمت معالجتها: {stats['processed']}")
    logger.info(f"   مع أرقام: {stats['with_numbers']}")
    logger.info(f"   بدون أرقام: {stats['without_numbers']}")
    logger.info(f"   تم التحديث: {stats['updated']}")
    logger.info(f"   أخطاء: {stats['errors']}")
    logger.info(f"=" * 80)
    
    # حساب النسب المئوية
    if stats['processed'] > 0:
        percentage_with_numbers = (stats['with_numbers'] / stats['processed']) * 100
        logger.info(f"📈 نسبة الأخبار مع أرقام: {percentage_with_numbers:.2f}%")
    
    return stats


def verify_update(limit: int = 200) -> dict:
    """
    التحقق من التحديثات
    
    Args:
        limit: عدد الأخبار للتحقق منها
    
    Returns:
        إحصائيات التحقق
    """
    try:
        db.ensure_connection()
        
        cursor = db.conn.cursor()
        
        # عدد الأخبار مع has_numbers = True
        query_true = """
            SELECT COUNT(*) FROM public.raw_news 
            WHERE has_numbers = true
            ORDER BY fetched_at DESC
            LIMIT %s
        """
        cursor.execute(query_true, (limit,))
        count_true = cursor.fetchone()[0]
        
        # عدد الأخبار مع has_numbers = False
        query_false = """
            SELECT COUNT(*) FROM public.raw_news 
            WHERE has_numbers = false
            ORDER BY fetched_at DESC
            LIMIT %s
        """
        cursor.execute(query_false, (limit,))
        count_false = cursor.fetchone()[0]
        
        # عدد الأخبار مع has_numbers = NULL
        query_null = """
            SELECT COUNT(*) FROM public.raw_news 
            WHERE has_numbers IS NULL
            ORDER BY fetched_at DESC
            LIMIT %s
        """
        cursor.execute(query_null, (limit,))
        count_null = cursor.fetchone()[0]
        
        cursor.close()
        
        total = count_true + count_false + count_null
        
        logger.info(f"\n" + "=" * 80)
        logger.info(f"🔍 التحقق من التحديثات:")
        logger.info(f"   مع أرقام (True): {count_true}")
        logger.info(f"   بدون أرقام (False): {count_false}")
        logger.info(f"   لم يتم تحديثها (NULL): {count_null}")
        logger.info(f"   الإجمالي: {total}")
        logger.info(f"=" * 80)
        
        return {
            'with_numbers': count_true,
            'without_numbers': count_false,
            'not_updated': count_null,
            'total': total
        }
    
    except Exception as e:
        logger.error(f"❌ خطأ في التحقق: {e}")
        if db.conn:
            db.conn.rollback()
        return {}


def show_sample_articles(limit: int = 10) -> None:
    """عرض عينة من الأخبار المحدثة"""
    try:
        db.ensure_connection()
        
        cursor = db.conn.cursor()
        query = """
            SELECT id, title_original, has_numbers
            FROM public.raw_news
            WHERE has_numbers IS NOT NULL
            ORDER BY fetched_at DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        cursor.close()
        
        logger.info(f"\n" + "=" * 80)
        logger.info(f"📋 عينة من الأخبار المحدثة:")
        logger.info(f"=" * 80)
        
        for i, (article_id, title, has_numbers) in enumerate(results, 1):
            status = "✅ مع أرقام" if has_numbers else "❌ بدون أرقام"
            logger.info(f"{i}. [{article_id}] {status}")
            logger.info(f"   العنوان: {title[:70]}...")
        
        logger.info(f"=" * 80)
    
    except Exception as e:
        logger.error(f"❌ خطأ في عرض العينة: {e}")


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("تطبيق كشف الأرقام المحسّن على آخر 200 خبر")
    print("=" * 80 + "\n")
    
    # تطبيق كشف الأرقام
    stats = apply_numbers_detection(limit=200, batch_size=50)
    
    # التحقق من التحديثات
    verify_stats = verify_update(limit=200)
    
    # عرض عينة
    show_sample_articles(limit=10)
    
    print("\n✅ انتهى التطبيق بنجاح!\n")
