"""
Background Job لمعالجة الملفات الفيديو
Video Processing Background Job
"""
import os
from datetime import datetime
from database.connection import DatabaseConnection
from utils.logger import logger
from config.keywords import is_relevant_article, get_matching_keywords, debug_filter
from services.stt_service import STTService


class VideoProcessingJob:
    """معالج الملفات الفيديو في الخلفية"""
    
    @staticmethod
    def process_video_file(uploaded_file_id: int, s3_url: str, db=None):
        """
        معالجة الملف الفيديو
        
        Flow:
        1. تحديث الحالة إلى processing
        2. استخراج الصوت من الفيديو
        3. تحويل الصوت لنص (STT)
        4. حفظ النص في transcripts (في uploaded_files)
        5. فحص الصلة بالكلمات المفتاحية
        6. إذا تمام: إنشاء صف في raw_data
        7. تحديث حالة الملف
        
        Args:
            uploaded_file_id: معرف الملف المرفوع
            s3_url: رابط الملف على S3
            db: database connection (اختياري - سيتم إنشاؤه إذا لم يُعطَ)
        """
        # إنشاء connection إذا لم تُعطَ
        if db is None:
            db = DatabaseConnection()
            if not db.connect():
                logger.error("❌ فشل الاتصال بقاعدة البيانات")
                return
        
        try:
            logger.info(f"🎬 جاري معالجة الملف الفيديو: {uploaded_file_id}")
            
            # Initialize STT service
            try:
                stt_service = STTService()
            except Exception as e:
                logger.error(f"❌ Failed to initialize STT service: {e}")
                VideoProcessingJob._update_status(uploaded_file_id, "failed", db)
                return
            
            # 1. تحديث الحالة إلى processing
            VideoProcessingJob._update_status(uploaded_file_id, "processing", db=db)
            
            # 2. استخراج الصوت من الفيديو
            logger.info(f"🎵 جاري استخراج الصوت من الفيديو...")
            audio_s3_url = VideoProcessingJob._extract_audio_from_video(s3_url)
            if not audio_s3_url:
                logger.error("❌ فشل استخراج الصوت من الفيديو")
                VideoProcessingJob._update_status(uploaded_file_id, "failed", db=db)
                return
            
            logger.info(f"✅ تم استخراج الصوت: {audio_s3_url}")
            
            # 3. تحويل الصوت لنص (STT)
            logger.info(f"🎤 جاري تحويل الصوت لنص...")
            stt_result = stt_service.transcribe_audio(audio_s3_url)
            
            if not stt_result['success']:
                logger.error(f"❌ فشل تحويل الصوت: {stt_result.get('error')}")
                VideoProcessingJob._update_status(uploaded_file_id, "failed", db=db)
                return
            
            transcription = stt_result['text']
            confidence = stt_result.get('confidence', 0)
            detected_language = stt_result.get('language', 'ar')
            logger.info(f"✅ تم تحويل الصوت: {transcription[:100]}...")
            logger.info(f"   Language: {stt_result.get('language_name', 'Unknown')}")
            logger.info(f"   Confidence: {confidence:.2%}")
            
            # 4. حفظ النص في transcripts (في uploaded_files)
            logger.info(f"💾 جاري حفظ النص في transcripts...")
            VideoProcessingJob._update_status(uploaded_file_id, "processing", transcription, db=db)
            
            # 5. فحص الصلة بالكلمات المفتاحية
            logger.info(f"🔍 جاري فحص الصلة بالكلمات المفتاحية...")
            is_relevant = is_relevant_article("", transcription, language="ar")
            matched_keywords = get_matching_keywords("", transcription, language="ar")
            
            # طباعة تفاصيل الفلترة
            debug_info = debug_filter("", transcription, language="ar")
            logger.info(f"📊 تفاصيل الفلترة:")
            logger.info(f"   - Layer 1 (أساسي): {debug_info['layer_1']}")
            logger.info(f"   - Layer 2 (عمليات): {debug_info['layer_2']}")
            logger.info(f"   - Layer 3 (سياق): {debug_info['layer_3']}")
            
            if not is_relevant:
                logger.warning(f"⚠️ الخبر غير ذي صلة - لم يتم العثور على كلمات مفتاحية")
                logger.warning(f"   الكلمات المطابقة: {matched_keywords}")
                VideoProcessingJob._update_status(uploaded_file_id, "rejected", db=db)
                return
            
            logger.info(f"✅ الخبر ذو صلة - الكلمات المفتاحية: {matched_keywords}")
            
            # 6. إنشاء صف في raw_data
            logger.info(f"💾 جاري إنشاء سجل في raw_data...")
            raw_data_id = VideoProcessingJob._create_raw_data_record(
                uploaded_file_id=uploaded_file_id,
                media_url=s3_url,
                content=transcription,
                tags=matched_keywords,
                db=db
            )
            
            if not raw_data_id:
                logger.error("❌ فشل إنشاء سجل في raw_data")
                VideoProcessingJob._update_status(uploaded_file_id, "failed", db=db)
                return
            
            logger.info(f"✅ تم إنشاء سجل raw_data برقم: {raw_data_id}")
            
            # 7. تحديث حالة الملف
            VideoProcessingJob._update_status(uploaded_file_id, "completed", transcription, db=db)
            
            logger.info(f"✅ تمت معالجة الملف الفيديو بنجاح: {uploaded_file_id}")
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الملف الفيديو: {e}")
            try:
                VideoProcessingJob._update_status(uploaded_file_id, "failed", db=db)
            except:
                pass
    
    @staticmethod
    def _extract_audio_from_video(video_s3_url: str) -> str:
        """
        استخراج الصوت من الفيديو
        
        Args:
            video_s3_url: رابط الفيديو على S3
            
        Returns:
            str: رابط الصوت المستخرج على S3
        """
        import tempfile
        import subprocess
        import boto3
        import os
        from config.settings import (
            S3_BUCKET_NAME, AWS_REGION, 
            AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
        )
        
        # Add FFmpeg to PATH
        try:
            import static_ffmpeg
            static_ffmpeg.add_paths()
        except:
            pass
        
        temp_video_path = None
        temp_audio_path = None
        
        try:
            # 1. تحميل الفيديو من S3
            logger.info(f"📥 جاري تحميل الفيديو من S3...")
            s3_client = boto3.client(
                's3',
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            
            # استخراج bucket و key من الـ URL
            # s3://bucket/path/file.mp4 → bucket, path/file.mp4
            parts = video_s3_url.replace('s3://', '').split('/', 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ''
            
            # إنشاء مسارات مؤقتة
            temp_dir = tempfile.gettempdir()
            temp_video_path = os.path.join(temp_dir, 'video_temp.mp4')
            temp_audio_path = os.path.join(temp_dir, 'audio_temp.wav')
            
            # حذف الملفات القديمة إن وجدت
            for path in [temp_video_path, temp_audio_path]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass
            
            # تحميل الفيديو
            s3_client.download_file(bucket, key, temp_video_path)
            logger.info(f"✅ تم تحميل الفيديو: {temp_video_path}")
            
            # 2. استخراج الصوت باستخدام ffmpeg
            logger.info(f"🎵 جاري استخراج الصوت باستخدام ffmpeg...")
            
            cmd = [
                'ffmpeg', '-y', '-i', temp_video_path,
                '-ar', '16000',      # 16kHz sample rate
                '-ac', '1',          # mono
                '-acodec', 'pcm_s16le',  # LINEAR16
                temp_audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ خطأ في ffmpeg: {result.stderr}")
                return None
            
            if not os.path.exists(temp_audio_path):
                logger.error(f"❌ الملف الصوتي لم ينشأ")
                return None
            
            logger.info(f"✅ تم استخراج الصوت: {temp_audio_path}")
            
            # 3. رفع الصوت إلى S3
            logger.info(f"📤 جاري رفع الصوت إلى S3...")
            audio_key = key.replace('.mp4', '.wav').replace('original/videos/', 'original/audios/')
            
            s3_client.upload_file(temp_audio_path, bucket, audio_key)
            
            audio_s3_url = f"s3://{bucket}/{audio_key}"
            logger.info(f"✅ تم رفع الصوت: {audio_s3_url}")
            
            return audio_s3_url
            
        except Exception as e:
            logger.error(f"❌ خطأ في استخراج الصوت من الفيديو: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
        finally:
            # تنظيف الملفات المؤقتة
            for path in [temp_video_path, temp_audio_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
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
                6,                      # source_id = 6 (video)
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
    
    @staticmethod
    def _save_transcript(uploaded_file_id: int, transcription: str, confidence: float, language: str, db=None) -> int:
        """
        حفظ النص المستخرج في جدول transcripts
        
        Args:
            uploaded_file_id: معرف الملف المرفوع
            transcription: النص المستخرج
            confidence: درجة الثقة
            language: اللغة المكتشفة
            db: database connection
            
        Returns:
            int: معرف السجل المحفوظ
        """
        if db is None:
            logger.error("❌ لم يتم توفير database connection")
            return None
            
        try:
            query = """
                INSERT INTO public.transcripts 
                (uploaded_file_id, transcription, confidence, language, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            
            db.cursor.execute(query, (
                uploaded_file_id,
                transcription,
                confidence,
                language,
                datetime.utcnow()
            ))
            
            result = db.cursor.fetchone()
            db.conn.commit()
            
            if result:
                transcript_id = result['id'] if isinstance(result, dict) else result[0]
                logger.info(f"✅ تم حفظ النص برقم: {transcript_id}")
                return transcript_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ النص: {e}")
            try:
                db.conn.rollback()
            except:
                pass
            return None
