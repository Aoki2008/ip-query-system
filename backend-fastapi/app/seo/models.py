"""
SEO配置数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from ..database import Base

class SeoConfig(Base):
    """SEO配置数据库模型"""
    __tablename__ = "seo_config"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="网站标题")
    description = Column(Text, nullable=False, comment="网站描述")
    keywords = Column(JSON, nullable=False, default=[], comment="关键词列表")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

class SeoConfigCreate(BaseModel):
    """创建SEO配置的请求模型"""
    title: str = Field(..., min_length=10, max_length=60, description="网站标题")
    description: str = Field(..., min_length=50, max_length=160, description="网站描述")
    keywords: List[str] = Field(default=[], max_items=10, description="关键词列表")

class SeoConfigUpdate(BaseModel):
    """更新SEO配置的请求模型"""
    title: Optional[str] = Field(None, min_length=10, max_length=60, description="网站标题")
    description: Optional[str] = Field(None, min_length=50, max_length=160, description="网站描述")
    keywords: Optional[List[str]] = Field(None, max_items=10, description="关键词列表")

class SeoConfigResponse(BaseModel):
    """SEO配置响应模型"""
    id: int
    title: str
    description: str
    keywords: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SeoPreview(BaseModel):
    """SEO预览模型"""
    title: str
    description: str
    keywords: List[str]
    meta_tags: str
    
class SeoStats(BaseModel):
    """SEO统计模型"""
    title_length: int
    description_length: int
    keywords_count: int
    title_status: str
    description_status: str
    keywords_status: str
    overall_score: int
