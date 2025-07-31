#!/usr/bin/env python3
"""
数据库迁移脚本：添加is_admin字段到users表
"""
import sqlite3
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_database():
    """执行数据库迁移"""
    db_path = "./data/admin.db"
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查is_admin列是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' in columns:
            print("✅ is_admin列已存在，无需迁移")
            return True
        
        print("🔧 开始添加is_admin列...")
        
        # 添加is_admin列
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        
        # 检查是否有admin用户，如果有则设置为管理员
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            cursor.execute("UPDATE users SET is_admin = 1 WHERE username = 'admin'")
            print("✅ 已将admin用户设置为管理员")
        
        # 提交更改
        conn.commit()
        print("✅ 数据库迁移完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

def main():
    """主函数"""
    print("🔧 开始数据库迁移：添加is_admin字段")
    
    success = migrate_database()
    
    if success:
        print("🎉 数据库迁移成功完成！")
    else:
        print("💥 数据库迁移失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
