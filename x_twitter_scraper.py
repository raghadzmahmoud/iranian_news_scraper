"""
X (Twitter) Scraper
استخدم الكوكيز أو اليوزرنيم لسحب تغريدات من قائمة حسابات
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# ============================================================
# ⚙️ الإعدادات — عدّل هنا فقط
# ============================================================

COOKIES = {
    "auth_token": "YOUR_AUTH_TOKEN_HERE",
    "ct0":        "YOUR_CT0_TOKEN_HERE",
}

# استخدم الكوكيز فقط
AUTH_METHOD = "cookies"

COOKIES_FILE = "x_cookies.json"

ACCOUNTS = [
    "wamnews", "spagov", "QatarNewsAgency", "bna_ar",
    "OmanNewsAgency", "kuna_ar", "Sana__gov", "Petranews",
    "arableague_gs", "INA__NEWS", "nnaleb", "DXBMediaOffice",
    "admediaoffice", "HHmansour", "UAEmediaoffice", "MohamedBinZayed",
    "araReuters", "AFPar", "dw_arabic", "RTArNewsRoom",
    "cnnarabic", "BBCArabic", "skynewsarabia", "BBCBreaking",
    "AvichayAdraee", "CaptainElla1", "WhiteHouse", "RapidResponse47",
    "CENTCOM", "elonmusk", "alilarijani_ir", "AnwarGargash",
]

MAX_TWEETS_PER_ACCOUNT  = 20
DELAY_BETWEEN_ACCOUNTS  = 3
OUTPUT_FILE             = "tweets_output.json"
DEBUG                   = True

# ============================================================


def extract_media_url(media_item) -> Optional[str]:
    """
    ✅ الحل الرئيسي — يجرب كل الـ attributes الممكنة لـ Photo/Video
    twikit بيرجع Photo أو Video objects بـ attributes مختلفة
    """
    # الـ attributes المحتملة بالترتيب
    for attr in ['url', 'media_url_https', 'media_url', 'preview_image_url', 'expanded_url']:
        val = getattr(media_item, attr, None)
        if val and isinstance(val, str) and val.startswith('http'):
            return val

    # لو كان dict
    if isinstance(media_item, dict):
        for key in ['url', 'media_url_https', 'media_url']:
            if media_item.get(key):
                return media_item[key]

    return None


def extract_image(tweet) -> Optional[str]:
    """استخرج أول صورة من التغريدة"""
    try:
        # twikit: tweet.media هو list من Photo/Video objects
        if hasattr(tweet, 'media') and tweet.media:
            for media_item in tweet.media:
                url = extract_media_url(media_item)
                if url:
                    return url

        # طريقة بديلة عبر _data الخام
        if hasattr(tweet, '_data'):
            entities = tweet._data.get('entities', {})
            media_list = entities.get('media', [])
            for m in media_list:
                url = m.get('media_url_https') or m.get('media_url')
                if url:
                    return url

    except Exception:
        pass

    return None


def format_tweet(tweet, username: str) -> Dict:
    """تحويل التغريدة إلى dict نظيف"""
    text = getattr(tweet, 'text', '') or getattr(tweet, 'full_text', '')
    tweet_id = str(getattr(tweet, 'id', '') or getattr(tweet, 'id_str', ''))
    date = str(getattr(tweet, 'created_at', ''))

    return {
        "account":  username,
        "id":       tweet_id,
        "text":     text,
        "url":      f"https://x.com/{username}/status/{tweet_id}",
        "date":     date,
        "likes":    getattr(tweet, 'favorite_count', 0),
        "retweets": getattr(tweet, 'retweet_count', 0),
        "image":    extract_image(tweet),  # ✅ الآن ما في خطأ
    }


async def setup_client():
    """إعداد الكلايت وتحميل الكوكيز"""
    try:
        from twikit import Client
    except ImportError:
        print("❌ twikit غير مثبت. شغّل: pip install twikit")
        exit(1)

    client = Client(language='ar-SA')

    print("🔑 تحميل الكوكيز...")
    with open(COOKIES_FILE, "w") as f:
        json.dump(COOKIES, f)
    client.load_cookies(COOKIES_FILE)
    print("✅ تم تحميل الكوكيز")

    return client


async def scrape_account(client, username: str) -> Dict:
    """سحب تغريدات من حساب واحد"""
    tweets_data = []
    status = "unknown"
    error_msg = None

    try:
        user = await client.get_user_by_screen_name(username)
        print(f"   👤 {user.name} (@{username}) — {user.followers_count:,} متابع")

        tweets = []

        # الطريقة 1: البحث
        try:
            tweets = await client.search_tweet(
                f"from:{username}", product='Latest', count=MAX_TWEETS_PER_ACCOUNT
            )
            if DEBUG:
                print(f"      [Search] وجدت {len(tweets)} تغريدة")
        except Exception as e1:
            if DEBUG:
                print(f"      [Search فشل] {str(e1)[:60]}")
            # الطريقة 2: get_tweets
            try:
                tweets = await user.get_tweets('Tweets', count=MAX_TWEETS_PER_ACCOUNT)
                if DEBUG:
                    print(f"      [get_tweets] وجدت {len(tweets)} تغريدة")
            except Exception as e2:
                if DEBUG:
                    print(f"      [get_tweets فشل] {str(e2)[:60]}")

        if not tweets:
            status = "⚠️ بدون تغريدات"
            print(f"   {status}")
            return {"tweets": [], "status": status, "error": None}

        # معالجة التغريدات
        for idx, tweet in enumerate(tweets):
            try:
                text = getattr(tweet, 'text', '') or getattr(tweet, 'full_text', '')
                if text and len(text.strip()) > 0:
                    tweets_data.append(format_tweet(tweet, username))
                elif DEBUG:
                    print(f"      [تغريدة فارغة {idx}]")
            except Exception as e:
                if DEBUG:
                    print(f"      [خطأ في التغريدة {idx}] {str(e)[:60]}")
                continue

        status = "✅ نجح"
        print(f"   {status} — {len(tweets_data)} تغريدة")

    except Exception as e:
        error = str(e)
        if "Rate limit" in error or "429" in error:
            status = "⏳ Rate limit"
            error_msg = "تم تجاوز الحد — انتظر دقيقة"
            print(f"   {status}")
            await asyncio.sleep(60)
        elif "Could not find" in error or "404" in error:
            status = "❌ غير موجود"
            error_msg = "الحساب غير موجود أو محذوف"
            print(f"   {status}: @{username}")
        elif "suspended" in error.lower():
            status = "🚫 موقوف"
            error_msg = "الحساب موقوف من X"
            print(f"   {status}: @{username}")
        elif "Unauthorized" in error or "401" in error:
            status = "🔐 خطأ مصادقة"
            error_msg = "الكوكيز انتهت أو غير صحيحة"
            print(f"   {status}")
        elif "Forbidden" in error or "403" in error:
            status = "🔒 ممنوع"
            error_msg = "لا صلاحية للوصول"
            print(f"   {status}: @{username}")
        else:
            status = "❌ خطأ"
            error_msg = error[:120]
            print(f"   {status}: {error_msg}")

    return {"tweets": tweets_data, "status": status, "error": error_msg}


async def main():
    print("=" * 60)
    print("🐦 X (Twitter) Scraper")
    print("=" * 60)

    client = await setup_client()

    all_results   = {}
    total_tweets  = 0
    failed        = []
    status_summary = {}

    for i, username in enumerate(ACCOUNTS, 1):
        print(f"\n[{i}/{len(ACCOUNTS)}] @{username}")
        result = await scrape_account(client, username)

        tweets = result["tweets"]
        status = result["status"]
        error  = result["error"]

        all_results[username] = {
            "tweets": tweets,
            "status": status,
            "error":  error,
            "count":  len(tweets),
        }

        status_summary[status] = status_summary.get(status, 0) + 1

        if status == "✅ نجح":
            total_tweets += len(tweets)
        else:
            failed.append({"username": username, "status": status, "error": error})

        if i < len(ACCOUNTS):
            await asyncio.sleep(DELAY_BETWEEN_ACCOUNTS)

    # حفظ النتائج
    output = {
        "scraped_at":     datetime.now().isoformat(),
        "total_accounts": len(ACCOUNTS),
        "total_tweets":   total_tweets,
        "status_summary": status_summary,
        "failed_accounts": failed,
        "results":        all_results,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # ملخص
    print("\n" + "=" * 60)
    print("📊 ملخص النتائج")
    print("=" * 60)
    print(f"✅ إجمالي التغريدات: {total_tweets}")
    print(f"✅ حسابات ناجحة:     {status_summary.get('✅ نجح', 0)}/{len(ACCOUNTS)}")

    print("\n📈 توزيع الحالات:")
    for s, count in sorted(status_summary.items(), key=lambda x: x[1], reverse=True):
        print(f"  {s}: {count}")

    if failed:
        print(f"\n❌ الحسابات الفاشلة ({len(failed)}):")
        for item in failed:
            err = f" — {item['error']}" if item['error'] else ""
            print(f"  • @{item['username']}: {item['status']}{err}")

    print(f"\n💾 النتائج محفوظة في: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())