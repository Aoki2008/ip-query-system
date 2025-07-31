"""
启动认证服务
"""
import uvicorn
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 启动FastAPI认证服务...")
    print("服务地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("认证端点: http://localhost:8000/api/auth/")

    try:
        # 直接使用模块路径启动
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # 禁用reload避免问题
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
