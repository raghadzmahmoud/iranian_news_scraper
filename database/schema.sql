-- جدول أنواع المصادر
CREATE TABLE IF NOT EXISTS public.source_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- جدول المصادر
CREATE TABLE IF NOT EXISTS public.sources (
    id BIGSERIAL PRIMARY KEY,
    source_type_id INTEGER NOT NULL REFERENCES public.source_type(id),
    url TEXT NOT NULL UNIQUE,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- جدول البيانات الخام
CREATE TABLE IF NOT EXISTS public.raw_data (
    id BIGSERIAL PRIMARY KEY,
    source_id BIGINT NOT NULL REFERENCES public.sources(id),
    url TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMP WITH TIME ZONE,
    media_url TEXT,
    stt_status VARCHAR(50) DEFAULT 'pending',
    source_type_id INTEGER NOT NULL REFERENCES public.source_type(id),
    tags TEXT,
    original_language VARCHAR(10) DEFAULT 'he',
    arabic_content TEXT,
    translation_status VARCHAR(50),
    translated_at TIMESTAMP WITH TIME ZONE,
    translation_error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- إدراج أنواع المصادر
INSERT INTO public.source_type (name, description) VALUES 
    ('RSS', 'مصدر RSS Feed'),
    ('API', 'مصدر API'),
    ('Web Scraping', 'سحب من الويب')
ON CONFLICT DO NOTHING;

-- إدراج المصادر الافتراضية
INSERT INTO public.sources (source_type_id, url, active) VALUES 
    (1, 'https://www.ynet.co.il/Integration/StoryRss2.xml', true),
    (1, 'https://rss.walla.co.il/feed/1', true),
    (1, 'https://www.maariv.co.il/Rss/RssChadashot', true)
ON CONFLICT DO NOTHING;

-- إنشاء فهارس للأداء
CREATE INDEX IF NOT EXISTS idx_raw_data_source_id ON public.raw_data(source_id);
CREATE INDEX IF NOT EXISTS idx_raw_data_fetched_at ON public.raw_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_raw_data_is_processed ON public.raw_data(is_processed);
CREATE INDEX IF NOT EXISTS idx_raw_data_url ON public.raw_data(url);
