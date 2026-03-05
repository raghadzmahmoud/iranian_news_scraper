"""
موديول معالجة وفلترة الأخبار
"""
import re
from config.keywords import is_relevant_article, get_matching_keywords
from storage.news_storage import NewsStorage
from utils.logger import logger


class ArticleProcessor:
    """فئة لمعالجة وفلترة الأخبار"""
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        كشف لغة النص
        
        Returns:
            'ar' للعربية، 'he' للعبرية، 'en' للإنجليزية
        """
        if not text:
            return 'ar'  # الافتراضي
        
        # عد الأحرف لكل لغة
        arabic_count = len(re.findall(r'[\u0600-\u06FF]', text))
        hebrew_count = len(re.findall(r'[\u0590-\u05FF]', text))
        english_count = len(re.findall(r'[a-zA-Z]', text))
        
        # إرجاع اللغة الأكثر
        counts = {
            'ar': arabic_count,
            'he': hebrew_count,
            'en': english_count
        }
        
        detected = max(counts, key=counts.get)
        logger.info(f"🌐 اللغة المكتشفة: {detected} (ar:{arabic_count}, he:{hebrew_count}, en:{english_count})")
        
        return detected
    
    @staticmethod
    def has_numbers(text: str) -> bool:
        """
        التحقق من وجود أرقام في النص
        
        Returns:
            True إذا كان هناك أرقام
        """
        if not text:
            return False
        
        # البحث عن أرقام عربية أو إنجليزية
        has_english_numbers = bool(re.search(r'\d', text))
        has_arabic_numbers = bool(re.search(r'[٠-٩]', text))
        
        return has_english_numbers or has_arabic_numbers
    
    @staticmethod
    def filter_and_process(source_id: int, article) -> dict:
        """
        فلترة ومعالجة مقالة واحدة
        
        Args:
            source_id: معرّف المصدر
            article: كائن المقالة (NewsArticle)
        
        Returns:
            قاموس بنتائج المعالجة أو None إذا لم تمر الفلترة
        """
        try:
            # الحصول على النص الكامل
            title = article.title or ""
            content = article.full_text or article.summary or ""
            
            if not title and not content:
                logger.warning(f"⚠️  مقالة بدون عنوان أو محتوى")
                return None
            
            # التحقق من الحد الأدنى للكلمات (300 كلمة)
            word_count = len(content.split())
            
            # كشف اللغة
            language = ArticleProcessor.detect_language(title + " " + content)
            
            # فلترة بناءً على الكلمات المفتاحية
            if not is_relevant_article(title, content, language):
                logger.info(f"⏭️  المقالة لا تطابق الكلمات المفتاحية")
                return None
            
            # الحصول على الكلمات المطابقة
            matching_keywords = get_matching_keywords(title, content, language)
            
            # التحقق من وجود أرقام
            has_numbers_flag = ArticleProcessor.has_numbers(content)
            
            # إذا كانت المقالة أقل من 300 كلمة، ضعها في warning
            if word_count < 300:
                logger.warning(f"⚠️  المقالة أقل من 300 كلمة ({word_count} كلمة) - سيتم حفظها في warning")
                return {
                    'source_id': source_id,
                    'title': title,
                    'content': content,
                    'language': language,
                    'has_numbers': has_numbers_flag,
                    'matching_keywords': matching_keywords,
                    'published_at': article.pub_date,
                    'url': article.url,
                    'is_warning': True,  # علامة أنها مقالة قصيرة
                    'word_count': word_count
                }
            
            logger.info(f"✅ المقالة تمر الفلترة")
            logger.info(f"   الكلمات: {word_count}")
            logger.info(f"   اللغة: {language}")
            logger.info(f"   أرقام: {'نعم' if has_numbers_flag else 'لا'}")
            
            return {
                'source_id': source_id,
                'title': title,
                'content': content,
                'language': language,
                'has_numbers': has_numbers_flag,
                'matching_keywords': matching_keywords,
                'published_at': article.pub_date,
                'url': article.url,
                'is_warning': False,
                'word_count': word_count
            }
        
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة المقالة: {e}")
            return None
    
    @staticmethod
    def process_and_save(source_id: int, articles: list) -> dict:
        """
        معالجة وحفظ مجموعة من المقالات
        
        Args:
            source_id: معرّف المصدر
            articles: قائمة المقالات
        
        Returns:
            إحصائيات المعالجة
        """
        logger.info(f"🔍 بدء معالجة {len(articles)} مقالة من المصدر {source_id}")
        
        stats = {
            'total': len(articles),
            'filtered': 0,
            'saved': 0,
            'skipped': 0,
            'errors': 0,
            'warnings': 0,  # مقالات قصيرة
            'by_language': {},
            'with_numbers': 0
        }
        
        for article in articles:
            try:
                # معالجة المقالة
                processed = ArticleProcessor.filter_and_process(source_id, article)
                
                if not processed:
                    stats['filtered'] += 1
                    continue
                
                # تحديث إحصائيات اللغة
                lang = processed['language']
                if lang not in stats['by_language']:
                    stats['by_language'][lang] = 0
                stats['by_language'][lang] += 1
                
                # تحديث إحصائيات الأرقام
                if processed['has_numbers']:
                    stats['with_numbers'] += 1
                
                # حفظ المقالة
                article_data = {
                    'title': processed['title'],
                    'url': processed['url'],
                    'content': processed['content'],
                    'language': processed['language'],
                    'published_at': processed['published_at'],
                    'has_numbers': processed['has_numbers']
                }
                
                result = NewsStorage.save_article(source_id, article_data)
                
                if result:
                    stats['saved'] += 1
                    logger.info(f"✅ تم حفظ المقالة برقم: {result}")
                    
                    # إذا كانت مقالة قصيرة، سجلها في warning
                    if processed.get('is_warning'):
                        stats['warnings'] += 1
                        logger.warning(f"⚠️  مقالة قصيرة ({processed.get('word_count')} كلمة) محفوظة برقم: {result}")
                else:
                    stats['skipped'] += 1
            
            except Exception as e:
                logger.error(f"❌ خطأ في معالجة المقالة: {e}")
                stats['errors'] += 1
        
        logger.info(f"\n📊 ملخص المعالجة:")
        logger.info(f"   إجمالي: {stats['total']}")
        logger.info(f"   تم الفلترة: {stats['filtered']}")
        logger.info(f"   تم الحفظ: {stats['saved']}")
        logger.info(f"   موجودة: {stats['skipped']}")
        logger.info(f"   أخطاء: {stats['errors']}")
        logger.info(f"   مقالات قصيرة: {stats['warnings']}")
        logger.info(f"   مع أرقام: {stats['with_numbers']}")
        logger.info(f"   حسب اللغة: {stats['by_language']}")
        
        return stats
    
    @staticmethod
    def process_all_sources(sources_articles: dict) -> dict:
        """
        معالجة وحفظ أخبار من عدة مصادر
        
        Args:
            sources_articles: قاموس {source_id: [articles]}
        
        Returns:
            إحصائيات شاملة
        """
        logger.info(f"🚀 بدء معالجة أخبار من {len(sources_articles)} مصدر")
        
        total_stats = {
            'total_sources': len(sources_articles),
            'total_articles': 0,
            'total_filtered': 0,
            'total_saved': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'total_warnings': 0,  # مقالات قصيرة
            'total_with_numbers': 0,
            'by_language': {},
            'by_source': {}
        }
        
        for source_id, articles in sources_articles.items():
            try:
                stats = ArticleProcessor.process_and_save(source_id, articles)
                
                total_stats['total_articles'] += stats['total']
                total_stats['total_filtered'] += stats['filtered']
                total_stats['total_saved'] += stats['saved']
                total_stats['total_skipped'] += stats['skipped']
                total_stats['total_errors'] += stats['errors']
                total_stats['total_warnings'] += stats.get('warnings', 0)
                total_stats['total_with_numbers'] += stats['with_numbers']
                
                # تجميع إحصائيات اللغة
                for lang, count in stats['by_language'].items():
                    if lang not in total_stats['by_language']:
                        total_stats['by_language'][lang] = 0
                    total_stats['by_language'][lang] += count
                
                total_stats['by_source'][source_id] = stats
            
            except Exception as e:
                logger.error(f"❌ خطأ في معالجة المصدر {source_id}: {e}")
        
        logger.info(f"\n✅ انتهت المعالجة الشاملة")
        logger.info(f"   إجمالي المقالات: {total_stats['total_articles']}")
        logger.info(f"   تم الفلترة: {total_stats['total_filtered']}")
        logger.info(f"   تم الحفظ: {total_stats['total_saved']}")
        logger.info(f"   مقالات قصيرة: {total_stats['total_warnings']}")
        logger.info(f"   مع أرقام: {total_stats['total_with_numbers']}")
        logger.info(f"   حسب اللغة: {total_stats['by_language']}")
        
        return total_stats
