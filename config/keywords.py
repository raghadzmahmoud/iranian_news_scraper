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
    ],
    "en": ["Iran", "Tehran", "IRGC", "Khamenei", "Supreme Leader", "Iranian", "Israel", "Israeli"],
    "he": ["איראן", "טהראן", "IRGC", "המשמרות המהפכניים", "ח'אמנאי", "המנהיג העליון", "הנהגה איראנית", "ישראל", "ישראלי"]
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
        # شخصيات إسرائيلية رئيسية
        "نتنياهو", "هرتسوغ", "بن غفير", "سموتريتش",
        # شخصيات عسكرية إسرائيلية
        "الرمتكال", "رئيس الأركان", "قائد الجيش",
        # تحالفات وأطراف معنية بالتصعيد (فقط المرتبطة بإيران)
        "محور المقاومة", "الحوثيون", "أنصار الله", "حزب الله", "كتائب حزب الله", "الحشد الشعبي",
        # أسلحة إيرانية محددة
        "صاروخ فتاح", "خيبر شكن", "صواريخ باليستية", "مسيّرات إيرانية",
        # مصطلحات عسكرية محددة
        "ضربة استباقية", "ضربة انتقامية", "تصعيد عسكري", "عملية عسكرية",
        # مواقع جغرافية ذات صلة بالتصعيد
        "لبنان", "الحدود الشمالية", "الجولان", "سوريا", "العراق",
        # مصطلحات نووية محددة
        "البرنامج النووي الإيراني", "تخصيب اليورانيوم", "نطنز", "فوردو"
    ],
    "en": [
        # Israeli political figures
        "Netanyahu", "Herzog", "Ben Gvir", "Smotrich",
        # Israeli military figures
        "IDF Chief", "Chief of Staff", "Army Commander",
        # Alliances and parties involved in escalation (Iran-related only)
        "Axis of Resistance", "Houthis", "Ansar Allah", "Hezbollah", "Kataib Hezbollah", "PMF", "PMU",
        # Specific Iranian weapons
        "Fattah missile", "Kheibar Shekan", "ballistic missiles", "Iranian drones",
        # Specific military terms
        "pre-emptive strike", "retaliatory strike", "military escalation", "military operation",
        # Geographic locations related to escalation
        "Lebanon", "northern border", "Golan", "Syria", "Iraq",
        # Specific nuclear terms
        "Iranian nuclear program", "uranium enrichment", "Natanz", "Fordow"
    ],
    "he": [
        # דמויות פוליטיות ישראליות
        "נתניהו", "הרצוג", "בן גביר", "סמוטריץ'",
        # דמויות צבאיות ישראליות
        "רמטכ\"ל", "ראש הצי", "מפקד הצבא",
        # ברית וצדדים המעורבים בהסלמה (קשורים לאיראן בלבד)
        "ציר ההתנגדות", "החות'ים", "אנצאר אללה", "חיזבאללה", "גדודי חיזבאללה", "כוחות עָם", "PMF", "PMU",
        # נשקים איראניים ספציפיים
        "טיל פטאח", "ח'יבר שקן", "טילים בליסטיים", "רחפנים איראניים",
        # מונחים צבאיים ספציפיים
        "תקיפה מונעת", "תקיפת נקמה", "הסלמה צבאית", "פעולה צבאית",
        # מיקומים גיאוגרפיים הקשורים להסלמה
        "לבנון", "הגבול הצפוני", "גולן", "סוריה", "עיראק",
        # מונחים גרעיניים ספציפיים
        "התוכנית הגרעינית האיראנית", "העשרת אורניום", "נאטנז", "פורדו"
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
    
    # المعادلة: (الطبقة_الأولى) OR (الطبقة_الثانية) OR (الطبقة_الثالثة)
    # كلمة واحدة من أي طبقة كافية
    return layer_1_match or layer_2_match or layer_3_match


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
