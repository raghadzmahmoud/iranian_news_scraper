"""
تحديث حالة الأخبار الأجنبية المترجمة
يفحص الأخبار الأجنبية التي تمت ترجمتها ويحدّث processing_status إلى 1
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from config.settings import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
from utils.logger import logger


def update_translated_foreign_news():
    """
    تحديث حالة الأخبار الأجنبية المترجمة
    
    المنطق:
    - البحث عن أخبار أجنبية (language_id != 1)
    - التحقق من وجود ترجمة (title_translated و content_translated ليست NULL)
    - تحديث processing_status إلى 1 (جاهز للنشر)
    """
    conn = None
    cursor = None
    
    try:
        # الاتصال بقاعدة البيانات
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode='require'
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        logger.info("✅ تم الاتصال بقاعدة البيانات")
        
        # البحث عن الأخبار الأجنبية المترجمة
        select_query = """
            SELECT rn.id, rn.url, rn.title_original, rn.content_original,
                   rn.language_id, rn.processing_status,
                   t.title, t.content
            FROM public.raw_news rn
            LEFT JOIN public.translations t ON rn.id = t.raw_news_id
            WHERE rn.language_id != (SELECT id FROM languages WHERE code = 'ar')
            AND t.title IS NOT NULL
            AND t.content IS NOT NULL
            AND rn.processing_status = 0
            ORDER BY rn.fetched_at DESC
        """
        
        cursor.execute(select_query)
        translated_news = cursor.fetchall()
        
        if not translated_news:
            logger.info("⚠️  لا توجد أخبار أجنبية مترجمة بحاجة إلى تحديث")
            return {"updated": 0, "total_found": 0}
        
        logger.info(f"📊 وجدت {len(translated_news)} خبر أجنبي مترجم")
        
        # تحديث processing_status إلى 1 للأخبار المترجمة
        update_query = """
            UPDATE public.raw_news
            SET processing_status = 1
            WHERE id IN (
                SELECT rn.id
                FROM public.raw_news rn
                LEFT JOIN public.translations t ON rn.id = t.raw_news_id
                WHERE rn.language_id != (SELECT id FROM languages WHERE code = 'ar')
                AND t.title IS NOT NULL
                AND t.content IS NOT NULL
                AND rn.processing_status = 0
            )
        """
        
        cursor.execute(update_query)
        updated_count = cursor.rowcount
        conn.commit()
        
        logger.info(f"✅ تم تحديث {updated_count} خبر أجنبي مترجم إلى حالة جاهز للنشر")
        
        # طباعة تفاصيل الأخبار المحدثة
        print("\n" + "="*80)
        print("📰 الأخبار الأجنبية المترجمة المحدثة:")
        print("="*80)
        
        for i, news in enumerate(translated_news, 1):
            print(f"\n{i}. المعرف: {news['id']}")
            print(f"   اللغة: {news['language_id']}")
            print(f"   العنوان الأصلي: {news['title_original'][:60]}...")
            print(f"   العنوان المترجم: {news['title'][:60]}...")
            print(f"   الحالة السابقة: {news['processing_status']} → الحالة الجديدة: 1")
            print(f"   الرابط: {news['url']}")
        
        print("\n" + "="*80)
        
        return {
            "updated": updated_count,
            "total_found": len(translated_news),
            "status": "success"
        }
        
    except psycopg2.Error as e:
        logger.error(f"❌ خطأ في قاعدة البيانات: {e}")
        if conn:
            conn.rollback()
        return {"updated": 0, "error": str(e), "status": "failed"}
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("🔌 تم إغلاق الاتصال بقاعدة البيانات")


if __name__ == "__main__":
    result = update_translated_foreign_news()
    print(f"\n📊 النتيجة النهائية: {result}")
