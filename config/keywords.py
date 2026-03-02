"""
كلمات مفتاحية لفلترة أخبار إيران والتصعيد العسكري
مترجمة للعبرية والإنجليزية والعربية
"""

import re


def normalize_arabic(text: str) -> str:
    """
    تطبيع النص العربي - إزالة الهمزات والتشكيل
    
    Args:
        text: النص العربي
        
    Returns:
        النص المطبّع
    """
    # إزالة التشكيل (الفتحة، الضمة، الكسرة، السكون، إلخ)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    
    # توحيد الهمزات
    text = text.replace('أ', 'ا')  # أ → ا
    text = text.replace('إ', 'ا')  # إ → ا
    text = text.replace('آ', 'ا')  # آ → ا
    text = text.replace('ؤ', 'و')  # ؤ → و
    text = text.replace('ئ', 'ي')  # ئ → ي
    text = text.replace('ة', 'ه')  # ة → ه
    text = text.replace('ى', 'ي')  # ى → ي
    
    # إزالة المسافات الزائدة
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


# الطبقة الأولى: كلمات أساسية (يجب وجود واحدة منها على الأقل)
LAYER_1_KEYWORDS = {
    "ar": [
        # إيران - جميع الأشكال
        "إيران", "ايران", "ایران", "إيران",
        # طهران - جميع الأشكال
        "طهران", "طهرن", "تهران", "تهرن",
        # الحرس الثوري
        "الحرس الثوري", "الحرس الثورى", "حرس ثوري", "حرس ثورى",
        "IRGC", "irgc",
        # خامنئي - جميع الأشكال
        "خامنئي", "خامنئى", "خامنه", "خامنه اي", "خامنهاي",
        # المرشد الأعلى
        "المرشد الأعلى", "المرشد الاعلى", "مرشد أعلى", "مرشد اعلى",
        # إسرائيل - جميع الأشكال
        "إسرائيل", "اسرائيل", "إسرائيل", "اسرائيل",
        # إسرائيلي
        "إسرائيلي", "اسرائيلي", "إسرائيليين", "اسرائيليين",
        # لبنان
        "لبنان", "لبنن",
    ],
    "en": ["Iran", "Tehran", "IRGC", "Khamenei", "Supreme Leader", "Iranian", "Israel", "Israeli", "Lebanon"],
    "he": ["איראן", "טהראן", "IRGC", "המשמרות המהפכניים", "ח'אמנאי", "המנהיג העליון", "הנהגה איראנית", "ישראל", "ישראלי", "לבנון"]
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
    
    # تطبيع النص العربي (إزالة الهمزات والتشكيل)
    if language == "ar":
        text = normalize_arabic(text)
    
    # التحقق من الكلمات المستبعدة
    exclude_words = EXCLUDE_KEYWORDS.get(language, [])
    for word in exclude_words:
        if normalize_arabic(word.lower()) in text if language == "ar" else word.lower() in text:
            return False
    
    # الطبقة الأولى: كلمات أساسية (يجب وجود واحدة)
    layer_1_words = LAYER_1_KEYWORDS.get(language, [])
    layer_1_match = False
    for word in layer_1_words:
        normalized_word = normalize_arabic(word.lower()) if language == "ar" else word.lower()
        if normalized_word in text:
            layer_1_match = True
            break
    
    # الطبقة الثانية: أسماء العمليات
    layer_2_words = LAYER_2_KEYWORDS.get(language, [])
    layer_2_match = False
    for word in layer_2_words:
        normalized_word = normalize_arabic(word.lower()) if language == "ar" else word.lower()
        if normalized_word in text:
            layer_2_match = True
            break
    
    # الطبقة الثالثة: سياق موسّع
    layer_3_words = LAYER_3_KEYWORDS.get(language, [])
    layer_3_match = False
    for word in layer_3_words:
        normalized_word = normalize_arabic(word.lower()) if language == "ar" else word.lower()
        if normalized_word in text:
            layer_3_match = True
            break
    
    # المعادلة: (الطبقة_الأولى) OR (الطبقة_الثانية) OR (الطبقة_الثالثة AND الطبقة_الأولى)
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
    
    # تطبيع النص العربي
    if language == "ar":
        text = normalize_arabic(text)
    
    matched = []
    
    # البحث في جميع الطبقات
    all_keywords = (
        LAYER_1_KEYWORDS.get(language, []) +
        LAYER_2_KEYWORDS.get(language, []) +
        LAYER_3_KEYWORDS.get(language, [])
    )
    
    for keyword in all_keywords:
        normalized_keyword = normalize_arabic(keyword.lower()) if language == "ar" else keyword.lower()
        if normalized_keyword in text:
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
    
    # تطبيع النص العربي
    if language == "ar":
        text = normalize_arabic(text)
    
    # التحقق من الكلمات المستبعدة
    exclude_words = EXCLUDE_KEYWORDS.get(language, [])
    excluded = []
    for word in exclude_words:
        normalized_word = normalize_arabic(word.lower()) if language == "ar" else word.lower()
        if normalized_word in text:
            excluded.append(word)
    
    # الطبقة الأولى
    layer_1_words = LAYER_1_KEYWORDS.get(language, [])
    layer_1_match = []
    for word in layer_1_words:
        normalized_word = normalize_arabic(word.lower()) if language == "ar" else word.lower()
        if normalized_word in text:
            layer_1_match.append(word)
    
    # الطبقة الثانية
    layer_2_words = LAYER_2_KEYWORDS.get(language, [])
    layer_2_match = []
    for word in layer_2_words:
        normalized_word = normalize_arabic(word.lower()) if language == "ar" else word.lower()
        if normalized_word in text:
            layer_2_match.append(word)
    
    # الطبقة الثالثة
    layer_3_words = LAYER_3_KEYWORDS.get(language, [])
    layer_3_match = []
    for word in layer_3_words:
        normalized_word = normalize_arabic(word.lower()) if language == "ar" else word.lower()
        if normalized_word in text:
            layer_3_match.append(word)
    
    return {
        "language": language,
        "excluded": excluded,
        "layer_1": layer_1_match,
        "layer_2": layer_2_match,
        "layer_3": layer_3_match,
        "is_relevant": is_relevant_article(title, content, language)
    }
