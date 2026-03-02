-- إضافة source_type الجديد للإدخال من المستخدم
INSERT INTO public.source_type (id, name, description) VALUES 
    (5, 'user_input', 'إدخال من المستخدم')
ON CONFLICT (id) DO NOTHING;

-- إضافة المصادر الجديدة للإدخال من المستخدم
-- Source ID 7: Text (نص يدوي)
INSERT INTO public.sources (id, source_type_id, url, active) VALUES 
    (7, 5, 'text', true)
ON CONFLICT (url) DO NOTHING;

-- Source ID 5: Voice (صوت)
INSERT INTO public.sources (id, source_type_id, url, active) VALUES 
    (5, 5, 'voice', true)
ON CONFLICT (url) DO NOTHING;

-- Source ID 6: Video (فيديو)
INSERT INTO public.sources (id, source_type_id, url, active) VALUES 
    (6, 5, 'video', true)
ON CONFLICT (url) DO NOTHING;

-- التحقق من البيانات المضافة
SELECT * FROM public.source_type WHERE id = 5;
SELECT * FROM public.sources WHERE source_type_id = 5;
