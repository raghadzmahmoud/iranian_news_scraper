"""
Background Job لمعالجة الملفات الصوتية
Audio Processing Background Job
"""
import os
from datetime import datetime
from utils.logger import logger
from config.keywords import is_relevant_article, get_matching_keywords, debug_filter
from services.stt_service import STTService


class AudioProcessingJob:
    """معالج الملفات الصوتية في الخلفية"""
    
    def __init__(self):
        """Initialize with STT service"""
        try:
            self.stt_service = STTService()
        except Exception as e:
            logger.error(f"❌ Failed to initialize STT service: {e}")
            self.stt_service = None
    
    @staticmethod
    def process_audio_file(uploaded_file_id: int, s3_url: str, db=None):
        """
        معالجة الملف الصوتي
        
        Pipeline:
        1. تحويل الصوت إلى نص (STT) - بدون فلترة
        2. حفظ الـ transcription في uploaded_files
        3. فحص الصلة بالكلمات المفتاحية
        4. حفظ النتيجة في raw_data (مع الفلترة)
        
        Args:
            uploaded_file_id: معرف الملف المرفوع
            s3_url: رابط الملف على S3
            db: database connection (اختياري - سيتم إنشاؤه إذا لم يُعطَ)
        """
        # إنشاء connection إذا لم تُعطَ
        if db is None:
            from database.connection import DatabaseConnection
            db = DatabaseConnection()
            if not db.connect():
                logger.error("❌ فشل الاتصال بقاعدة البيانات")
                return
        
        try:
            logger.info(f"🎙️ جاري معالجة الملف الصوتي: {uploaded_file_id}")
            
            # Initialize STT service
            try:
                stt_service = STTService()
            except Exception as e:
                logger.error(f"❌ Failed to initialize STT service: {e}")
                AudioProcessingJob._update_status(uploaded_file_id, "failed", db=db)
                return
            
            # ========================================
            # Step 1: تحديث الحالة إلى processing
            # ========================================
            AudioProcessingJob._update_status(uploaded_file_id, "processing", db=db)
            
            # ========================================
            # Step 2: تحويل الصوت لنص (STT) - بدون فلترة
            # ========================================
            logger.info(f"🎤 جاري تحويل الصوت لنص...")
            stt_result = stt_service.transcribe_audio(s3_url)
            
            if not stt_result['success']:
                logger.error(f"❌ فشل تحويل الصوت: {stt_result.get('error')}")
                AudioProcessingJob._update_status(uploaded_file_id, "failed", db=db)
                return
            
            transcription = stt_result['text']
            confidence = stt_result.get('confidence', 0)
            detected_language = stt_result.get('language', 'ar')
            logger.info(f"✅ تم تحويل الصوت: {transcription[:100]}...")
            logger.info(f"   Language: {stt_result.get('language_name', 'Unknown')}")
            logger.info(f"   Confidence: {confidence:.2%}")
            
            # ========================================
            # Step 3: حفظ الـ transcription في uploaded_files (بدون فلترة)
            # ========================================
            logger.info(f"💾 Step 3: حفظ الـ transcription في uploaded_files...")
            AudioProcessingJob._update_status(uploaded_file_id, "transcribed", transcription, db=db)
            logger.info(f"✅ تم حفظ الـ transcription: {uploaded_file_id}")
            
            # ========================================
            # Step 4: فحص الصلة بالكلمات المفتاحية (الفلترة)
            # ========================================
            logger.info(f"🔍 Step 4: جاري فحص الصلة بالكلمات المفتاحية...")
            is_relevant = is_relevant_article("", transcription, language="ar")
            matched_keywords = get_matching_keywords("", transcription, language="ar")
            
            # طباعة تفاصيل الفلترة
            debug_info = debug_filter("", transcription, language="ar")
            logger.info(f"📊 تفاصيل الفلترة:")
            logger.info(f"   - Layer 1 (أساسي): {debug_info['layer_1']}")
            logger.info(f"   - Layer 2 (عمليات): {debug_info['layer_2']}")
            logger.info(f"   - Layer 3 (سياق): {debug_info['layer_3']}")
            
            # ========================================
            # Step 5: حفظ النتيجة في raw_data (مع الفلترة)
            # ========================================
            logger.info(f"💾 Step 5: حفظ النتيجة في raw_data...")
            
            if not is_relevant:
                logger.warning(f"⚠️ الخبر غير ذي صلة - لم يتم العثور على كلمات مفتاحية")
                logger.warning(f"   الكلمات المطابقة: {matched_keywords}")
                # تحديث status في uploaded_files إلى rejected
                AudioProcessingJob._update_status(uploaded_file_id, "rejected", transcription, db=db)
                logger.info(f"✅ تم رفض الخبر (غير ذي صلة): {uploaded_file_id}")
                return
            
            logger.info(f"✅ الخبر ذو صلة - الكلمات المفتاحية: {matched_keywords}")
            
            # إنشاء سجل في raw_data
            logger.info(f"💾 جاري إنشاء سجل في raw_data...")
            raw_data_id = AudioProcessingJob._create_raw_data_record(
                uploaded_file_id=uploaded_file_id,
                media_url=s3_url,
                content=transcription,
                tags=matched_keywords,
                db=db
            )
            
            if not raw_data_id:
                logger.error("❌ فشل إنشاء سجل في raw_data")
                AudioProcessingJob._update_status(uploaded_file_id, "failed", db=db)
                return
            
            logger.info(f"✅ تم إنشاء سجل raw_data برقم: {raw_data_id}")
            
            # تحديث status في uploaded_files إلى completed
            AudioProcessingJob._update_status(uploaded_file_id, "completed", transcription, db=db)
            
            logger.info(f"✅ تمت معالجة الملف الصوتي بنجاح: {uploaded_file_id}")
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الملف الصوتي: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            try:
                AudioProcessingJob._update_status(uploaded_file_id, "failed", db=db)
            except:
                pass
    
    @staticmethod
    def _update_status(uploaded_file_id: int, status: str, transcription: str = None, db=None):
        """
        تحديث حالة الملف
        
        Args:
            uploaded_file_id: معرف الملف
            status: الحالة الجديدة
            transcription: النص المستخرج (اختياري)
            db: database connection
        """
        if db is None:
            logger.error("❌ لم يتم توفير database connection")
            return
            
        try:
            query = """
                UPDATE public.uploaded_files 
                SET status = %s, transcription = %s, processed_at = %s
                WHERE id = %s
            """
            
            db.cursor.execute(query, (
                status,
                transcription,
                datetime.utcnow() if status in ["completed", "rejected", "failed"] else None,
                uploaded_file_id
            ))
            db.conn.commit()
            logger.info(f"✅ تم تحديث حالة الملف: {uploaded_file_id} -> {status}")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث حالة الملف: {e}")
            try:
                db.conn.rollback()
            except:
                pass
    
    @staticmethod
    def _create_raw_data_record(uploaded_file_id: int, media_url: str, content: str, tags: list, db=None) -> int:
        """
        إنشاء سجل في جدول raw_data (بعد الفلترة الناجحة)
        
        Args:
            uploaded_file_id: معرف الملف المرفوع
            media_url: رابط الملف على S3
            content: النص المستخرج
            tags: الكلمات المفتاحية المطابقة
            db: database connection
            
        Returns:
            int: معرف السجل المحفوظ
        """
        if db is None:
            logger.error("❌ لم يتم توفير database connection")
            return None
            
        try:
            tags_str = ",".join(tags) if tags else None
            
            # ✅ استخدم الـ columns الموجودة فقط في raw_data table
            query = """
                INSERT INTO public.raw_data 
                (source_id, source_type_id, url, content, media_url, 
                 fetched_at, is_processed, stt_status, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            db.cursor.execute(query, (
                7,                      # source_id = 7 (audio)
                5,                      # source_type_id = 5 (user_input)
                media_url,              # url
                content,                # content (النص المستخرج)
                media_url,              # media_url
                datetime.utcnow(),      # fetched_at
                False,                  # is_processed
                "completed",            # stt_status
                tags_str                # tags
            ))
            
            result = db.cursor.fetchone()
            db.conn.commit()
            
            if result:
                raw_data_id = result['id'] if isinstance(result, dict) else result[0]
                logger.info(f"✅ تم إنشاء سجل raw_data برقم: {raw_data_id}")
                return raw_data_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء سجل raw_data: {e}")
            try:
                db.conn.rollback()
            except:
                pass
            return None
    
    @staticmethod
    def _update_raw_data(raw_data_id: int, transcription: str, matched_keywords: list, is_relevant: bool, db=None):
        """
        تحديث سجل raw_data
        
        Args:
            raw_data_id: معرف السجل
            transcription: النص المستخرج
            matched_keywords: الكلمات المفتاحية المطابقة
            is_relevant: هل الخبر ذو صلة
            db: database connection
            
        ملاحظة:
            - is_processed يبقى FALSE للملفات الصوتية/الفيديو
            - لأن is_processed مخصص للأخبار من RSS و Telegram
            - الملفات الصوتية/الفيديو لا تحتاج هذا الـ flag
        """
        if db is None:
            logger.error("❌ لم يتم توفير database connection")
            return
            
        try:
            tags_str = ",".join(matched_keywords) if matched_keywords else None
            
            query = """
                UPDATE public.raw_data 
                SET content = %s, tags = %s, 
                    processed_at = %s, stt_status = %s
                WHERE id = %s
            """
            
            db.cursor.execute(query, (
                transcription,
                tags_str,
                datetime.utcnow(),
                "completed",
                raw_data_id
            ))
            db.conn.commit()
            logger.info(f"✅ تم تحديث raw_data: {raw_data_id}")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث raw_data: {e}")
            try:
                db.conn.rollback()
            except:
                pass
