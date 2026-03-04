"""
مثال على استخدام خدمة الترجمة
Example usage of the translation service
"""

import asyncio
import os
from services.translation.translator import NewsTranslator
from database.connection import get_db_connection

# Example 1: Translate a single article
async def example_single_translation():
    print("=" * 50)
    print("Example 1: Single Article Translation")
    print("=" * 50)

    api_key = os.getenv("war_news_translation_api_key")
    translator = NewsTranslator(api_key=api_key)

    # Hebrew example
    hebrew_text = """
    צבא ההגנה הישראלי ביצע מבצע צבאי בעזה.
    כוחות הכיבוש תקפו מטרות צבאיות.
    """

    # English example
    english_text = """
    The Israeli Defense Forces conducted a military operation in Gaza.
    The IDF targeted military objectives.
    """

    print("\nTranslating Hebrew text...")
    hebrew_translation = await translator.translate_single(hebrew_text)
    print(f"Hebrew → Arabic:\n{hebrew_translation}\n")

    print("Translating English text...")
    english_translation = await translator.translate_single(english_text)
    print(f"English → Arabic:\n{english_translation}\n")


# Example 2: Batch translation with bounded concurrency
async def example_batch_translation():
    print("=" * 50)
    print("Example 2: Batch Translation (5 concurrent)")
    print("=" * 50)

    api_key = os.getenv("war_news_translation_api_key")
    translator = NewsTranslator(api_key=api_key, max_concurrent=5)

    articles = [
        "Israeli forces launched an airstrike on Gaza",
        "The Mossad confirmed the operation",
        "Senior officials discussed the ceasefire",
        "Sources familiar with the matter said...",
        "Casualties reported in the region",
        "The Shin Bet released a statement",
    ]

    print(f"\nTranslating {len(articles)} articles with 5 concurrent requests...")
    translations = await translator.translate_batch(articles)

    for i, (original, translation) in enumerate(zip(articles, translations), 1):
        print(f"\n{i}. Original: {original}")
        print(f"   Translation: {translation[:100]}...")


# Example 3: Translate and store from database
async def example_translate_and_store():
    print("=" * 50)
    print("Example 3: Translate and Store from Database")
    print("=" * 50)

    api_key = os.getenv("war_news_translation_api_key")
    translator = NewsTranslator(api_key=api_key, max_concurrent=5)

    # Get pending articles from database
    from database.connection import DatabaseConnection
    
    db = DatabaseConnection()
    if not db.connect():
        print("Failed to connect to database")
        return

    try:
        db.cursor.execute(
            """
            SELECT id FROM raw_news
            WHERE language_id IN (2, 3)
            AND processing_status = 0
            LIMIT 5
            """
        )

        pending = db.cursor.fetchall()
        raw_news_ids = [
            article['id'] if isinstance(article, dict) else article[0]
            for article in pending
        ]

        if raw_news_ids:
            print(f"\nFound {len(raw_news_ids)} articles to translate")
            print(f"Article IDs: {raw_news_ids}")

            result = await translator.translate_and_store(raw_news_ids)
            print(f"\nTranslation Result:")
            print(f"  Success: {result.get('success', 0)}")
            print(f"  Failed: {result.get('failed', 0)}")
            print(f"  Total: {result.get('total', 0)}")
        else:
            print("No pending articles found")

    finally:
        db.close()


# Example 4: Check translation statistics
async def example_translation_stats():
    print("=" * 50)
    print("Example 4: Translation Statistics")
    print("=" * 50)

    from database.connection import DatabaseConnection
    
    db = DatabaseConnection()
    if not db.connect():
        print("Failed to connect to database")
        return

    try:
        # Count translations by language
        db.cursor.execute(
            """
            SELECT l.name, COUNT(t.id) as count
            FROM translations t
            JOIN languages l ON t.language_id = l.id
            GROUP BY l.name
            """
        )

        stats = db.cursor.fetchall()
        print("\nTranslations by target language:")
        for row in stats:
            if isinstance(row, dict):
                print(f"  {row['name']}: {row['count']}")
            else:
                print(f"  {row[0]}: {row[1]}")

        # Count pending articles
        db.cursor.execute(
            """
            SELECT l.name, COUNT(r.id) as count
            FROM raw_news r
            JOIN languages l ON r.language_id = l.id
            WHERE r.language_id IN (2, 3)
            AND r.processing_status = 0
            GROUP BY l.name
            """
        )

        pending = db.cursor.fetchall()
        print("\nPending articles by source language:")
        for row in pending:
            if isinstance(row, dict):
                print(f"  {row['name']}: {row['count']}")
            else:
                print(f"  {row[0]}: {row[1]}")

    finally:
        db.close()


async def main():
    """Run all examples"""
    try:
        # Uncomment to run examples
        # await example_single_translation()
        # await example_batch_translation()
        # await example_translate_and_store()
        await example_translation_stats()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
