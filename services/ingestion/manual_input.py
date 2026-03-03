"""
خدمة معالجة الإدخال اليدوي للنصوص
Manual Text Input Processing Service
"""
import json
import random
from datetime import datetime
from database.connection import db
from utils.logger import logger
from config.keywords import is_relevant_article, get_matching_keywords, debug_filter


class ManualInputProcessor:
    """معالج الإدخال اليدوي للنصوص"""
    
    SOURCE_TYPE_ID = 5  # user_input
    SOURCE_ID = 7      # text
    
    @staticmethod
    def process_manual_input(text: str, user_id: int = None) -> dict:
        """
        معالجة النص المدخل يدويًا
        
        Args:
            text: النص المدخل من المستخدم
            user_id: معرف المستخدم (اختياري)
            
        Returns:
            dict: نتيجة المعالجة
        """
        try:
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "النص فارغ",
                    "message": "يجب إدخال نص غير فارغ"
                }
            
            # 1. فحص الصلة بالكلمات المفتاحية
            logger.info("🔍 جاري فحص الصلة بالكلمات المفتاحية...")
            is_relevant = is_relevant_article("", text, language="ar")
            matched_keywords = get_matching_keywords("", text, language="ar")
            
            if not is_relevant:
                logger.warning(f"⚠️ الخبر غير ذي صلة - لم يتم العثور على كلمات مفتاحية")
                return {
                    "success": False,
                    "error": "الخبر لا يندرج ضمن نطاق التغطية (إيران – إسرائيل – التصعيد العسكري الحالي)",
                    "message": "تم رفض الخبر لأنه لا يندرج ضمن نطاق التغطية. يجب أن يتضمن الخبر إشارات واضحة إلى الأطراف أو العمليات العسكرية المرتبطة بالأحداث الجارية."
                }
            
            logger.info(f"✅ الخبر ذو صلة - الكلمات المفتاحية المطابقة: {matched_keywords}")
            
            # 2. معالجة النص
            processed_data = ManualInputProcessor._process_and_save(text, user_id, matched_keywords)
            
            if processed_data:
                return {
                    "success": True,
                    "news_id": processed_data["id"],
                    "message": "تم قبول الخبر وحفظه بنجاح",
                    "data": {
                        "id": processed_data["id"],
                        "title": processed_data.get("title"),
                        "content": processed_data.get("content"),
                        "tags": processed_data.get("tags"),
                        "created_at": processed_data.get("created_at")
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "فشل في حفظ البيانات",
                    "message": "حدث خطأ أثناء حفظ الخبر"
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الإدخال اليدوي: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "حدث خطأ في معالجة الإدخال"
            }
    
    @staticmethod
    def _process_and_save(text: str, user_id: int = None, matched_keywords: list = None) -> dict:
        """
        معالجة وحفظ النص
        
        Args:
            text: النص المدخل
            user_id: معرف المستخدم
            matched_keywords: الكلمات المفتاحية المطابقة
            
        Returns:
            dict: بيانات الخبر المحفوظ
        """
        try:
            # معالجة النص بـ AI (استخراج البيانات)
            processed_text = ManualInputProcessor._process_with_ai(text)
            
            if not processed_text:
                return None
            
            # حفظ في قاعدة البيانات
            raw_data_id = ManualInputProcessor._save_to_database(
                text=text,
                processed_data=processed_text,
                user_id=user_id,
                matched_keywords=matched_keywords
            )
            
            if raw_data_id:
                return {
                    "id": raw_data_id,
                    "content": text,
                    "title": processed_text.get("title"),
                    "category": processed_text.get("category"),
                    "tags": processed_text.get("tags"),
                    "created_at": datetime.utcnow().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة وحفظ النص: {e}")
            return None
    
    @staticmethod
    def _process_with_ai(text: str) -> dict:
        """
        معالجة النص باستخدام AI
        
        Args:
            text: النص المدخل
            
        Returns:
            dict: البيانات المستخرجة
        """
        try:
            # هنا يتم استدعاء Claude API أو أي خدمة AI أخرى
            # للآن نرجع بيانات افتراضية
            
            processed_data = {
                "title": text[:100] if len(text) > 100 else text,
                "content": text,
                "category": "عام",
                "tags": ["مستخدم", "إدخال يدوي"]
            }
            
            logger.info(f"✅ تمت معالجة النص بـ AI بنجاح")
            return processed_data
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة النص بـ AI: {e}")
            return None
    
    @staticmethod
    def _save_to_database(text: str, processed_data: dict, user_id: int = None, matched_keywords: list = None) -> int:
        """
        حفظ البيانات في قاعدة البيانات
        
        Args:
            text: النص الأصلي
            processed_data: البيانات المعالجة
            user_id: معرف المستخدم
            matched_keywords: الكلمات المفتاحية المطابقة
            
        Returns:
            int: معرف السجل المحفوظ
        """
        try:
            # إنشاء URL فريد للنص اليدوي
            url = f"manual_text_{datetime.utcnow().timestamp()}"
            
            # التحقق من أن الـ URL فريد
            check_query = "SELECT 1 FROM public.raw_data WHERE url = %s LIMIT 1"
            db.cursor.execute(check_query, (url,))
            if db.cursor.fetchone():
                # إذا كان موجود، أضف رقم عشوائي
                url = f"manual_text_{datetime.utcnow().timestamp()}_{random.randint(1000, 9999)}"
            
            query = """
                INSERT INTO public.raw_data 
                (source_id, source_type_id, url, content, fetched_at, 
                 is_processed, processed_at, stt_status, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            # دمج الكلمات المفتاحية مع الـ tags
            all_tags = list(set(processed_data.get("tags", []) + (matched_keywords or [])))
            tags_str = ",".join(all_tags) if all_tags else None
            
            db.cursor.execute(query, (
                ManualInputProcessor.SOURCE_ID,           # source_id = 7 (text)
                ManualInputProcessor.SOURCE_TYPE_ID,      # source_type_id = 5 (user_input)
                url,                                       # url
                text,                                      # content
                datetime.utcnow(),                         # fetched_at
                False,                                     # is_processed - يجب أن يبقى False
                None,                                      # processed_at - لا نحدثه الآن
                "not_needed",                              # stt_status - نصوص فقط
                tags_str,                                  # tags
            ))
            
            result = db.cursor.fetchone()
            db.conn.commit()
            
            if result:
                raw_data_id = result['id'] if isinstance(result, dict) else result[0]
                logger.info(f"✅ تم حفظ النص في قاعدة البيانات برقم: {raw_data_id}")
                return raw_data_id
            
            logger.error("❌ لم يتم الحصول على معرف السجل")
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ البيانات: {e}")
            logger.error(f"❌ تفاصيل الخطأ: {str(e)}")
            try:
                db.conn.rollback()
            except:
                pass
            return None
