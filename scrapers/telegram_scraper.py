"""
سكرابر Telegram - سحب البوستات من قنوات Telegram عبر الويب
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from config.settings import DELAY_BETWEEN_REQUESTS, HEADERS
from utils.logger import logger


class TelegramScraper:
    """سكرابر Telegram للقنوات العامة"""

    def __init__(self, media_dir: str = "./media"):
        self.media_dir = Path(media_dir)
        self.media_dir.mkdir(exist_ok=True)
        self.headers = HEADERS

    def download_media(self, media_url: str) -> Optional[str]:
        """
        تحميل صورة أو فيديو وحفظها محلياً
        
        Args:
            media_url: رابط الميديا
            
        Returns:
            مسار الملف المحفوظ أو None
        """
        if not media_url:
            return None

        try:
            response = requests.get(
                media_url,
                headers=self.headers,
                timeout=20,
                stream=True
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "image/jpeg")
            ext = mimetypes.guess_extension(
                content_type.split(";")[0].strip()
            ) or ".jpg"
            ext = ext.replace(".jpe", ".jpg")

            file_hash = hashlib.md5(media_url.encode()).hexdigest()[:12]
            filename = self.media_dir / f"{file_hash}{ext}"

            if not filename.exists():
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"    💾 ميديا: {filename.name}")

            return str(filename)

        except Exception as e:
            logger.warning(f"    ⚠️  فشل تحميل الميديا: {e}")
            return None

    def extract_media_url_from_style(self, style: str) -> Optional[str]:
        """استخراج رابط الميديا من CSS style"""
        match = re.search(r"url\(['\"]?(https?://[^'\")\s]+)", style)
        return match.group(1) if match else None

    def extract_post_media(self, wrap) -> Dict[str, Optional[str]]:
        """
        استخراج معلومات الميديا من البوست
        
        Returns:
            dict بـ media_type, media_url, media_local
        """
        media_info = {
            "media_type": None,
            "media_url": None,
            "media_local": None
        }

        # 1. صورة
        photo_el = wrap.select_one("a.tgme_widget_message_photo_wrap")
        if photo_el:
            style = photo_el.get("style", "")
            media_url = self.extract_media_url_from_style(style)
            if media_url:
                media_info["media_type"] = "image"
                media_info["media_url"] = media_url
                media_info["media_local"] = self.download_media(media_url)
                return media_info

        # 2. فيديو
        video_el = wrap.select_one("video")
        if video_el:
            src = (
                video_el.get("src") or
                (video_el.select_one("source") or {}).get("src")
            )
            if src:
                media_info["media_type"] = "video"
                media_info["media_url"] = src
                media_info["media_local"] = self.download_media(src)
                return media_info

        # 3. صورة الفيديو (thumbnail)
        video_thumb = wrap.select_one("i.tgme_widget_message_video_thumb")
        if video_thumb:
            style = video_thumb.get("style", "")
            media_url = self.extract_media_url_from_style(style)
            if media_url:
                media_info["media_type"] = "video_thumb"
                media_info["media_url"] = media_url
                return media_info

        # 4. مستند / GIF
        doc_el = wrap.select_one("div.tgme_widget_message_document_thumb")
        if doc_el:
            style = doc_el.get("style", "")
            media_url = self.extract_media_url_from_style(style)
            if media_url:
                media_info["media_type"] = "document"
                media_info["media_url"] = media_url
                return media_info

        return media_info

    def scrape_channel(self, channel: str, max_posts: int = 30, text_only: bool = True) -> List[Dict]:
        """
        سحب بوستات من قناة Telegram
        
        Args:
            channel: اسم القناة (بدون @)
            max_posts: عدد البوستات المطلوبة
            text_only: سحب النص فقط بدون ميديا
            
        Returns:
            قائمة البوستات
        """
        url = f"https://t.me/s/{channel}"
        logger.info(f"\n📨 القناة: @{channel}  →  {url}")

        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"  ❌ فشل الاتصال: {e}")
            return []

        soup = BeautifulSoup(response.text, "lxml")
        wraps = soup.select("div.tgme_widget_message_wrap")

        if not wraps:
            logger.warning(
                "  ⚠️  لم يُعثر على بوستات — ربما القناة خاصة أو الاسم خاطئ"
            )
            return []

        logger.info(f"  📋 عدد البوستات المتاحة: {len(wraps)}")

        posts = []
        for wrap in wraps[-max_posts:]:
            post = {}

            # الرابط
            link_el = wrap.select_one("a.tgme_widget_message_date")
            if not link_el:
                continue

            post["url"] = link_el.get("href", "")
            post["channel"] = channel

            # النص
            text_el = wrap.select_one("div.tgme_widget_message_text")
            post["content"] = (
                text_el.get_text(separator="\n", strip=True)
                if text_el else ""
            )

            # التاريخ
            post["published_at"] = None
            time_el = wrap.select_one("time")
            if time_el and time_el.get("datetime"):
                try:
                    post["published_at"] = datetime.fromisoformat(
                        time_el["datetime"]
                    ).isoformat()
                except Exception:
                    pass

            # الميديا - فقط إذا كان text_only = False
            if text_only:
                post["media_type"] = None
                post["media_url"] = None
                post["media_local"] = None
            else:
                media_info = self.extract_post_media(wrap)
                post.update(media_info)

            posts.append(post)
            time.sleep(DELAY_BETWEEN_REQUESTS)

        logger.info(f"\n  ✅ مجموع البوستات المسحوبة: {len(posts)}")
        return posts


# Instance واحد للاستخدام
telegram_scraper = TelegramScraper()
