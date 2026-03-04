"""
إدراج المصادر في قاعدة البيانات
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT', '5432')

def connect_db():
    """الاتصال بقاعدة البيانات"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode='require'
        )
        print(f"✅ تم الاتصال بـ {DB_NAME}")
        return conn
    except psycopg2.Error as e:
        print(f"❌ خطأ: {e}")
        return None

def insert_languages(conn):
    """إدراج اللغات"""
    cursor = conn.cursor()
    
    try:
        print("\n🌐 إدراج اللغات...")
        
        query = """
            INSERT INTO public.languages (code, name) VALUES 
                ('ar', 'Arabic'),
                ('en', 'English'),
                ('he', 'Hebrew')
            ON CONFLICT (code) DO NOTHING;
        """
        
        cursor.execute(query)
        conn.commit()
        
        cursor.execute("SELECT * FROM public.languages")
        langs = cursor.fetchall()
        print(f"✅ {len(langs)} لغة")
        
        return True
    
    except psycopg2.Error as e:
        print(f"❌ خطأ: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def insert_source_types(conn):
    """إدراج أنواع المصادر"""
    cursor = conn.cursor()
    
    try:
        print("\n📌 إدراج أنواع المصادر...")
        
        query = """
            INSERT INTO public.source_types (name, description) VALUES 
                ('full_scrape', 'مواقع يتم سحب الخبر الكامل منها (300+ كلمة)'),
                ('rss_only', 'مواقع يتم سحب الملخص من RSS فقط')
            ON CONFLICT (name) DO NOTHING;
        """
        
        cursor.execute(query)
        conn.commit()
        
        cursor.execute("SELECT * FROM public.source_types WHERE name IN ('full_scrape', 'rss_only')")
        types = cursor.fetchall()
        print(f"✅ {len(types)} نوع مصدر")
        
        return True
    
    except psycopg2.Error as e:
        print(f"❌ خطأ: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def insert_sources(conn):
    """إدراج المصادر"""
    cursor = conn.cursor()
    
    sources = [
        # Full Scrape (8)
        ('full_scrape', 'Ynet', 'https://www.ynet.co.il/Integration/StoryRss2.xml'),
        ('full_scrape', 'Walla', 'https://rss.walla.co.il/feed/1'),
        ('full_scrape', 'Maariv', 'https://www.maariv.co.il/Rss/RssChadashot'),
        ('full_scrape', 'BBC Arabic', 'https://feeds.bbci.co.uk/arabic/rss.xml'),
        ('full_scrape', 'Deutsche Welle Arabic', 'https://rss.dw.com/rdf/rss-ar-all'),
        ('full_scrape', 'BBC Politics', 'https://feeds.bbci.co.uk/news/politics/rss.xml'),
        ('full_scrape', 'Al Jazeera', 'https://www.aljazeera.com/xml/rss/all.xml'),
        ('full_scrape', 'Al-Sharq', 'https://al-sharq.com/rss/latestNews'),
        
        # RSS Only (8)
        ('rss_only', 'France24 Arabic', 'https://www.france24.com/ar/%D8%A7%D9%84%D8%B4%D8%B1%D9%82-%D8%A7%D9%84%D8%A3%D9%88%D8%B3%D8%B7/rss'),
        ('rss_only', 'Asharq Al-Awsat', 'https://aawsat.com/feed/arab-world'),
        ('rss_only', 'Al-Quds Al-Arabi', 'https://www.alquds.co.uk/feed/'),
        ('rss_only', 'New York Times Politics', 'https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml'),
        ('rss_only', 'CNN World', 'http://rss.cnn.com/rss/edition_world.rss'),
        ('rss_only', 'RSS App Feed 1', 'https://rss.app/feeds/N7N49HNSJv8hyFnC.xml'),
        ('rss_only', 'RSS App Feed 2', 'https://rss.app/feeds/tUPHvh2ed2cgzSw2.xml'),
        ('rss_only', 'RSS App Feed 3', 'https://rss.app/feeds/1RLQecU83zmiCNY4.xml'),
    ]
    
    try:
        print("\n📡 إدراج المصادر...")
        
        inserted = 0
        
        for source_type, name, url in sources:
            query = """
                INSERT INTO public.sources (source_type_id, name, url, is_active) 
                SELECT id, %s, %s, true
                FROM public.source_types 
                WHERE name = %s
                ON CONFLICT (url) DO NOTHING
                RETURNING id;
            """
            
            cursor.execute(query, (name, url, source_type))
            result = cursor.fetchone()
            
            if result:
                inserted += 1
        
        conn.commit()
        print(f"✅ {inserted} مصدر جديد")
        
        return True
    
    except psycopg2.Error as e:
        print(f"❌ خطأ: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def verify_data(conn):
    """التحقق من البيانات"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("\n" + "="*60)
        print("📊 التحقق من البيانات")
        print("="*60)
        
        cursor.execute("""
            SELECT st.name as type, COUNT(s.id) as count
            FROM public.source_types st
            LEFT JOIN public.sources s ON st.id = s.source_type_id
            GROUP BY st.name
            ORDER BY st.name
        """)
        
        for row in cursor.fetchall():
            print(f"   {row['type']}: {row['count']} مصدر")
        
        print("="*60)
        
    except psycopg2.Error as e:
        print(f"❌ خطأ: {e}")
    finally:
        cursor.close()

def main():
    """الدالة الرئيسية"""
    print("\n" + "="*60)
    print("🚀 إدراج البيانات في قاعدة البيانات")
    print("="*60)
    
    conn = connect_db()
    if not conn:
        return False
    
    try:
        if not insert_languages(conn):
            return False
        
        if not insert_source_types(conn):
            return False
        
        if not insert_sources(conn):
            return False
        
        verify_data(conn)
        
        print("\n✅ انتهى بنجاح!")
        return True
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
