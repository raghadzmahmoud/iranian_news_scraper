#!/usr/bin/env python
"""
Quick test to verify X scraper setup
اختبار سريع للتحقق من إعدادات السحب من X
"""
import sys
import os
from pathlib import Path

print("=" * 60)
print("🔍 X Scraper Setup Verification")
print("=" * 60)

# Check Python version
print(f"\n✅ Python version: {sys.version}")

# Check required packages
print("\n📦 Checking required packages...")
required_packages = [
    'playwright',
    'psycopg2',
    'python-dotenv',
    'requests',
    'aiohttp',
]

missing = []
for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} - MISSING")
        missing.append(package)

if missing:
    print(f"\n⚠️  Missing packages: {', '.join(missing)}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Check .env file
print("\n📝 Checking .env file...")
if os.path.exists('.env'):
    print("   ✅ .env file exists")
    
    # Check required env vars
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'X_USERNAME',
        'X_PASSWORD',
        'DB_HOST',
        'DB_USER',
        'DB_PASSWORD',
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:3] + '*' * (len(value) - 6) if len(value) > 6 else '***'
            print(f"   ✅ {var} = {masked}")
        else:
            print(f"   ❌ {var} - NOT SET")
else:
    print("   ❌ .env file not found")
    sys.exit(1)

# Check Chrome profile directory
print("\n🌐 Checking Chrome profile directory...")
profile_dir = os.getenv('X_CHROME_PROFILE_DIR', 'media/playwright_profile')
if os.path.exists(profile_dir):
    print(f"   ✅ {profile_dir} exists")
else:
    print(f"   ℹ️  {profile_dir} will be created on first run")

# Check database connection
print("\n🗄️  Checking database connection...")
try:
    from database.connection import db
    if not db.conn:
        db.connect()
    
    cursor = db.conn.cursor()
    cursor.execute("SELECT 1")
    print("   ✅ Database connection successful")
    
    # Check X sources
    cursor.execute("""
        SELECT COUNT(*) FROM public.sources 
        WHERE source_type_id = 7 AND is_active = true
    """)
    count = cursor.fetchone()[0]
    print(f"   ✅ Found {count} active X sources")
    
except Exception as e:
    print(f"   ❌ Database connection failed: {e}")
    sys.exit(1)

# Check Playwright
print("\n🎭 Checking Playwright...")
try:
    from playwright.async_api import async_playwright
    print("   ✅ Playwright installed")
except ImportError:
    print("   ❌ Playwright not installed")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All checks passed! Ready to run X scraper")
print("=" * 60)
print("\n🚀 To start scraping, run:")
print("   python run_x_scraper_local.py")
print("\nOr use the setup script:")
print("   Linux/Mac: ./setup_and_run.sh")
print("   Windows:   setup_and_run.bat")
