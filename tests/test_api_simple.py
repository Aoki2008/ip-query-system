#!/usr/bin/env python3
"""
简单API测试
"""
import requests
import json

def test_endpoints():
    """测试API端点"""
    base_url = "http://localhost:5000/api"
    
    endpoints = [
        "/health",
        "/monitoring/metrics", 
        "/monitoring/alerts",
        "/monitoring/health"
    ]
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            print(f"测试: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  响应: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
            else:
                print(f"  错误: {response.text}")
                
        except Exception as e:
            print(f"  异常: {e}")
        
        print()

if __name__ == "__main__":
    test_endpoints()
