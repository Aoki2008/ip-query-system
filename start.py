"""
IP查询工具 - 统一启动脚本
支持启动前端、后端或完整服务
"""
import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def run_command(self, command, cwd=None, name=""):
        """运行命令并管理进程"""
        try:
            print(f"🚀 启动 {name}...")
            print(f"📍 目录: {cwd}")
            print(f"⚡ 命令: {command}")
            
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append((process, name))
            
            # 实时输出日志
            def output_reader():
                for line in iter(process.stdout.readline, ''):
                    if self.running:
                        print(f"[{name}] {line.strip()}")
                    else:
                        break
            
            thread = threading.Thread(target=output_reader)
            thread.daemon = True
            thread.start()
            
            return process
            
        except Exception as e:
            print(f"❌ 启动 {name} 失败: {e}")
            return None
    
    def start_backend(self):
        """启动FastAPI后端"""
        backend_dir = Path("backend-fastapi")
        if not backend_dir.exists():
            print("❌ backend-fastapi 目录不存在")
            return None
            
        # 检查依赖
        try:
            subprocess.run([sys.executable, "-c", "import fastapi, uvicorn"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("📦 安装FastAPI依赖...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         cwd=backend_dir)
        
        return self.run_command(
            f"{sys.executable} main.py",
            cwd=backend_dir,
            name="FastAPI后端"
        )
    
    def start_frontend(self):
        """启动Vue3前端"""
        frontend_dir = Path("frontend-vue3")
        if not frontend_dir.exists():
            print("❌ frontend-vue3 目录不存在")
            return None
        
        # 检查node_modules
        if not (frontend_dir / "node_modules").exists():
            print("📦 安装前端依赖...")
            subprocess.run(["npm", "install"], cwd=frontend_dir)
        
        return self.run_command(
            "npm run dev",
            cwd=frontend_dir,
            name="Vue3前端"
        )
    
    def start_flask_backend(self):
        """启动Flask后端（兼容性）"""
        api_dir = Path("API")
        if not api_dir.exists():
            print("❌ API 目录不存在")
            return None
            
        return self.run_command(
            f"{sys.executable} app.py",
            cwd=api_dir,
            name="Flask后端"
        )
    
    def check_services(self):
        """检查服务状态"""
        print("\n🔍 检查服务状态...")
        
        services = [
            ("FastAPI后端", "http://localhost:8000/health"),
            ("Vue3前端", "http://localhost:8080"),
            ("Flask后端", "http://localhost:5000/api/health")
        ]
        
        try:
            import requests
            for name, url in services:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {name}: 运行正常")
                    else:
                        print(f"⚠️ {name}: 状态码 {response.status_code}")
                except requests.exceptions.RequestException:
                    print(f"❌ {name}: 无法连接")
        except ImportError:
            print("⚠️ 请安装 requests 库来检查服务状态: pip install requests")
    
    def stop_all(self):
        """停止所有服务"""
        print("\n🛑 停止所有服务...")
        self.running = False
        
        for process, name in self.processes:
            try:
                print(f"🔄 停止 {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} 已停止")
            except subprocess.TimeoutExpired:
                print(f"⚠️ 强制停止 {name}...")
                process.kill()
            except Exception as e:
                print(f"❌ 停止 {name} 失败: {e}")
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n📡 收到信号 {signum}")
        self.stop_all()
        sys.exit(0)

def show_help():
    """显示帮助信息"""
    print("""
🚀 IP查询工具 - 统一启动脚本

用法: python start.py [选项]

选项:
  backend     启动FastAPI后端服务
  frontend    启动Vue3前端服务
  flask       启动Flask后端服务（兼容）
  all         启动所有服务（默认）
  check       检查服务状态
  help        显示此帮助信息

示例:
  python start.py              # 启动所有服务
  python start.py backend      # 只启动后端
  python start.py frontend     # 只启动前端
  python start.py check        # 检查服务状态

服务地址:
  前端: http://localhost:8080
  FastAPI: http://localhost:8000
  Flask API: http://localhost:5000
  API文档: http://localhost:8000/docs
""")

def main():
    """主函数"""
    manager = ServiceManager()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    # 解析命令行参数
    command = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if command == "help":
        show_help()
        return
    
    if command == "check":
        manager.check_services()
        return
    
    print("🎯 IP查询工具 - 现代化全栈应用")
    print("=" * 50)
    
    try:
        if command == "backend":
            manager.start_backend()
        elif command == "frontend":
            manager.start_frontend()
        elif command == "flask":
            manager.start_flask_backend()
        elif command == "all":
            # 启动所有服务
            manager.start_backend()
            time.sleep(3)  # 等待后端启动
            manager.start_frontend()
        else:
            print(f"❌ 未知命令: {command}")
            show_help()
            return
        
        if manager.processes:
            print(f"\n✅ 服务启动完成!")
            print("\n📍 服务地址:")
            print("  前端: http://localhost:8080")
            print("  FastAPI: http://localhost:8000")
            print("  API文档: http://localhost:8000/docs")
            print("\n按 Ctrl+C 停止所有服务")
            
            # 等待所有进程
            try:
                while manager.running:
                    time.sleep(1)
                    # 检查进程是否还在运行
                    active_processes = []
                    for process, name in manager.processes:
                        if process.poll() is None:
                            active_processes.append((process, name))
                        else:
                            print(f"⚠️ {name} 已退出")
                    
                    manager.processes = active_processes
                    if not active_processes:
                        break
                        
            except KeyboardInterrupt:
                pass
            finally:
                manager.stop_all()
    
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        manager.stop_all()

if __name__ == "__main__":
    main()
