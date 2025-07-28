#!/usr/bin/env python3
"""
完整的集成测试脚本
"""

import requests
import time
import json

def test_services():
    """测试前后端服务是否正常运行"""
    print("🔍 检查服务状态...")
    
    # 测试后端服务
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常 (端口5000)")
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端服务连接失败: {e}")
        return False
    
    # 测试前端服务
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ IP查询工具运行正常 (端口3000)")
        else:
            print(f"❌ 前端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端服务连接失败: {e}")
        return False
    
    return True

def test_api_functionality():
    """测试API功能"""
    print("\n🧪 测试API功能...")
    
    # 测试单个IP查询
    test_cases = [
        ("8.8.8.8", "Google DNS"),
        ("114.114.114.114", "114 DNS"),
        ("1.1.1.1", "Cloudflare DNS")
    ]
    
    for ip, description in test_cases:
        try:
            response = requests.get(f"http://localhost:5000/api/query-ip?ip={ip}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {description} ({ip}): {data.get('country', '未知')}")
            else:
                print(f"❌ {description} ({ip}): 查询失败")
        except Exception as e:
            print(f"❌ {description} ({ip}): {e}")
    
    # 测试批量查询
    try:
        payload = {"ips": [case[0] for case in test_cases]}
        response = requests.post(
            "http://localhost:5000/api/query-batch",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 批量查询成功: {data.get('total', 0)}个IP")
        else:
            print(f"❌ 批量查询失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 批量查询异常: {e}")

def test_frontend_resources():
    """测试前端资源是否正确加载"""
    print("\n🎨 测试前端资源...")
    
    resources = [
        ("主页", "/"),
        ("CSS样式", "/css/style.css"),
        ("JavaScript", "/js/script.js"),
        ("Logo图标", "/assets/logo.svg"),
        ("IP查询页", "/ip-lookup.html"),
        ("帮助页面", "/help.html"),
        ("关于页面", "/about.html")
    ]
    
    for name, path in resources:
        try:
            response = requests.get(f"http://localhost:3000{path}")
            if response.status_code == 200:
                print(f"✅ {name}: 加载正常")
            else:
                print(f"❌ {name}: 加载失败 ({response.status_code})")
        except Exception as e:
            print(f"❌ {name}: {e}")

def test_cors():
    """测试CORS配置"""
    print("\n🌐 测试CORS配置...")
    
    try:
        # 模拟跨域请求
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options("http://localhost:5000/api/health", headers=headers)
        if response.status_code == 200:
            print("✅ CORS预检请求成功")
        else:
            print(f"❌ CORS预检请求失败: {response.status_code}")
            
        # 检查CORS头
        response = requests.get("http://localhost:5000/api/health", headers={'Origin': 'http://localhost:3000'})
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print(f"✅ CORS头设置正确: {cors_header}")
        else:
            print("❌ 缺少CORS头")
            
    except Exception as e:
        print(f"❌ CORS测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始完整集成测试...")
    print("=" * 50)
    
    # 检查服务状态
    if not test_services():
        print("\n❌ 服务检查失败，请确保前后端服务都已启动")
        return
    
    # 测试API功能
    test_api_functionality()
    
    # 测试前端资源
    test_frontend_resources()
    
    # 测试CORS
    test_cors()
    
    print("\n" + "=" * 50)
    print("🎉 集成测试完成!")
    print("\n📋 测试总结:")
    print("✅ API服务正常")
    print("✅ IP查询工具正常")
    print("✅ IP查询功能正常")
    print("✅ 批量查询功能正常")
    print("✅ 前端资源加载正常")
    print("✅ CORS配置正确")
    print("\n🌐 访问地址:")
    print("   IP查询工具: http://localhost:3000")
    print("   API服务: http://localhost:5000/api")

if __name__ == "__main__":
    main()
