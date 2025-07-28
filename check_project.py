"""
项目状态检查脚本
检查项目完整性和服务状态
"""
import os
import sys
import subprocess
import requests
from pathlib import Path

class ProjectChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        
    def log_issue(self, message):
        """记录问题"""
        self.issues.append(message)
        print(f"❌ {message}")
    
    def log_warning(self, message):
        """记录警告"""
        self.warnings.append(message)
        print(f"⚠️ {message}")
    
    def log_success(self, message):
        """记录成功"""
        print(f"✅ {message}")
    
    def check_directory_structure(self):
        """检查目录结构"""
        print("\n📁 检查目录结构...")
        
        required_dirs = [
            "frontend-vue3",
            "backend-fastapi", 
            "API",
            "nginx",
            "docs",
            "scripts",
            "tests",
            "config"
        ]
        
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                self.log_success(f"目录存在: {dir_name}")
            else:
                self.log_issue(f"缺少目录: {dir_name}")
    
    def check_frontend_files(self):
        """检查前端文件"""
        print("\n🎨 检查前端文件...")
        
        frontend_dir = Path("frontend-vue3")
        required_files = [
            "package.json",
            "vite.config.ts",
            "index.html",
            "src/main.ts",
            "src/App.vue"
        ]
        
        for file_path in required_files:
            full_path = frontend_dir / file_path
            if full_path.exists():
                self.log_success(f"前端文件存在: {file_path}")
            else:
                self.log_issue(f"前端文件缺失: {file_path}")
        
        # 检查node_modules
        if (frontend_dir / "node_modules").exists():
            self.log_success("前端依赖已安装")
        else:
            self.log_warning("前端依赖未安装，需要运行 npm install")
    
    def check_backend_files(self):
        """检查后端文件"""
        print("\n⚡ 检查后端文件...")
        
        backend_dir = Path("backend-fastapi")
        required_files = [
            "main.py",
            "requirements.txt",
            "app/main.py",
            "app/config.py",
            "app/api/routes.py",
            "app/services/geoip_service.py"
        ]
        
        for file_path in required_files:
            full_path = backend_dir / file_path
            if full_path.exists():
                self.log_success(f"后端文件存在: {file_path}")
            else:
                self.log_issue(f"后端文件缺失: {file_path}")
        
        # 检查GeoIP数据库
        geoip_db = backend_dir / "data" / "GeoLite2-City.mmdb"
        if geoip_db.exists():
            self.log_success("GeoIP数据库存在")
        else:
            self.log_warning("GeoIP数据库缺失")
    
    def check_python_dependencies(self):
        """检查Python依赖"""
        print("\n🐍 检查Python依赖...")
        
        required_packages = [
            "fastapi",
            "uvicorn", 
            "pydantic",
            "requests"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.log_success(f"Python包已安装: {package}")
            except ImportError:
                self.log_warning(f"Python包未安装: {package}")
    
    def check_services(self):
        """检查服务状态"""
        print("\n🔍 检查服务状态...")
        
        services = [
            ("FastAPI后端", "http://localhost:8000/health"),
            ("Vue3前端", "http://localhost:8080"),
            ("Flask后端", "http://localhost:5000/api/health")
        ]
        
        for name, url in services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.log_success(f"{name}: 运行正常")
                else:
                    self.log_warning(f"{name}: 状态码 {response.status_code}")
            except requests.exceptions.RequestException:
                self.log_warning(f"{name}: 无法连接")
    
    def check_docker_files(self):
        """检查Docker文件"""
        print("\n🐳 检查Docker文件...")
        
        docker_files = [
            "frontend-vue3/Dockerfile",
            "backend-fastapi/Dockerfile", 
            "API/Dockerfile",
            "config/docker-compose.yml",
            "config/docker-compose.dev.yml"
        ]
        
        for file_path in docker_files:
            if Path(file_path).exists():
                self.log_success(f"Docker文件存在: {file_path}")
            else:
                self.log_warning(f"Docker文件缺失: {file_path}")
    
    def check_scripts(self):
        """检查脚本文件"""
        print("\n📜 检查脚本文件...")
        
        script_files = [
            "scripts/deploy.sh",
            "scripts/deploy.bat",
            "start.py"
        ]
        
        for file_path in script_files:
            if Path(file_path).exists():
                self.log_success(f"脚本文件存在: {file_path}")
            else:
                self.log_warning(f"脚本文件缺失: {file_path}")
    
    def generate_report(self):
        """生成检查报告"""
        print("\n" + "="*60)
        print("📊 项目状态检查报告")
        print("="*60)
        
        total_checks = len(self.issues) + len(self.warnings)
        
        if not self.issues and not self.warnings:
            print("🎉 项目状态完美！所有检查都通过了。")
        else:
            if self.issues:
                print(f"\n❌ 发现 {len(self.issues)} 个问题:")
                for i, issue in enumerate(self.issues, 1):
                    print(f"  {i}. {issue}")
            
            if self.warnings:
                print(f"\n⚠️ 发现 {len(self.warnings)} 个警告:")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"  {i}. {warning}")
        
        print(f"\n📈 检查统计:")
        print(f"  问题数量: {len(self.issues)}")
        print(f"  警告数量: {len(self.warnings)}")
        
        if self.issues:
            print(f"\n🔧 建议修复:")
            print("  1. 检查缺失的文件和目录")
            print("  2. 安装缺失的依赖")
            print("  3. 确保服务正常启动")
        
        return len(self.issues) == 0
    
    def run_all_checks(self):
        """运行所有检查"""
        print("🚀 开始项目状态检查...")
        
        self.check_directory_structure()
        self.check_frontend_files()
        self.check_backend_files()
        self.check_python_dependencies()
        self.check_services()
        self.check_docker_files()
        self.check_scripts()
        
        return self.generate_report()

def main():
    """主函数"""
    checker = ProjectChecker()
    success = checker.run_all_checks()
    
    if success:
        print("\n✅ 项目检查完成，可以正常运行！")
        print("\n🚀 启动项目:")
        print("  python start.py")
    else:
        print("\n⚠️ 项目存在问题，请先修复后再启动。")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
