"""
سكريبت إعداد قاعدة البيانات
Database Setup Script
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
from utils.logger import logger


def setup_database():
    """إعداد قاعدة البيانات بالبيانات المطلوبة"""
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
        
        # 1. إضافة source_type الجديد
        logger.info("📝 جاري إضافة source_type الجديد...")
        cursor.execute("""
            INSERT INTO public.source_type (id, name, description) 
            VALUES (5, 'user_input', 'إدخال من المستخدم')
            ON CONFLICT (id) DO NOTHING
        """)
        conn.commit()
        logger.info("✅ تم إضافة source_type")
        
        # 2. إضافة المصادر الجديدة
        logger.info("📝 جاري إضافة المصادر الجديدة...")
        
        sources = [
            (5, 5, 'voice', True),   # Source ID 5: Voice
            (6, 5, 'video', True),   # Source ID 6: Video
            (7, 5, 'text', True),    # Source ID 7: Text
        ]
        
        for source_id, source_type_id, url, active in sources:
            cursor.execute("""
                INSERT INTO public.sources (id, source_type_id, url, active) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
            """, (source_id, source_type_id, url, active))
        
        conn.commit()
        logger.info("✅ تم إضافة المصادر الجديدة")
        
        # 3. التحقق من البيانات
        logger.info("📊 جاري التحقق من البيانات...")
        
        cursor.execute("SELECT * FROM public.source_type WHERE id = 5")
        source_type = cursor.fetchone()
        if source_type:
            logger.info(f"✅ source_type: {source_type}")
        
        cursor.execute("SELECT * FROM public.sources WHERE source_type_id = 5 ORDER BY id")
        sources = cursor.fetchall()
        if sources:
            logger.info(f"✅ عدد المصادر الجديدة: {len(sources)}")
            for source in sources:
                logger.info(f"   - ID: {source['id']}, URL: {source['url']}, Active: {source['active']}")
        
        cursor.close()
        conn.close()
        logger.info("✅ تم إعداد قاعدة البيانات بنجاح!")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد قاعدة البيانات: {e}")
        return False


if __name__ == "__main__":
    logger.info("🚀 جاري بدء إعداد قاعدة البيانات...")
    success = setup_database()
    if success:
        logger.info("✅ تم الإعداد بنجاح!")
    else:
        logger.error("❌ فشل الإعداد!")
