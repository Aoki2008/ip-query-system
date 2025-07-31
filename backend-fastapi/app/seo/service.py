"""
SEO配置服务层
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from .models import SeoConfig, SeoConfigCreate, SeoConfigUpdate, SeoPreview, SeoStats
import logging

logger = logging.getLogger(__name__)

class SeoService:
    """SEO配置服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_seo_config(self) -> Optional[SeoConfig]:
        """获取SEO配置"""
        try:
            return self.db.query(SeoConfig).first()
        except SQLAlchemyError as e:
            logger.error(f"获取SEO配置失败: {e}")
            return None
    
    def create_seo_config(self, config: SeoConfigCreate) -> Optional[SeoConfig]:
        """创建SEO配置"""
        try:
            # 检查是否已存在配置
            existing_config = self.get_seo_config()
            if existing_config:
                # 如果已存在，则更新
                return self.update_seo_config(SeoConfigUpdate(**config.dict()))
            
            db_config = SeoConfig(
                title=config.title,
                description=config.description,
                keywords=config.keywords
            )
            self.db.add(db_config)
            self.db.commit()
            self.db.refresh(db_config)
            return db_config
        except SQLAlchemyError as e:
            logger.error(f"创建SEO配置失败: {e}")
            self.db.rollback()
            return None
    
    def update_seo_config(self, config: SeoConfigUpdate) -> Optional[SeoConfig]:
        """更新SEO配置"""
        try:
            db_config = self.get_seo_config()
            if not db_config:
                return None
            
            update_data = config.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_config, field, value)
            
            self.db.commit()
            self.db.refresh(db_config)
            return db_config
        except SQLAlchemyError as e:
            logger.error(f"更新SEO配置失败: {e}")
            self.db.rollback()
            return None
    
    def delete_seo_config(self) -> bool:
        """删除SEO配置"""
        try:
            db_config = self.get_seo_config()
            if not db_config:
                return False
            
            self.db.delete(db_config)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"删除SEO配置失败: {e}")
            self.db.rollback()
            return False
    
    def generate_meta_tags(self, config: SeoConfig) -> str:
        """生成Meta标签"""
        keywords = ", ".join(config.keywords)
        meta_tags = f"""<title>{config.title}</title>
<meta name="description" content="{config.description}" />
<meta name="keywords" content="{keywords}" />
<meta property="og:title" content="{config.title}" />
<meta property="og:description" content="{config.description}" />
<meta property="og:type" content="website" />
<meta name="twitter:card" content="summary" />
<meta name="twitter:title" content="{config.title}" />
<meta name="twitter:description" content="{config.description}" />"""
        return meta_tags
    
    def get_seo_preview(self) -> Optional[SeoPreview]:
        """获取SEO预览"""
        config = self.get_seo_config()
        if not config:
            return None
        
        meta_tags = self.generate_meta_tags(config)
        return SeoPreview(
            title=config.title,
            description=config.description,
            keywords=config.keywords,
            meta_tags=meta_tags
        )
    
    def get_seo_stats(self) -> Optional[SeoStats]:
        """获取SEO统计信息"""
        config = self.get_seo_config()
        if not config:
            return None
        
        title_length = len(config.title)
        description_length = len(config.description)
        keywords_count = len(config.keywords)
        
        # 评估状态
        title_status = self._evaluate_title_status(title_length)
        description_status = self._evaluate_description_status(description_length)
        keywords_status = self._evaluate_keywords_status(keywords_count)
        
        # 计算总体评分
        overall_score = self._calculate_overall_score(
            title_status, description_status, keywords_status
        )
        
        return SeoStats(
            title_length=title_length,
            description_length=description_length,
            keywords_count=keywords_count,
            title_status=title_status,
            description_status=description_status,
            keywords_status=keywords_status,
            overall_score=overall_score
        )
    
    def _evaluate_title_status(self, length: int) -> str:
        """评估标题状态"""
        if length < 10:
            return "too_short"
        elif length <= 60:
            return "good"
        else:
            return "too_long"
    
    def _evaluate_description_status(self, length: int) -> str:
        """评估描述状态"""
        if length < 50:
            return "too_short"
        elif length <= 160:
            return "good"
        else:
            return "too_long"
    
    def _evaluate_keywords_status(self, count: int) -> str:
        """评估关键词状态"""
        if count == 0:
            return "none"
        elif count < 5:
            return "few"
        elif count <= 10:
            return "good"
        else:
            return "too_many"
    
    def _calculate_overall_score(self, title_status: str, description_status: str, keywords_status: str) -> int:
        """计算总体评分"""
        score = 0
        
        # 标题评分 (40%)
        if title_status == "good":
            score += 40
        elif title_status == "too_short":
            score += 20
        else:  # too_long
            score += 30
        
        # 描述评分 (40%)
        if description_status == "good":
            score += 40
        elif description_status == "too_short":
            score += 20
        else:  # too_long
            score += 30
        
        # 关键词评分 (20%)
        if keywords_status == "good":
            score += 20
        elif keywords_status == "few":
            score += 15
        elif keywords_status == "none":
            score += 0
        else:  # too_many
            score += 10
        
        return score
    
    def get_keyword_suggestions(self) -> List[str]:
        """获取关键词建议"""
        return [
            "IP查询", "IP地址查询", "地理位置查询", "网络工具",
            "IP定位", "批量IP查询", "IP地址定位", "网络分析",
            "ISP查询", "IP归属地", "网络诊断", "IP工具",
            "网络安全", "IP追踪", "地理定位", "网络监控"
        ]
