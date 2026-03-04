"""
موديول قراءة الأخبار من قاعدة البيانات
"""
from database.connection import db
from utils.logger import logger


class NewsReader:
    """فئة لقراءة الأخبار من قاعدة البيانات"""
    
    @staticmethod
    def get_by_id(article_id: int) -> dict:
        """الحصول على مقالة بـ ID"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            query = """
                SELECT rn.id, rn.source_id, rn.url, rn.title_original, rn.content_original,
                       l.code as language, rn.published_at, rn.fetched_at, rn.processing_status,
                       s.name as source_name
                FROM public.raw_news rn
                JOIN public.languages l ON rn.language_id = l.id
                JOIN public.sources s ON rn.source_id = s.id
                WHERE rn.id = %s
            """
            
            cursor.execute(query, (article_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'id': result[0],
                    'source_id': result[1],
                    'url': result[2],
                    'title': result[3],
                    'content': result[4],
                    'language': result[5],
                    'published_at': result[6],
                    'fetched_at': result[7],
                    'processing_status': result[8],
                    'source_name': result[9]
                }
            
            return None
        
        except Exception as e:
            logger.error(f"❌ خطأ في جلب المقالة: {e}")
            if db.conn:
                db.conn.rollback()
            return None
    
    @staticmethod
    def get_by_source(source_id: int, limit: int = 10, offset: int = 0) -> list:
        """الحصول على أخبار من مصدر معين"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            query = """
                SELECT rn.id, rn.source_id, rn.url, rn.title_original, rn.content_original,
                       l.code as language, rn.published_at, rn.fetched_at, rn.processing_status
                FROM public.raw_news rn
                JOIN public.languages l ON rn.language_id = l.id
                WHERE rn.source_id = %s
                ORDER BY rn.fetched_at DESC
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, (source_id, limit, offset))
            results = cursor.fetchall()
            cursor.close()
            
            articles = []
            for row in results:
                articles.append({
                    'id': row[0],
                    'source_id': row[1],
                    'url': row[2],
                    'title': row[3],
                    'content': row[4],
                    'language': row[5],
                    'published_at': row[6],
                    'fetched_at': row[7],
                    'processing_status': row[8]
                })
            
            return articles
        
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الأخبار: {e}")
            if db.conn:
                db.conn.rollback()
            return []
    
    @staticmethod
    def get_unprocessed(limit: int = 100, offset: int = 0) -> list:
        """الحصول على أخبار لم تتم معالجتها"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            query = """
                SELECT rn.id, rn.source_id, rn.url, rn.title_original, rn.content_original,
                       l.code as language, rn.published_at, rn.fetched_at,
                       s.name as source_name
                FROM public.raw_news rn
                JOIN public.languages l ON rn.language_id = l.id
                JOIN public.sources s ON rn.source_id = s.id
                WHERE rn.processing_status = 0
                ORDER BY rn.fetched_at DESC
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, (limit, offset))
            results = cursor.fetchall()
            cursor.close()
            
            articles = []
            for row in results:
                articles.append({
                    'id': row[0],
                    'source_id': row[1],
                    'url': row[2],
                    'title': row[3],
                    'content': row[4],
                    'language': row[5],
                    'published_at': row[6],
                    'fetched_at': row[7],
                    'source_name': row[8]
                })
            
            return articles
        
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الأخبار غير المعالجة: {e}")
            if db.conn:
                db.conn.rollback()
            return []
    
    @staticmethod
    def get_by_language(language_code: str, limit: int = 10, offset: int = 0) -> list:
        """الحصول على أخبار بلغة معينة"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            query = """
                SELECT rn.id, rn.source_id, rn.url, rn.title_original, rn.content_original,
                       l.code as language, rn.published_at, rn.fetched_at,
                       s.name as source_name
                FROM public.raw_news rn
                JOIN public.languages l ON rn.language_id = l.id
                JOIN public.sources s ON rn.source_id = s.id
                WHERE l.code = %s
                ORDER BY rn.fetched_at DESC
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, (language_code, limit, offset))
            results = cursor.fetchall()
            cursor.close()
            
            articles = []
            for row in results:
                articles.append({
                    'id': row[0],
                    'source_id': row[1],
                    'url': row[2],
                    'title': row[3],
                    'content': row[4],
                    'language': row[5],
                    'published_at': row[6],
                    'fetched_at': row[7],
                    'source_name': row[8]
                })
            
            return articles
        
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الأخبار: {e}")
            return []
    
    @staticmethod
    def search(query_text: str, limit: int = 10) -> list:
        """البحث عن أخبار"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            query = """
                SELECT rn.id, rn.source_id, rn.url, rn.title_original, rn.content_original,
                       l.code as language, rn.published_at, rn.fetched_at,
                       s.name as source_name
                FROM public.raw_news rn
                JOIN public.languages l ON rn.language_id = l.id
                JOIN public.sources s ON rn.source_id = s.id
                WHERE rn.title_original ILIKE %s OR rn.content_original ILIKE %s
                ORDER BY rn.fetched_at DESC
                LIMIT %s
            """
            
            search_pattern = f"%{query_text}%"
            cursor.execute(query, (search_pattern, search_pattern, limit))
            results = cursor.fetchall()
            cursor.close()
            
            articles = []
            for row in results:
                articles.append({
                    'id': row[0],
                    'source_id': row[1],
                    'url': row[2],
                    'title': row[3],
                    'content': row[4],
                    'language': row[5],
                    'published_at': row[6],
                    'fetched_at': row[7],
                    'source_name': row[8]
                })
            
            return articles
        
        except Exception as e:
            logger.error(f"❌ خطأ في البحث: {e}")
            return []
    
    @staticmethod
    def get_stats() -> dict:
        """الحصول على إحصائيات الأخبار"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            
            # إجمالي الأخبار
            cursor.execute("SELECT COUNT(*) FROM public.raw_news")
            total = cursor.fetchone()[0]
            
            # الأخبار غير المعالجة
            cursor.execute("SELECT COUNT(*) FROM public.raw_news WHERE processing_status = 0")
            unprocessed = cursor.fetchone()[0]
            
            # الأخبار حسب اللغة
            cursor.execute("""
                SELECT l.code, COUNT(rn.id)
                FROM public.raw_news rn
                JOIN public.languages l ON rn.language_id = l.id
                GROUP BY l.code
            """)
            by_language = dict(cursor.fetchall())
            
            # الأخبار حسب المصدر
            cursor.execute("""
                SELECT s.name, COUNT(rn.id)
                FROM public.raw_news rn
                JOIN public.sources s ON rn.source_id = s.id
                GROUP BY s.name
                ORDER BY COUNT(rn.id) DESC
            """)
            by_source = dict(cursor.fetchall())
            
            cursor.close()
            
            return {
                'total': total,
                'unprocessed': unprocessed,
                'by_language': by_language,
                'by_source': by_source
            }
        
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الإحصائيات: {e}")
            if db.conn:
                db.conn.rollback()
            return {}
