#!/usr/bin/env python3
"""
项目清理脚本
清理重复文件夹和测试文件，优化项目结构
"""
import os
import shutil
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProjectCleaner:
    """项目清理器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / "cleanup_backup"
        
    def create_backup(self, file_path: Path):
        """创建备份"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir()
        
        backup_path = self.backup_dir / file_path.name
        if file_path.is_file():
            shutil.copy2(file_path, backup_path)
        elif file_path.is_dir():
            shutil.copytree(file_path, backup_path, dirs_exist_ok=True)
        
        logger.info(f"已备份: {file_path} -> {backup_path}")
    
    def remove_duplicate_folders(self):
        """移除重复的文件夹"""
        # 检查是否存在旧的前端文件夹
        old_frontend = self.project_root / "IP查询工具"
        new_frontend = self.project_root / "frontend-vue3"
        
        if old_frontend.exists() and new_frontend.exists():
            logger.info("发现重复的前端文件夹")
            
            # 备份旧文件夹
            self.create_backup(old_frontend)
            
            # 移除旧文件夹
            shutil.rmtree(old_frontend)
            logger.info(f"已移除旧前端文件夹: {old_frontend}")
    
    def organize_test_files(self):
        """整理测试文件"""
        test_files = [
            "test_api.py",
            "test_ip_service.py", 
            "test_validators.py",
            "test_cache.py"
        ]
        
        # 创建tests目录
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            tests_dir.mkdir()
            logger.info(f"创建测试目录: {tests_dir}")
        
        # 移动测试文件
        for test_file in test_files:
            file_path = self.project_root / test_file
            if file_path.exists():
                target_path = tests_dir / test_file
                shutil.move(str(file_path), str(target_path))
                logger.info(f"移动测试文件: {file_path} -> {target_path}")
    
    def clean_temp_files(self):
        """清理临时文件"""
        temp_patterns = [
            "*.pyc",
            "*.pyo", 
            "__pycache__",
            "*.tmp",
            "*.log",
            ".DS_Store",
            "Thumbs.db"
        ]
        
        for pattern in temp_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                    logger.info(f"删除临时文件: {file_path}")
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    logger.info(f"删除临时目录: {file_path}")
    
    def create_gitignore(self):
        """创建或更新.gitignore文件"""
        gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Vue.js
dist/
.nuxt/

# Environment variables
.env
.env.local
.env.*.local

# Cache
.cache/
*.cache

# Backup
*_backup_*/
cleanup_backup/

# Database
*.db
*.sqlite
*.sqlite3

# Temporary files
*.tmp
*.temp
"""
        
        gitignore_path = self.project_root / ".gitignore"
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content.strip())
        
        logger.info(f"创建/更新 .gitignore: {gitignore_path}")
    
    def create_project_structure_doc(self):
        """创建项目结构文档"""
        structure_content = """# 项目结构说明

## 目录结构

```
ip-query-tool/
├── API/                    # 后端API服务
│   ├── api/               # API接口模块
│   ├── utils/             # 工具类
│   ├── logs/              # 日志文件
│   ├── app.py             # Flask应用主文件
│   ├── start.py           # 启动脚本
│   └── requirements.txt   # Python依赖
│
├── frontend-vue3/         # Vue3前端应用
│   ├── src/               # 源代码
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面组件
│   │   ├── services/      # API服务
│   │   ├── types/         # TypeScript类型定义
│   │   └── assets/        # 静态资源
│   ├── public/            # 公共资源
│   └── package.json       # Node.js依赖
│
├── tests/                 # 测试文件
├── docs/                  # 文档
├── README.md              # 项目说明
├── Aotd.md               # 任务跟踪
└── ISSUES_FIXED.md       # 问题修复记录
```

## 文件说明

### 后端 (API/)
- `app.py` - Flask应用主文件，包含API路由
- `api/ip_service.py` - IP查询核心服务
- `utils/` - 工具模块（验证器、缓存、日志等）

### 前端 (frontend-vue3/)
- `src/components/` - 可复用的Vue组件
- `src/views/` - 页面级组件
- `src/services/` - API调用服务
- `src/types/` - TypeScript类型定义

### 配置文件
- `.env.development` - 开发环境配置
- `.env.production` - 生产环境配置
- `requirements.txt` - Python依赖
- `package.json` - Node.js依赖

## 开发指南

### 启动开发环境
1. 后端: `cd API && python start.py`
2. 前端: `cd frontend-vue3 && npm run dev`

### 构建生产版本
1. 前端: `cd frontend-vue3 && npm run build`
2. 后端: 使用WSGI服务器部署

### 测试
- 运行测试: `python -m pytest tests/`
- 代码覆盖率: `python -m pytest --cov=API tests/`
"""
        
        structure_path = self.project_root / "PROJECT_STRUCTURE.md"
        with open(structure_path, 'w', encoding='utf-8') as f:
            f.write(structure_content.strip())
        
        logger.info(f"创建项目结构文档: {structure_path}")
    
    def run_cleanup(self):
        """执行完整的清理流程"""
        logger.info("开始项目清理...")
        
        try:
            # 1. 移除重复文件夹
            self.remove_duplicate_folders()
            
            # 2. 整理测试文件
            self.organize_test_files()
            
            # 3. 清理临时文件
            self.clean_temp_files()
            
            # 4. 创建.gitignore
            self.create_gitignore()
            
            # 5. 创建项目结构文档
            self.create_project_structure_doc()
            
            logger.info("项目清理完成!")
            
        except Exception as e:
            logger.error(f"清理过程中出现错误: {str(e)}")
            raise

if __name__ == "__main__":
    cleaner = ProjectCleaner()
    cleaner.run_cleanup()
