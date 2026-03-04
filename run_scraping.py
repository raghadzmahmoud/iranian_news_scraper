#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
سكريبت سهل لتشغيل سحب المقالات الكاملة
"""
import sys
import os

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """الدالة الرئيسية"""
    print("\n" + "="*70)
    print("🚀 برنامج سحب المقالات الكاملة من مصادر RSS")
    print("="*70)
    
    print("\nالخيارات المتاحة:")
    print("1. سحب المقالات من جميع المصادر")
    print("2. سحب المقالات من مصدر معين")
    print("3. عرض الإحصائيات")
    print("4. البحث عن مقالات")
    print("5. تصدير إلى CSV")
    print("0. خروج")
    
    choice = input("\nاختر خياراً (0-5): ").strip()
    
    if choice == "1":
        scrape_all_sources()
    elif choice == "2":
        scrape_single_source()
    elif choice == "3":
        show_statistics()
    elif choice == "4":
        search_articles()
    elif choice == "5":
        export_to_csv()
    elif choice == "0":
        print("\nوداعاً!")
        sys.exit(0)
    else:
        print("❌ خيار غير صحيح")


def scrape_all_sources():
    """سحب المقالات من جميع المصادر"""
    print("\n" + "="*70)
    print("🔄 جاري سحب المقالات من جميع المصادر...")
    print("="*70)
    
    try:
        from test_article_scraping import test_all_sources_scraping, print_summary, save_results_to_json
        
        results = test_all_sources_scraping()
        print_summary(results)
        save_results_to_json(results, "scraped_articles.json")
        
        print("\n✅ تم إكمال السحب بنجاح!")
        print(f"   الملف: scraped_articles.json")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")


def scrape_single_source():
    """سحب المقالات من مصدر معين"""
    from scrapers.rss_scraper import load_rss_sources
    
    sources = load_rss_sources()
    
    print("\n" + "="*70)
    print("المصادر المتاحة:")
    print("="*70)
    
    source_list = list(sources.keys())
    for i, source_id in enumerate(source_list, 1):
        source = sources[source_id]
        print(f"{i}. {source['name']} ({source_id})")
    
    try:
        choice = int(input("\nاختر رقم المصدر: ")) - 1
        if 0 <= choice < len(source_list):
            source_id = source_list[choice]
            
            from test_article_scraping import test_source_scraping
            
            print(f"\n🔄 جاري سحب المقالات من {sources[source_id]['name']}...")
            success, articles = test_source_scraping(source_id, max_articles=3)
            
            if articles:
                print(f"\n✅ تم سحب {len(articles)} مقالة")
                for i, article in enumerate(articles, 1):
                    print(f"\n{i}. {article['title'][:60]}")
                    print(f"   الكلمات: {article['word_count']}")
                    print(f"   الحالة: {article['status']}")
            else:
                print("⚠️ لم يتم سحب أي مقالات")
        else:
            print("❌ رقم غير صحيح")
    except ValueError:
        print("❌ أدخل رقماً صحيحاً")


def show_statistics():
    """عرض الإحصائيات"""
    import json
    
    if not os.path.exists("scraped_articles.json"):
        print("❌ ملف scraped_articles.json غير موجود")
        print("   قم بسحب المقالات أولاً")
        return
    
    try:
        with open("scraped_articles.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("\n" + "="*70)
        print("📊 الإحصائيات")
        print("="*70)
        
        metadata = data['metadata']
        print(f"\nتاريخ السحب: {metadata['scraping_date']}")
        print(f"إجمالي المصادر: {metadata['total_sources']}")
        print(f"المصادر الناجحة: {metadata['successful_sources']}")
        print(f"المصادر الفاشلة: {metadata['failed_sources']}")
        print(f"نسبة النجاح: {metadata['success_rate']}")
        
        articles = data['articles']
        print(f"\nإجمالي المقالات: {len(articles)}")
        
        total_words = sum(a['word_count'] for a in articles)
        total_chars = sum(a['character_count'] for a in articles)
        
        print(f"إجمالي الكلمات: {total_words:,}")
        print(f"إجمالي الأحرف: {total_chars:,}")
        
        if articles:
            avg_words = total_words / len(articles)
            print(f"متوسط الكلمات: {avg_words:.0f}")
            
            # أطول وأقصر مقالة
            longest = max(articles, key=lambda x: x['word_count'])
            shortest = min(articles, key=lambda x: x['word_count'])
            
            print(f"\nأطول مقالة: {longest['source']} ({longest['word_count']} كلمة)")
            print(f"أقصر مقالة: {shortest['source']} ({shortest['word_count']} كلمة)")
        
        # إحصائيات حسب المصدر
        print(f"\n📰 إحصائيات حسب المصدر:")
        sources_stats = {}
        for article in articles:
            source = article['source']
            if source not in sources_stats:
                sources_stats[source] = {'count': 0, 'words': 0}
            sources_stats[source]['count'] += 1
            sources_stats[source]['words'] += article['word_count']
        
        for source, stats in sorted(sources_stats.items()):
            print(f"  {source}: {stats['count']} مقالة ({stats['words']} كلمة)")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")


def search_articles():
    """البحث عن مقالات"""
    import json
    
    if not os.path.exists("scraped_articles.json"):
        print("❌ ملف scraped_articles.json غير موجود")
        return
    
    try:
        with open("scraped_articles.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        search_term = input("\nأدخل كلمة البحث: ").strip()
        
        if not search_term:
            print("❌ أدخل كلمة بحث")
            return
        
        results = []
        for article in data['articles']:
            if (search_term.lower() in article['title'].lower() or
                search_term.lower() in article['full_text'].lower()):
                results.append(article)
        
        if results:
            print(f"\n✅ تم العثور على {len(results)} نتيجة:")
            for i, article in enumerate(results, 1):
                print(f"\n{i}. {article['title'][:60]}")
                print(f"   المصدر: {article['source']}")
                print(f"   الكلمات: {article['word_count']}")
                print(f"   الرابط: {article['url'][:60]}...")
        else:
            print(f"❌ لم يتم العثور على نتائج لـ '{search_term}'")
    
    except Exception as e:
        print(f"❌ خطأ: {e}")


def export_to_csv():
    """تصدير إلى CSV"""
    import json
    import csv
    
    if not os.path.exists("scraped_articles.json"):
        print("❌ ملف scraped_articles.json غير موجود")
        return
    
    try:
        with open("scraped_articles.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        filename = "articles_export.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['المصدر', 'العنوان', 'الكلمات', 'الأحرف', 'الحالة', 'الرابط'])
            
            for article in data['articles']:
                writer.writerow([
                    article['source'],
                    article['title'],
                    article['word_count'],
                    article['character_count'],
                    article['status'],
                    article['url']
                ])
        
        print(f"\n✅ تم التصدير بنجاح إلى: {filename}")
        print(f"   عدد الصفوف: {len(data['articles'])}")
    
    except Exception as e:
        print(f"❌ خطأ: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ تم الإيقاف من قبل المستخدم")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        sys.exit(1)
