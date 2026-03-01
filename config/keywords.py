"""
كلمات مفتاحية لفلترة أخبار إيران والتصعيد العسكري
مترجمة للعبرية والإنجليزية والعربية
"""

# الطبقة الأولى: كلمات أساسية (يجب وجود واحدة منها على الأقل)
LAYER_1_KEYWORDS = {
    "ar": ["إيران", "طهران", "الحرس الثوري", "IRGC", "خامنئي", "المرشد الأعلى"],
    "en": ["Iran", "Tehran", "IRGC", "Khamenei", "Supreme Leader", "Iranian"],
    "he": ["איראן", "טהראן", "IRGC", "המשמרות המהפכניים", "ח'אמנאי", "המנהיג העליון", "הנהגה איראנית"]
}

# الطبقة الثانية: أسماء العمليات العسكرية
LAYER_2_KEYWORDS = {
    "ar": [
        # عمليات إسرائيلية
        "زئير الأسد", "شاغات هآري", "درع يهودا", "الأسد الصاعد",
        # عمليات أمريكية
        "الغضب الملحمي", "مطرقة منتصف الليل",
        # عمليات إيرانية
        "الوعد الصادق", "الوعد الصادق 4", "فاتح خيبر", "فتح خيبر", "بشارة الفتح"
    ],
    "en": [
        # Israeli operations
        "Lion's Roar", "Roaring Lion", "Shield of Judah", "Rising Lion",
        # American operations
        "Epic Fury", "Midnight Hammer",
        # Iranian operations
        "True Promise", "True Promise 4", "Fateh Khyber", "Fatah Khyber", "Besharat al-Fath"
    ],
    "he": [
        # עמליות ישראליות
        "שאגת האריה", "מגן יהודה", "האריה העולה",
        # עמליות אמריקאיות
        "מבצע זעם אפי", "פטיש חצות",
        # עמליות איראניות
        "ההבטחה הנאמנה", "ההבטחה הנאמנה 4", "כובש ח'יבר", "בשארת אל-פתח"
    ]
}

# الطبقة الثالثة: سياق موسّع
LAYER_3_KEYWORDS = {
    "ar": [
        # شخصيات
        "نتنياهو", "هرتسوغ", "إبراهيم جباري", "ترامب",
        # تحالفات
        "محور المقاومة", "الحوثيون", "أنصار الله", "حزب الله", "كتائب حزب الله", "الحشد الشعبي",
        # مواقع نووية
        "نطنز", "فوردو", "أصفهان", "بارشين", "كرج", "كرمانشاه",
        # أسلحة
        "صاروخ فتاح", "خيبر شكن", "صواريخ باليستية", "صواريخ فرط صوتية", "مسيّرات",
        # مصطلحات
        "ضربة استباقية", "ضربة انتقامية", "حرب شاملة", "تصعيد إقليمي", "البرنامج النووي",
        "تخصيب اليورانيوم", "مضيق هرمز", "حيفا"
    ],
    "en": [
        # Personalities
        "Netanyahu", "Herzog", "Jabbari", "Trump", "Pentagon",
        # Alliances
        "Axis of Resistance", "Houthis", "Ansar Allah", "Hezbollah", "Kataib Hezbollah", "PMF", "PMU",
        # Nuclear sites
        "Natanz", "Fordow", "Isfahan", "Parchin", "Karaj", "Kermanshah",
        # Weapons
        "Fattah", "Kheibar Shekan", "ballistic missiles", "hypersonic missiles", "drones", "UAV",
        "B-2 bombers", "bunker busters", "cruise missiles", "Iron Dome", "F-35",
        # Terms
        "pre-emptive strike", "retaliatory strike", "all-out war", "regional escalation", "nuclear program",
        "uranium enrichment", "Strait of Hormuz", "Haifa"
    ],
    "he": [
        # אישיויות
        "נתניהו", "הרצוג", "ג'בארי", "טראמפ", "הפנטגון",
        # ברית
        "ציר ההתנגדות", "החות'ים", "אנצאר אללה", "חיזבאללה", "גדודי חיזבאללה", "כוחות עָם", "PMF", "PMU",
        # אתרים גרעיניים
        "נאטנז", "פורדו", "אספהאן", "פארצ'ין", "קראג'", "כרמאנסאה",
        # נשקים
        "טיל פטאח", "ח'יבר שקן", "טילים בליסטיים", "טילים על-קוליים", "רחפנים", "UAV",
        "מפציצי B-2", "פצצות חודרות מבצרים", "טילי קרוז", "כיפת ברזל", "מטוסי קרב F-35",
        # מונחים
        "תקיפה מונעת", "תקיפת נקמה", "מלחמה כוללת", "הסלמה אזורית", "תוכנית הגרעין האיראנית",
        "העשרת אורניום", "מיצר הורמוז", "חיפה",
        # מדינות ובסיסים
        "קטאר", "בחרייןן", "כוויתן", "איחוד האמירויות", "בסיס אל-אודיד", "בסיסים אמריקאיים", "מדינות המפרץ"
    ]
}

