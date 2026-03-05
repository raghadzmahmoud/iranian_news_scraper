"""
كاشف الأرقام المحسّن - يدعم العربية والإنجليزية والعبرية
مع دعم المثنى والجمع والسياق الحربي
"""
import re


class NumberDetector:
    """كاشف الأرقام المحسّن"""
    
    # أنماط الأرقام الأساسية
    ENGLISH_DIGITS = r'\d'
    ARABIC_DIGITS = r'[٠-٩]'
    
    # أنماط الكلمات الحربية بالعربية (مع المثنى والجمع)
    ARABIC_WAR_PATTERNS = [
        # صاروخ/صواريخ/صاروخين
        r'\d+\s*(صاروخ|صواريخ|صاروخين|صاروخا)',
        # قتيل/قتلى/قتيلين
        r'\d+\s*(قتيل|قتلى|قتيلين|قتيلا)',
        # جريح/جرحى/جريحين
        r'\d+\s*(جريح|جرحى|جريحين|جريحا)',
        # مصاب/مصابين/مصابة
        r'\d+\s*(مصاب|مصابين|مصابة|مصابات)',
        # طائرة/طائرات/طائرتين
        r'\d+\s*(طائرة|طائرات|طائرتين)',
        # مسيرة/مسيرات/مسيرتين (درون)
        r'\d+\s*(مسيرة|مسيرات|مسيرتين)',
        # غارة/غارات/غارتين
        r'\d+\s*(غارة|غارات|غارتين)',
        # ضربة/ضربات/ضربتين
        r'\d+\s*(ضربة|ضربات|ضربتين)',
        # جندي/جنود/جنديين
        r'\d+\s*(جندي|جنود|جنديين)',
        # عسكري/عسكريين/عسكريون
        r'\d+\s*(عسكري|عسكريين|عسكريون)',
        # قتل/مقتل/قتلوا
        r'(قتل|مقتل|قتلوا|قتلن)\s+\d+',
        # أصيب/جرح/أصابوا
        r'(أصيب|جرح|أصابوا|جرحوا|أصابن|جرحن)\s+\d+',
        # دمّر/دمّرت/دمّروا
        r'(دمّر|دمّرت|دمّروا|دمّرن)\s+\d+',
        # أسر/أسروا/أسرن
        r'(أسر|أسروا|أسرن)\s+\d+',
    ]
    
    # أنماط الكلمات الحربية بالإنجليزية (مع المثنى والجمع)
    ENGLISH_WAR_PATTERNS = [
        # missile/missiles
        r'\d+\s*(missile|missiles)',
        # killed/dead/deaths
        r'\d+\s*(killed|dead|deaths|casualty|casualties)',
        # injured/wounded/injuries
        r'\d+\s*(injured|wounded|injuries|hurt)',
        # aircraft/planes/jets
        r'\d+\s*(aircraft|plane|planes|jet|jets|drone|drones)',
        # strike/strikes/raid/raids
        r'\d+\s*(strike|strikes|raid|raids|attack|attacks)',
        # soldier/soldiers
        r'\d+\s*(soldier|soldiers)',
        # military/troops
        r'\d+\s*(military|troops|troop)',
        # killed/died/died
        r'(killed|died|died)\s+\d+',
        # injured/wounded
        r'(injured|wounded)\s+\d+',
        # destroyed/destroyed
        r'(destroyed|destroyed)\s+\d+',
        # captured/captured
        r'(captured|captured)\s+\d+',
    ]
    
    # אנماط الكلمات الحربية بالعبرية (مع المثنى والجمع)
    HEBREW_WAR_PATTERNS = [
        # טיל/טילים/טילי
        r'\d+\s*(טיל|טילים|טילי)',
        # הרוג/הרוגים/הרוגות
        r'\d+\s*(הרוג|הרוגים|הרוגות)',
        # פצוע/פצועים/פצועות
        r'\d+\s*(פצוע|פצועים|פצועות)',
        # חייל/חיילים
        r'\d+\s*(חייל|חיילים)',
        # מטוס/מטוסים
        r'\d+\s*(מטוס|מטוסים)',
        # רחפן/רחפנים
        r'\d+\s*(רחפן|רחפנים)',
        # התקפה/התקפות
        r'\d+\s*(התקפה|התקפות)',
        # הכה/הכו/הכתה
        r'(הכה|הכו|הכתה)\s+\d+',
        # פגע/פגעו/פגעה
        r'(פגע|פגעו|פגעה)\s+\d+',
        # הרג/הרגו/הרגה
        r'(הרג|הרגו|הרגה)\s+\d+',
    ]
    
    @staticmethod
    def has_basic_numbers(text: str) -> bool:
        """
        التحقق من وجود أرقام أساسية (إنجليزية أو عربية)
        
        Args:
            text: النص المراد فحصه
        
        Returns:
            True إذا كان هناك أرقام
        """
        if not text:
            return False
        
        has_english = bool(re.search(NumberDetector.ENGLISH_DIGITS, text))
        has_arabic = bool(re.search(NumberDetector.ARABIC_DIGITS, text))
        
        return has_english or has_arabic
    
    @staticmethod
    def has_war_context_numbers(text: str) -> bool:
        """
        التحقق من وجود أرقام في سياق حربي
        
        Args:
            text: النص المراد فحصه
        
        Returns:
            True إذا كان هناك أرقام في سياق حربي
        """
        if not text:
            return False
        
        # فحص الأنماط العربية
        for pattern in NumberDetector.ARABIC_WAR_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # فحص الأنماط الإنجليزية
        for pattern in NumberDetector.ENGLISH_WAR_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # فحص الأنماط العبرية
        for pattern in NumberDetector.HEBREW_WAR_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def detect_numbers(text: str, use_war_context: bool = True) -> dict:
        """
        كشف شامل للأرقام مع معلومات تفصيلية
        
        Args:
            text: النص المراد فحصه
            use_war_context: هل نستخدم السياق الحربي (الافتراضي: True)
        
        Returns:
            قاموس بمعلومات الأرقام:
            {
                'has_numbers': bool,
                'has_basic_numbers': bool,
                'has_war_context': bool,
                'english_digits': list,
                'arabic_digits': list,
                'war_matches': list
            }
        """
        if not text:
            return {
                'has_numbers': False,
                'has_basic_numbers': False,
                'has_war_context': False,
                'english_digits': [],
                'arabic_digits': [],
                'war_matches': []
            }
        
        # البحث عن الأرقام الأساسية
        english_digits = re.findall(NumberDetector.ENGLISH_DIGITS, text)
        arabic_digits = re.findall(NumberDetector.ARABIC_DIGITS, text)
        
        has_basic = bool(english_digits or arabic_digits)
        
        # البحث عن السياق الحربي
        has_war = False
        war_matches = []
        
        if use_war_context:
            # فحص الأنماط العربية
            for pattern in NumberDetector.ARABIC_WAR_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    has_war = True
                    war_matches.extend(matches)
            
            # فحص الأنماط الإنجليزية
            for pattern in NumberDetector.ENGLISH_WAR_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    has_war = True
                    war_matches.extend(matches)
            
            # فحص الأنماط العبرية
            for pattern in NumberDetector.HEBREW_WAR_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    has_war = True
                    war_matches.extend(matches)
        
        return {
            'has_numbers': has_basic or has_war,
            'has_basic_numbers': has_basic,
            'has_war_context': has_war,
            'english_digits': english_digits,
            'arabic_digits': arabic_digits,
            'war_matches': war_matches
        }
