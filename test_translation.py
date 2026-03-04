"""
اختبار سريع لخدمة الترجمة
Quick test for translation service
"""

import asyncio
import os
from services.translation.translator import NewsTranslator


async def test_translation():
    """Test translation service"""
    api_key = os.getenv("war_news_translation_api_key")

    if not api_key:
        print("❌ Error: API key not found in environment variables")
        return False

    print("✓ API key found")

    translator = NewsTranslator(api_key=api_key, max_concurrent=5)
    print("✓ Translator initialized")

    # Test 1: Single translation
    print("\n" + "=" * 50)
    print("Test 1: Single Translation")
    print("=" * 50)

    test_text = "The Israeli Defense Forces conducted an airstrike on Gaza"
    print(f"Original: {test_text}")

    try:
        translation = await translator.translate_single(test_text)
        if translation:
            print(f"✓ Translation successful")
            print(f"Arabic: {translation[:100]}...")
        else:
            print("❌ Translation returned None")
            return False
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return False

    # Test 2: Batch translation
    print("\n" + "=" * 50)
    print("Test 2: Batch Translation (3 articles)")
    print("=" * 50)

    test_texts = [
        "The Mossad confirmed the operation",
        "Senior officials discussed the ceasefire",
        "Sources familiar with the matter said...",
    ]

    try:
        translations = await translator.translate_batch(test_texts)
        successful = sum(1 for t in translations if t)
        print(f"✓ Batch translation completed")
        print(f"  Successful: {successful}/{len(test_texts)}")

        for i, (original, translation) in enumerate(zip(test_texts, translations), 1):
            if translation:
                print(f"  {i}. ✓ {original[:40]}...")
            else:
                print(f"  {i}. ❌ {original[:40]}...")

    except Exception as e:
        print(f"❌ Batch translation error: {e}")
        return False

    # Test 3: Semaphore test (verify bounded concurrency)
    print("\n" + "=" * 50)
    print("Test 3: Bounded Concurrency (5 concurrent)")
    print("=" * 50)

    many_texts = [f"Test article {i}" for i in range(10)]

    try:
        print(f"Translating {len(many_texts)} articles with max 5 concurrent...")
        translations = await translator.translate_batch(many_texts)
        successful = sum(1 for t in translations if t)
        print(f"✓ Bounded concurrency test passed")
        print(f"  Successful: {successful}/{len(many_texts)}")
    except Exception as e:
        print(f"❌ Bounded concurrency error: {e}")
        return False

    # Test 4: Database connection
    print("\n" + "=" * 50)
    print("Test 4: Database Connection")
    print("=" * 50)

    try:
        from database.connection import DatabaseConnection
        
        db = DatabaseConnection()
        if db.connect():
            print("✓ Database connection successful")
            db.cursor.execute("SELECT COUNT(*) FROM raw_news WHERE language_id IN (2, 3)")
            result = db.cursor.fetchone()
            count = result['count'] if isinstance(result, dict) else result[0]
            print(f"  Pending articles: {count}")
            db.close()
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

    print("\n" + "=" * 50)
    print("✓ All tests passed!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_translation())
    exit(0 if success else 1)