# كلمات يجب استبعادها (false positives)
EXCLUDE_KEYWORDS = {
    "ar": ["ايران الآن", "إيران اليوم", "إيران الرياضة", "إيران الفن", "إيران إير", "تيران"],
    "en": ["Iran Air", "Iran tourism", "Iran culture", "Iran sports"],
    "he": ["תיירות איראן", "ספורט איראן", "תרבות איראן", "אייר איראן"]
}


def is_relevant_article(title: str, content: str, language: str = "he") -> bool:
    """
    التحقق من أن المقالة متعلقة بإيران والتصعيد العسكري
    
    Args:
        title: عنوان المقالة
        content: محتوى المقالة
        language: اللغة (he, en, ar)
    
    Returns:
        True إذا كانت المقالة ذات صلة
    """
    text = (title + " " + content).lower()
    
    # التحقق من الكلمات المستبعدة
    exclude_words = EXCLUDE_KEYWORDS.get(language, [])
    for word in exclude_words:
        if word.lower() in text:
            return False
    
    # الطبقة الأولى: كلمات أساسية (يجب وجود واحدة)
    layer_1_words = LAYER_1_KEYWORDS.get(language, [])
    layer_1_match = any(word.lower() in text for word in layer_1_words)
    
    # الطبقة الثانية: أسماء العمليات
    layer_2_words = LAYER_2_KEYWORDS.get(language, [])
    layer_2_match = any(word.lower() in text for word in layer_2_words)
    
    # الطبقة الثالثة: سياق موسّع
    layer_3_words = LAYER_3_KEYWORDS.get(language, [])
    layer_3_match = any(word.lower() in text for word in layer_3_words)
    
    # المعادلة: (الطبقة_الأولى) OR (الطبقة_الثانية) OR (الطبقة_الثالثة)
    return layer_1_match or layer_2_match or (layer_3_match and layer_1_match)


def get_matching_keywords(title: str, content: str, language: str = "he") -> list:
    """
    الحصول على الكلمات المفتاحية المطابقة
    
    Args:
        title: عنوان المقالة
        content: محتوى المقالة
        language: اللغة
    
    Returns:
        قائمة الكلمات المطابقة
    """
    text = (title + " " + content).lower()
    matched = []
    
    # البحث في جميع الطبقات
    all_keywords = (
        LAYER_1_KEYWORDS.get(language, []) +
        LAYER_2_KEYWORDS.get(language, []) +
        LAYER_3_KEYWORDS.get(language, [])
    )
    
    for keyword in all_keywords:
        if keyword.lower() in text:
            matched.append(keyword)
    
    return matched


def debug_filter(title: str, content: str, language: str = "he") -> dict:
    """
    دالة debug لطباعة تفاصيل الفلترة
    
    Args:
        title: عنوان المقالة
        content: محتوى المقالة
        language: اللغة
    
    Returns:
        dict بتفاصيل الفلترة
    """
    text = (title + " " + content).lower()
    
    # التحقق من الكلمات المستبعدة
    exclude_words = EXCLUDE_KEYWORDS.get(language, [])
    excluded = [word for word in exclude_words if word.lower() in text]
    
    # الطبقة الأولى
    layer_1_words = LAYER_1_KEYWORDS.get(language, [])
    layer_1_match = [word for word in layer_1_words if word.lower() in text]
    
    # الطبقة الثانية
    layer_2_words = LAYER_2_KEYWORDS.get(language, [])
    layer_2_match = [word for word in layer_2_words if word.lower() in text]
    
    # الطبقة الثالثة
    layer_3_words = LAYER_3_KEYWORDS.get(language, [])
    layer_3_match = [word for word in layer_3_words if word.lower() in text]
    
    return {
        "language": language,
        "excluded": excluded,
        "layer_1": layer_1_match,
        "layer_2": layer_2_match,
        "layer_3": layer_3_match,
        "is_relevant": is_relevant_article(title, content, language)
    }
