#!/usr/bin/env python3
"""
直接测试Flask应用
"""
import sys
import os

# 添加API目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'API'))

try:
    print("导入Flask应用...")
    from app import app
    
    print("创建测试客户端...")
    with app.test_client() as client:
        print("测试基础健康检查...")
        response = client.get('/api/health')
        print(f"健康检查状态码: {response.status_code}")
        print(f"健康检查响应: {response.get_json()}")
        
        print("\n测试监控指标...")
        response = client.get('/api/monitoring/metrics')
        print(f"监控指标状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"监控指标响应: {response.get_json()}")
        else:
            print(f"监控指标错误: {response.get_data(as_text=True)}")
        
        print("\n测试监控告警...")
        response = client.get('/api/monitoring/alerts')
        print(f"监控告警状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"监控告警响应: {response.get_json()}")
        else:
            print(f"监控告警错误: {response.get_data(as_text=True)}")
        
        print("\n测试健康状态...")
        response = client.get('/api/monitoring/health')
        print(f"健康状态状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"健康状态响应: {response.get_json()}")
        else:
            print(f"健康状态错误: {response.get_data(as_text=True)}")

except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
