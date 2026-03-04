"""
التحقق من حالة الترجمة والمعالجة
Verify translation and processing status
"""

from database.connection import DatabaseConnection


def verify_translation_status():
    """التحقق من حالة الترجمة والمعالجة"""
    
    db = DatabaseConnection()
    if not db.connect():
        print("❌ Failed to connect to database")
        return

    try:
        print("=" * 60)
        print("📊 Translation and Processing Status Report")
        print("=" * 60)

        # 1. إجمالي الأخبار
        db.cursor.execute("SELECT COUNT(*) FROM raw_news WHERE language_id IN (2, 3)")
        result = db.cursor.fetchone()
        total_articles = result['count'] if isinstance(result, dict) else result[0]
        print(f"\n📰 Total Articles (Hebrew & English): {total_articles}")

        # 2. الأخبار المعلقة (لم تتم معالجتها)
        db.cursor.execute(
            """
            SELECT COUNT(*) FROM raw_news 
            WHERE language_id IN (2, 3) 
            AND processing_status = 0
            """
        )
        result = db.cursor.fetchone()
        pending = result['count'] if isinstance(result, dict) else result[0]
        print(f"⏳ Pending (processing_status = 0): {pending}")

        # 3. الأخبار المعالجة
        db.cursor.execute(
            """
            SELECT COUNT(*) FROM raw_news 
            WHERE language_id IN (2, 3) 
            AND processing_status = 1
            """
        )
        result = db.cursor.fetchone()
        processed = result['count'] if isinstance(result, dict) else result[0]
        print(f"✅ Processed (processing_status = 1): {processed}")

        # 4. نسبة المعالجة
        if total_articles > 0:
            percentage = (processed / total_articles) * 100
            print(f"📈 Processing Rate: {percentage:.2f}%")
        else:
            print("📈 Processing Rate: N/A (no articles)")

        # 5. الترجمات المخزنة
        db.cursor.execute("SELECT COUNT(*) FROM translations")
        result = db.cursor.fetchone()
        total_translations = result['count'] if isinstance(result, dict) else result[0]
        print(f"\n🌍 Total Translations Stored: {total_translations}")

        # 6. توزيع حسب اللغة المصدر
        print("\n📋 Articles by Source Language:")
        db.cursor.execute(
            """
            SELECT l.name, COUNT(r.id) as count
            FROM raw_news r
            JOIN languages l ON r.language_id = l.id
            WHERE r.language_id IN (2, 3)
            GROUP BY l.name
            """
        )
        for row in db.cursor.fetchall():
            if isinstance(row, dict):
                print(f"   {row['name']}: {row['count']}")
            else:
                print(f"   {row[0]}: {row[1]}")

        # 7. توزيع المعالجة حسب اللغة
        print("\n📊 Processing Status by Source Language:")
        db.cursor.execute(
            """
            SELECT 
                l.name,
                COUNT(CASE WHEN r.processing_status = 0 THEN 1 END) as pending,
                COUNT(CASE WHEN r.processing_status = 1 THEN 1 END) as processed,
                COUNT(*) as total
            FROM raw_news r
            JOIN languages l ON r.language_id = l.id
            WHERE r.language_id IN (2, 3)
            GROUP BY l.name
            """
        )
        for row in db.cursor.fetchall():
            if isinstance(row, dict):
                lang = row['name']
                pending_count = row['pending']
                processed_count = row['processed']
                total_count = row['total']
            else:
                lang, pending_count, processed_count, total_count = row
            
            pct = (processed_count / total_count * 100) if total_count > 0 else 0
            print(f"   {lang}:")
            print(f"      Pending: {pending_count}")
            print(f"      Processed: {processed_count}")
            print(f"      Total: {total_count}")
            print(f"      Rate: {pct:.2f}%")

        # 8. أمثلة على الأخبار المعالجة
        print("\n✅ Recently Processed Articles:")
        db.cursor.execute(
            """
            SELECT r.id, r.title_original, l.name, r.processing_status
            FROM raw_news r
            JOIN languages l ON r.language_id = l.id
            WHERE r.language_id IN (2, 3)
            AND r.processing_status = 1
            ORDER BY r.created_at DESC
            LIMIT 5
            """
        )
        for i, row in enumerate(db.cursor.fetchall(), 1):
            if isinstance(row, dict):
                article_id = row['id']
                title = row['title_original']
                lang = row['name']
                status = row['processing_status']
            else:
                article_id, title, lang, status = row
            
            status_emoji = "✅" if status == 1 else "⏳"
            print(f"   {i}. {status_emoji} [{lang}] ID:{article_id}")
            print(f"      {title[:60]}...")

        # 9. أمثلة على الأخبار المعلقة
        print("\n⏳ Pending Articles:")
        db.cursor.execute(
            """
            SELECT r.id, r.title_original, l.name, r.processing_status
            FROM raw_news r
            JOIN languages l ON r.language_id = l.id
            WHERE r.language_id IN (2, 3)
            AND r.processing_status = 0
            ORDER BY r.created_at DESC
            LIMIT 5
            """
        )
        pending_list = db.cursor.fetchall()
        if pending_list:
            for i, row in enumerate(pending_list, 1):
                if isinstance(row, dict):
                    article_id = row['id']
                    title = row['title_original']
                    lang = row['name']
                    status = row['processing_status']
                else:
                    article_id, title, lang, status = row
                
                print(f"   {i}. ⏳ [{lang}] ID:{article_id}")
                print(f"      {title[:60]}...")
        else:
            print("   ✅ No pending articles!")

        # 10. ملخص سريع
        print("\n" + "=" * 60)
        print("📌 Quick Summary:")
        print("=" * 60)
        print(f"Total Articles: {total_articles}")
        print(f"Processed: {processed} ({percentage:.1f}%)" if total_articles > 0 else "Processed: 0")
        print(f"Pending: {pending}")
        print(f"Translations: {total_translations}")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    verify_translation_status()
