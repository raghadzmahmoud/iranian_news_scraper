"""
نموذج المقالة
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NewsArticle:
    """نموذج بيانات المقالة الإخبارية"""
    source: str
    title: str
    url: str
    pub_date: str
    summary: str
    image_url: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    full_text: Optional[str] = None
    paragraphs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """تحويل المقالة إلى قاموس"""
        return {
            "source": self.source,
            "title": self.title,
            "url": self.url,
            "pub_date": self.pub_date,
            "image_url": self.image_url,
            "tags": self.tags,
            "summary": self.summary,
            "full_text": self.full_text,
            "paragraphs": self.paragraphs,
        }
