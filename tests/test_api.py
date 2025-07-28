#!/usr/bin/env python3
"""
测试API功能的脚本
"""

import requests
import json

API_BASE = "http://localhost:5000/api"

def test_health():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_single_query():
    """测试单个IP查询"""
    print("\n🔍 测试单个IP查询...")
    test_ips = ["8.8.8.8", "114.114.114.114", "1.1.1.1"]
    
    for ip in test_ips:
        try:
            response = requests.get(f"{API_BASE}/query-ip", params={"ip": ip})
            print(f"查询IP {ip}:")
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  国家: {data.get('country', '未知')}")
                print(f"  城市: {data.get('city', '未知')}")
                print(f"  ISP: {data.get('isp', '未知')}")
            else:
                print(f"  错误: {response.text}")
        except Exception as e:
            print(f"❌ 查询IP {ip} 失败: {e}")

def test_batch_query():
    """测试批量IP查询"""
    print("\n🔍 测试批量IP查询...")
    test_ips = ["8.8.8.8", "114.114.114.114", "1.1.1.1"]
    
    try:
        payload = {"ips": test_ips}
        response = requests.post(
            f"{API_BASE}/query-batch",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"总数: {data.get('total', 0)}")
            print("结果:")
            for result in data.get('results', []):
                ip = result.get('ip', '未知')
                country = result.get('country', '未知')
                city = result.get('city', '未知')
                print(f"  {ip}: {country} - {city}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"❌ 批量查询失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试IP查询API...")
    
    # 测试健康检查
    if not test_health():
        print("❌ 后端服务未启动或不可访问")
        return
    
    # 测试单个查询
    test_single_query()
    
    # 测试批量查询
    test_batch_query()
    
    print("\n✅ API测试完成!")

if __name__ == "__main__":
    main()
