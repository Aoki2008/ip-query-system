"""
SEO配置路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..admin.auth.dependencies import require_admin
from .models import (
    SeoConfigCreate, SeoConfigUpdate, SeoConfigResponse, 
    SeoPreview, SeoStats
)
from .service import SeoService

router = APIRouter(prefix="/api/admin/seo", tags=["SEO配置"])

@router.get("/config", response_model=SeoConfigResponse, summary="获取SEO配置")
async def get_seo_config(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """获取当前的SEO配置"""
    service = SeoService(db)
    config = service.get_seo_config()
    
    if not config:
        # 返回默认配置
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SEO配置不存在"
        )
    
    return config

@router.post("/config", response_model=SeoConfigResponse, summary="创建SEO配置")
async def create_seo_config(
    config: SeoConfigCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """创建或更新SEO配置"""
    service = SeoService(db)
    
    # 验证关键词
    if len(config.keywords) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关键词数量不能超过10个"
        )
    
    # 验证关键词唯一性
    if len(config.keywords) != len(set(config.keywords)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关键词不能重复"
        )
    
    db_config = service.create_seo_config(config)
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建SEO配置失败"
        )
    
    return db_config

@router.put("/config", response_model=SeoConfigResponse, summary="更新SEO配置")
async def update_seo_config(
    config: SeoConfigUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """更新SEO配置"""
    service = SeoService(db)
    
    # 验证关键词
    if config.keywords is not None:
        if len(config.keywords) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关键词数量不能超过10个"
            )
        
        if len(config.keywords) != len(set(config.keywords)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关键词不能重复"
            )
    
    db_config = service.update_seo_config(config)
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SEO配置不存在"
        )
    
    return db_config

@router.delete("/config", summary="删除SEO配置")
async def delete_seo_config(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """删除SEO配置"""
    service = SeoService(db)
    
    if not service.delete_seo_config():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SEO配置不存在"
        )
    
    return {"message": "SEO配置删除成功"}

@router.get("/preview", response_model=SeoPreview, summary="获取SEO预览")
async def get_seo_preview(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """获取SEO预览效果"""
    service = SeoService(db)
    preview = service.get_seo_preview()
    
    if not preview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SEO配置不存在"
        )
    
    return preview

@router.get("/stats", response_model=SeoStats, summary="获取SEO统计")
async def get_seo_stats(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """获取SEO统计信息"""
    service = SeoService(db)
    stats = service.get_seo_stats()
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SEO配置不存在"
        )
    
    return stats

@router.get("/keywords/suggestions", response_model=List[str], summary="获取关键词建议")
async def get_keyword_suggestions(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """获取关键词建议列表"""
    service = SeoService(db)
    return service.get_keyword_suggestions()

# 公开接口，用于前端获取SEO信息
@router.get("/public/config", response_model=SeoConfigResponse, summary="获取公开SEO配置")
async def get_public_seo_config(db: Session = Depends(get_db)):
    """获取公开的SEO配置，用于前端页面"""
    service = SeoService(db)
    config = service.get_seo_config()
    
    if not config:
        # 返回默认配置
        from .models import SeoConfig
        from datetime import datetime
        
        default_config = SeoConfig(
            id=0,
            title="IP查询工具 - 专业的IP地址查询服务",
            description="专业的IP地址查询工具，支持单个和批量查询，提供准确的地理位置信息、ISP信息和网络分析功能。",
            keywords=["IP查询", "IP地址查询", "地理位置", "网络工具"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return default_config
    
    return config
