"""
数据库连接和管理模块
使用SQLite作为默认数据库，支持扩展到PostgreSQL
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio
from contextlib import asynccontextmanager

from app.core.logging import get_logger
from app.models.user import UserInDB
from app.models.auth import SessionInfo

logger = get_logger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 自动检测数据库路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(os.path.dirname(current_dir))
            db_path = os.path.join(backend_dir, "data", "ip_query.db")

        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        # 确保数据目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 创建表
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            
            # 用户表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    avatar_url TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    is_premium BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login_at TIMESTAMP
                )
            """)
            
            # 用户设置表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id TEXT PRIMARY KEY,
                    theme TEXT DEFAULT 'auto',
                    language TEXT DEFAULT 'zh-CN',
                    timezone TEXT DEFAULT 'Asia/Shanghai',
                    email_notifications BOOLEAN DEFAULT 1,
                    history_retention_days INTEGER DEFAULT 90,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # 查询历史表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    ip_address TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    result_data TEXT,
                    query_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_time REAL,
                    success BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
                )
            """)
            
            # 会话表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # API密钥表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    key_name TEXT NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    rate_limit INTEGER DEFAULT 1000,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_query_history_user_id ON query_history(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_query_history_query_time ON query_history(query_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id)")
            
            conn.commit()
            logger.info("数据库初始化完成")
    
    @asynccontextmanager
    def get_connection_sync(self):
        """获取同步数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接"""
        conn = None
        try:
            # 在线程池中执行数据库操作
            loop = asyncio.get_event_loop()
            conn = await loop.run_in_executor(None, self.get_connection_sync)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """创建用户"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._create_user_sync, user_data)
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return None

    def _create_user_sync(self, user_data: Dict[str, Any]) -> Optional[str]:
        """同步创建用户"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")

                cursor = conn.execute("""
                    INSERT INTO users (id, username, email, password_hash, full_name, avatar_url)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_data['id'],
                    user_data['username'],
                    user_data['email'],
                    user_data['password_hash'],
                    user_data.get('full_name'),
                    user_data.get('avatar_url')
                ))

                # 创建默认用户设置
                conn.execute("""
                    INSERT INTO user_settings (user_id) VALUES (?)
                """, (user_data['id'],))

                conn.commit()
                logger.info(f"用户创建成功: {user_data['username']}")
                return user_data['id']

        except sqlite3.IntegrityError as e:
            logger.warning(f"用户创建失败，可能已存在: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._get_user_by_username_sync, username)
        except Exception as e:
            logger.error(f"异步获取用户失败: {e}")
            return None

    def _get_user_by_username_sync(self, username: str) -> Optional[Dict[str, Any]]:
        """同步根据用户名获取用户"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM users WHERE username = ? AND is_active = 1
            """, (username,))
            row = cursor.fetchone()
            result = dict(row) if row else None
            conn.close()
            logger.debug(f"查询用户 {username}: {result is not None}")
            return result
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_user_by_email_sync, email)

    def _get_user_by_email_sync(self, email: str) -> Optional[Dict[str, Any]]:
        """同步根据邮箱获取用户"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM users WHERE email = ? AND is_active = 1
            """, (email,))
            row = cursor.fetchone()
            result = dict(row) if row else None
            conn.close()
            logger.debug(f"查询邮箱 {email}: {result is not None}")
            return result
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_user_by_id_sync, user_id)

    def _get_user_by_id_sync(self, user_id: str) -> Optional[Dict[str, Any]]:
        """同步根据ID获取用户"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM users WHERE id = ? AND is_active = 1
                """, (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    async def update_user_login_time(self, user_id: str):
        """更新用户最后登录时间"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._update_user_login_time_sync, user_id)

    def _update_user_login_time_sync(self, user_id: str):
        """同步更新用户最后登录时间"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?
                """, (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"更新登录时间失败: {e}")
    
    async def save_query_history(self, history_data: Dict[str, Any]):
        """保存查询历史"""
        async with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO query_history 
                (id, user_id, ip_address, query_type, result_data, response_time, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                history_data['id'],
                history_data.get('user_id'),
                history_data['ip_address'],
                history_data['query_type'],
                json.dumps(history_data.get('result_data', {})),
                history_data.get('response_time'),
                history_data.get('success', True)
            ))
            conn.commit()
    
    async def get_user_query_stats(self, user_id: str) -> Dict[str, Any]:
        """获取用户查询统计"""
        async with self.get_connection() as conn:
            # 总查询数
            cursor = conn.execute("""
                SELECT COUNT(*) as total_queries FROM query_history WHERE user_id = ?
            """, (user_id,))
            total_queries = cursor.fetchone()[0]
            
            # 今日查询数
            cursor = conn.execute("""
                SELECT COUNT(*) as today_queries FROM query_history 
                WHERE user_id = ? AND DATE(query_time) = DATE('now')
            """, (user_id,))
            today_queries = cursor.fetchone()[0]
            
            # 本月查询数
            cursor = conn.execute("""
                SELECT COUNT(*) as month_queries FROM query_history 
                WHERE user_id = ? AND strftime('%Y-%m', query_time) = strftime('%Y-%m', 'now')
            """, (user_id,))
            month_queries = cursor.fetchone()[0]
            
            # 成功率
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
                FROM query_history WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            success_rate = (result[1] / result[0] * 100) if result[0] > 0 else 0
            
            return {
                "total_queries": total_queries,
                "queries_today": today_queries,
                "queries_this_month": month_queries,
                "success_rate": round(success_rate, 2)
            }


# 全局数据库管理器实例
db_manager = DatabaseManager()
