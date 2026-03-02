"""
🎙️ STT Service (Speech-to-Text)
تحويل الصوت إلى نص باستخدام Google Cloud Speech-to-Text
يدعم الملفات الطويلة (> 1 دقيقة) والـ WebM format
"""
import os
import sys
import subprocess
import tempfile
from typing import Optional, Dict
import requests
from dotenv import load_dotenv

# Add FFmpeg to PATH automatically
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
    print("✅ static-ffmpeg loaded successfully")
except ImportError:
    print("⚠️ static-ffmpeg not installed, FFmpeg must be in PATH")
    print("   Run: pip install static-ffmpeg")

load_dotenv()

# Google Cloud Speech-to-Text
try:
    from google.cloud import speech
except ImportError:
    print("❌ google-cloud-speech not installed")
    print("   Run: pip install google-cloud-speech")
    sys.exit(1)

from utils.logger import logger


class STTService:
    """تحويل ملفات الصوت إلى نص
    يدعم الملفات الطويلة وتحويل الـ WebM تلقائياً
    يدعم لغات متعددة: العربية، الإنجليزية، العبرية"""
    
    # Language codes mapping
    SUPPORTED_LANGUAGES = {
        'ar': {
            'name': 'العربية',
            'code': 'ar-SA',
            'alternatives': ['ar-EG', 'ar-JO', 'ar-PS', 'ar-AE']
        },
        'en': {
            'name': 'English',
            'code': 'en-US',
            'alternatives': ['en-GB', 'en-AU']
        },
        'he': {
            'name': 'עברית',
            'code': 'he-IL',
            'alternatives': []
        }
    }
    
    def __init__(self):
        """Initialize Google Cloud Speech-to-Text"""
        try:
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if credentials_json:
                import json
                from google.oauth2 import service_account
                try:
                    credentials_dict = json.loads(credentials_json)
                    credentials = service_account.Credentials.from_service_account_info(
                        credentials_dict,
                        scopes=['https://www.googleapis.com/auth/cloud-platform']
                    )
                    self.client = speech.SpeechClient(credentials=credentials)
                    logger.info("✅ STTService initialized (from JSON env var)")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON in GOOGLE_CREDENTIALS_JSON: {e}")
                    raise ValueError(f"Invalid JSON credentials: {e}")
            elif credentials_path and os.path.exists(credentials_path):
                self.client = speech.SpeechClient()
                logger.info("✅ STTService initialized (from file)")
            else:
                raise ValueError("Google credentials not found")
        except Exception as e:
            logger.error(f"❌ STTService initialization failed: {e}")
            raise
    
    def transcribe_audio(self, audio_url: str, language: str = 'ar', max_retries: int = 3) -> Dict:
        """تحويل ملف صوتي إلى نص
        يدعم الملفات الطويلة وتحويل الـ WebM تلقائياً
        
        Args:
            audio_url: رابط الملف الصوتي على S3
            language: رمز اللغة (ar, en, he) - الافتراضي: ar
            max_retries: عدد محاولات إعادة المحاولة
            
        Returns:
            dict: نتيجة التحويل
        """
        
        if not audio_url:
            return {'success': False, 'error': 'رابط الصوت فارغ'}
        
        # Validate language
        if language not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"⚠️ Language '{language}' not supported, using Arabic")
            language = 'ar'
        
        lang_info = self.SUPPORTED_LANGUAGES[language]
        logger.info(f"🎙️ Transcribing audio in {lang_info['name']}: {audio_url}")
        
        audio_file_path = None
        wav_file_path = None
        
        try:
            # ========================================
            # Step 1: Download audio
            # ========================================
            logger.info(f"📥 Step 1: Downloading audio from S3...")
            audio_file_path = self._download_audio(audio_url)
            logger.info(f"✅ Audio downloaded: {audio_file_path}")
            
            # ========================================
            # Step 2: Convert to WAV if needed
            # ========================================
            file_extension = audio_url.split('.')[-1].lower()
            logger.info(f"📋 File extension: {file_extension}")
            
            if file_extension in ['webm', 'ogg', 'm4a']:
                logger.info(f"🔄 Converting {file_extension} to WAV...")
                wav_file_path = self._convert_to_wav(audio_file_path)
                if wav_file_path:
                    logger.info(f"✅ Converted to WAV: {wav_file_path}")
                    working_file = wav_file_path
                    encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
                    sample_rate = 16000
                else:
                    logger.warning(f"⚠️ Conversion failed, trying original format")
                    working_file = audio_file_path
                    encoding = self._get_audio_encoding(file_extension)
                    # Set sample rate for Opus formats (WhatsApp PTT = Opus 16kHz)
                    if file_extension == 'ogg':
                        sample_rate = 16000  # WhatsApp PTT = Opus 16kHz
                    elif file_extension == 'webm':
                        sample_rate = 48000
                    else:
                        sample_rate = None
            else:
                working_file = audio_file_path
                encoding = self._get_audio_encoding(file_extension)
                sample_rate = None
            
            # ========================================
            # Step 3: Read audio content OR upload to GCS
            # ========================================
            logger.info(f"📖 Step 3: Reading audio content...")
            with open(working_file, 'rb') as f:
                audio_content = f.read()
            
            file_size_mb = len(audio_content) / (1024 * 1024)
            logger.info(f"📊 Audio size: {file_size_mb:.2f} MB")
            logger.info(f"📊 Encoding: {encoding}")
            logger.info(f"📊 Sample rate: {sample_rate}")
            
            # ← هون التغيير: إذا الملف أكبر من 1 دقيقة (~1MB WAV) استخدم GCS
            USE_GCS = file_size_mb > 1.0
            gcs_uri = None
            
            if USE_GCS:
                logger.info(f"📦 File size > 1MB, uploading to GCS for long audio processing...")
                file_name = os.path.basename(working_file)
                gcs_uri = self._upload_to_gcs(working_file, file_name)
                if not gcs_uri:
                    return {'success': False, 'error': 'فشل رفع الملف إلى Google Cloud Storage'}
            
            # ========================================
            # Step 4: Transcribe with retries
            # ========================================
            # Sample rates to try per attempt (for Opus formats)
            sample_rate_attempts = [16000, 48000, None] if file_extension in ['webm', 'ogg'] else [sample_rate]
            
            last_error = None
            for attempt in range(max_retries):
                try:
                    logger.info(f"🤖 Transcribing... (attempt {attempt + 1}/{max_retries})")
                    
                    # Use different sample rate for each attempt (if applicable)
                    current_sample_rate = sample_rate_attempts[attempt] if attempt < len(sample_rate_attempts) else sample_rate_attempts[-1]
                    
                    # Build config with language support
                    config_params = {
                        'encoding': encoding,
                        'language_code': lang_info['code'],
                        'alternative_language_codes': lang_info['alternatives'],
                        'enable_automatic_punctuation': True,
                        'model': 'default',
                    }
                    
                    if current_sample_rate:
                        config_params['sample_rate_hertz'] = current_sample_rate
                        logger.info(f"   📊 Trying sample_rate={current_sample_rate} Hz")
                    
                    config = speech.RecognitionConfig(**config_params)
                    
                    # ← بدل audio = speech.RecognitionAudio(content=audio_content)
                    # ← صير هيك: استخدم GCS URI للملفات الطويلة
                    if USE_GCS and gcs_uri:
                        logger.info(f"   📦 Using GCS URI for long audio")
                        audio = speech.RecognitionAudio(uri=gcs_uri)
                        # للـ GCS دايماً استخدم long_running_recognize
                        logger.info(f"   📤 Sending to Google Cloud Speech API (async)...")
                        response = self.client.long_running_recognize(config=config, audio=audio)
                        logger.info(f"   ⏳ Waiting for long audio transcription...")
                        response = response.result(timeout=300)
                    else:
                        audio = speech.RecognitionAudio(content=audio_content)
                        # Try sync first, then async for long audio
                        logger.info(f"   📤 Sending to Google Cloud Speech API...")
                        try:
                            response = self.client.recognize(config=config, audio=audio)
                        except Exception as sync_error:
                            error_str = str(sync_error)
                            if 'Sync input too long' in error_str or 'audio too long' in error_str.lower():
                                logger.info(f"   ⏳ Audio too long, using async recognition...")
                                response = self._transcribe_long_audio(audio_content, config)
                            else:
                                raise sync_error
                    
                    # Extract transcription
                    transcription = self._extract_transcription(response)
                    if not transcription or len(transcription) < 10:
                        logger.warning(f"⚠️ Transcription too short: {len(transcription) if transcription else 0} chars")
                        if attempt < max_retries - 1:
                            continue
                        else:
                            return {'success': False, 'error': 'النص المستخرج قصير جداً أو فارغ'}
                    
                    confidence = self._calculate_confidence(response)
                    logger.info(f"✅ Transcription successful: {len(transcription)} chars")
                    logger.info(f"   Language: {lang_info['name']}")
                    logger.info(f"   Preview: {transcription[:100]}...")
                    logger.info(f"   Confidence: {confidence:.2%}")
                    
                    return {
                        'success': True,
                        'text': transcription,
                        'language': language,
                        'language_name': lang_info['name'],
                        'confidence': confidence,
                        'char_count': len(transcription),
                        'word_count': len(transcription.split())
                    }
                    
                except Exception as e:
                    last_error = str(e)
                    logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                    # Don't retry for certain errors
                    if 'sample rate' in last_error.lower() and attempt == len(sample_rate_attempts) - 1:
                        break
                    continue
            
            return {
                'success': False,
                'error': f'فشل التحويل بعد {max_retries} محاولات: {last_error}'
            }
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return {'success': False, 'error': str(e)}
        finally:
            # Cleanup temp files
            self._cleanup(audio_file_path)
            self._cleanup(wav_file_path)
    
    def _transcribe_long_audio(self, audio_content: bytes, config: speech.RecognitionConfig):
        """Transcribe long audio using async recognition"""
        audio = speech.RecognitionAudio(content=audio_content)
        operation = self.client.long_running_recognize(config=config, audio=audio)
        logger.info(f"   ⏳ Waiting for long audio transcription...")
        # Wait for completion (timeout 5 minutes)
        response = operation.result(timeout=300)
        return response
    
    def _convert_to_wav(self, input_path: str) -> Optional[str]:
        """Convert audio to WAV format (16kHz, mono)"""
        try:
            # Create output path
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
            
            # Try ffmpeg conversion
            cmd = [
                'ffmpeg', '-y', '-i', input_path,
                '-ar', '16000',      # 16kHz sample rate
                '-ac', '1',          # mono
                '-acodec', 'pcm_s16le',  # LINEAR16
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60, text=True)
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 1000:  # At least 1KB
                    return output_path
            
            # Cleanup failed output
            self._cleanup(output_path)
            return None
            
        except Exception as e:
            logger.warning(f"   ⚠️ FFmpeg conversion failed: {e}")
            return None
    
    def _download_audio(self, audio_url: str) -> str:
        """Download audio file from URL (supports S3 URIs and HTTPS URLs)"""
        extension = audio_url.split('.')[-1].lower()
        if extension not in ['mp3', 'wav', 'ogg', 'm4a', 'webm', 'flac']:
            extension = 'mp3'
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{extension}')
        temp_file_path = temp_file.name
        temp_file.close()
        
        logger.info(f"📥 Downloading audio from: {audio_url}")
        
        # Handle S3 URIs (s3://bucket/key)
        if audio_url.startswith('s3://'):
            try:
                import boto3
                from config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
                
                # Parse S3 URI
                s3_parts = audio_url.replace('s3://', '').split('/', 1)
                bucket = s3_parts[0]
                key = s3_parts[1] if len(s3_parts) > 1 else ''
                
                # Create S3 client
                s3_client = boto3.client(
                    's3',
                    region_name=AWS_REGION,
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                )
                
                # Download from S3
                logger.info(f"   📦 Downloading from S3: {bucket}/{key}")
                s3_client.download_file(bucket, key, temp_file_path)
                
            except Exception as e:
                logger.error(f"❌ Failed to download from S3: {e}")
                raise
        else:
            # Handle HTTPS URLs
            response = requests.get(audio_url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        file_size = os.path.getsize(temp_file_path)
        logger.info(f"✅ Downloaded: {file_size / 1024 / 1024:.2f} MB")
        return temp_file_path
    
    def _get_audio_encoding(self, file_extension: str) -> speech.RecognitionConfig.AudioEncoding:
        """Get audio encoding based on file extension"""
        encoding_map = {
            'mp3': speech.RecognitionConfig.AudioEncoding.MP3,
            'wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
            'ogg': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            'flac': speech.RecognitionConfig.AudioEncoding.FLAC,
            'webm': speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            'm4a': speech.RecognitionConfig.AudioEncoding.MP3
        }
        return encoding_map.get(file_extension, speech.RecognitionConfig.AudioEncoding.MP3)
    
    def _extract_transcription(self, response) -> str:
        """Extract transcription text from response"""
        parts = []
        for result in response.results:
            if result.alternatives:
                parts.append(result.alternatives[0].transcript)
        return ' '.join(parts).strip()
    
    def _calculate_confidence(self, response) -> float:
        """Calculate average confidence"""
        confidences = []
        for result in response.results:
            if result.alternatives:
                confidences.append(result.alternatives[0].confidence)
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def _cleanup(self, file_path: str):
        """Delete temp file"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ Cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup failed: {e}")
    
    def _upload_to_gcs(self, audio_file_path: str, file_name: str) -> Optional[str]:
        """
        رفع الملف الصوتي إلى Google Cloud Storage
        مطلوب للملفات الطويلة (> 1 دقيقة)
        
        Args:
            audio_file_path: مسار الملف الصوتي المحلي
            file_name: اسم الملف
            
        Returns:
            str: GCS URI (gs://bucket/path/file)، أو None إذا فشل
        """
        try:
            from google.cloud import storage
            import json
            from google.oauth2 import service_account
            
            # استخدم نفس credentials الـ Speech client
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            if not credentials_json:
                logger.error("❌ GOOGLE_CREDENTIALS_JSON not found in .env")
                return None
            
            credentials_dict = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # إنشاء GCS client
            gcs_client = storage.Client(credentials=credentials)
            bucket_name = os.getenv('GCS_BUCKET_NAME')
            
            if not bucket_name:
                logger.error("❌ GCS_BUCKET_NAME not found in .env")
                return None
            
            bucket = gcs_client.bucket(bucket_name)
            
            # تحديد مسار الملف في GCS
            blob_name = f"stt_temp/{file_name}"
            blob = bucket.blob(blob_name)
            
            # رفع الملف
            logger.info(f"📤 Uploading to GCS: {blob_name}")
            blob.upload_from_filename(audio_file_path)
            
            # إرجاع GCS URI
            gcs_uri = f"gs://{bucket_name}/{blob_name}"
            logger.info(f"✅ Uploaded to GCS: {gcs_uri}")
            return gcs_uri
            
        except Exception as e:
            logger.error(f"❌ GCS upload failed: {e}")
            return None
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect language from text
        
        Args:
            text: النص المراد التحقق من لغته
            
        Returns:
            str: رمز اللغة (ar, en, he)
        """
        if not text:
            return 'ar'  # Default to Arabic
        
        # Count characters by script
        arabic_count = 0
        hebrew_count = 0
        english_count = 0
        
        for char in text:
            # Arabic Unicode range: 0x0600 - 0x06FF
            if 0x0600 <= ord(char) <= 0x06FF:
                arabic_count += 1
            # Hebrew Unicode range: 0x0590 - 0x05FF
            elif 0x0590 <= ord(char) <= 0x05FF:
                hebrew_count += 1
            # English/Latin
            elif char.isalpha():
                english_count += 1
        
        total = arabic_count + hebrew_count + english_count
        if total == 0:
            return 'ar'  # Default to Arabic
        
        # Return the language with highest count
        if arabic_count >= hebrew_count and arabic_count >= english_count:
            return 'ar'
        elif hebrew_count >= english_count:
            return 'he'
        else:
            return 'en'
