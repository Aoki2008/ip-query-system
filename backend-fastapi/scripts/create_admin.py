#!/usr/bin/env python3
"""
创建默认管理员用户脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.core.security import security
from app.core.logging import get_logger

logger = get_logger(__name__)

async def create_admin_user():
    """创建默认管理员用户"""
    try:
        # 检查是否已存在管理员用户
        existing_admin = await db_manager.get_user_by_username("admin")
        if existing_admin:
            print("✅ 管理员用户已存在")
            return True
        
        # 创建管理员用户数据
        import uuid
        admin_data = {
            'id': str(uuid.uuid4()),
            'username': 'admin',
            'email': 'admin@example.com',
            'password_hash': security.get_password_hash('admin123'),
            'full_name': '系统管理员',
            'is_active': True,
            'is_premium': True,
            'is_admin': True,
            'avatar_url': None
        }
        
        # 创建管理员用户
        admin_id = await db_manager.create_user(admin_data)
        if admin_id:
            print("✅ 管理员用户创建成功")
            print(f"   用户名: admin")
            print(f"   密码: admin123")
            print(f"   邮箱: admin@example.com")
            return True
        else:
            print("❌ 管理员用户创建失败")
            return False
            
    except Exception as e:
        logger.error(f"创建管理员用户失败: {e}")
        print(f"❌ 创建管理员用户失败: {e}")
        return False

async def main():
    """主函数"""
    print("🔧 正在创建默认管理员用户...")
    
    try:
        # 初始化数据库
        await db_manager.init_database()
        
        # 创建管理员用户
        success = await create_admin_user()
        
        if success:
            print("🎉 管理员用户设置完成！")
        else:
            print("💥 管理员用户设置失败！")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"脚本执行失败: {e}")
        print(f"💥 脚本执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
