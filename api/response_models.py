"""
موديلات الـ Response الموحدة
Unified Response Models
"""
from typing import Optional, Any, Dict, List
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """نموذج الـ Response الناجح"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """نموذج الـ Response الخاطئ"""
    success: bool = False
    error_code: str
    message: str
    details: Optional[str] = None


class APIResponse(BaseModel):
    """نموذج الـ Response الموحد"""
    status: int
    success: bool
    message: str
    error_code: Optional[str] = None
    data: Optional[Any] = None
    details: Optional[str] = None
