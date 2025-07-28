#!/usr/bin/env python3
"""
测试连接
"""
import requests
import time

def test_backend():
    """测试后端连接"""
    try:
        print("测试后端API连接...")
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return True
    except Exception as e:
        print(f"后端连接失败: {e}")
        return False

def test_async_backend():
    """测试异步后端连接"""
    try:
        print("测试异步API连接...")
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return True
    except Exception as e:
        print(f"异步后端连接失败: {e}")
        return False

def test_frontend():
    """测试前端连接"""
    # 测试多个可能的前端端口
    ports = [9000, 8080, 5173, 3000]

    for port in ports:
        try:
            print(f"测试前端连接 (端口{port})...")
            response = requests.get(f'http://localhost:{port}', timeout=5)
            print(f"状态码: {response.status_code}")
            print(f"响应长度: {len(response.text)} 字符")
            print(f"✅ 前端在端口{port}正常运行")
            return True
        except Exception as e:
            print(f"端口{port}连接失败: {e}")
            continue

    print("❌ 所有前端端口都无法连接")
    return False

if __name__ == "__main__":
    print("🔍 开始连接测试...")
    print("=" * 40)
    
    backend_ok = test_backend()
    print()
    
    async_ok = test_async_backend()
    print()
    
    frontend_ok = test_frontend()
    print()
    
    print("=" * 40)
    print("📊 测试结果:")
    print(f"后端API: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"异步API: {'✅ 正常' if async_ok else '❌ 异常'}")
    print(f"前端应用: {'✅ 正常' if frontend_ok else '❌ 异常'}")
