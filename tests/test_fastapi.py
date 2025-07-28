"""
FastAPI应用测试脚本
"""
import requests
import json
import time

def test_fastapi_api():
    """测试FastAPI API"""
    base_url = "http://localhost:8000"
    
    print("🚀 开始测试FastAPI API...")
    
    # 测试根路径
    try:
        print("\n1. 测试根路径...")
        response = requests.get(f"{base_url}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
    
    # 测试健康检查
    try:
        print("\n2. 测试健康检查...")
        response = requests.get(f"{base_url}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ 健康检查测试失败: {e}")
    
    # 测试API信息
    try:
        print("\n3. 测试API信息...")
        response = requests.get(f"{base_url}/api")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ API信息测试失败: {e}")
    
    # 测试单个IP查询
    try:
        print("\n4. 测试单个IP查询...")
        response = requests.get(f"{base_url}/api/query-ip?ip=8.8.8.8")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"查询成功: {data['data']['ip']}")
            print(f"国家: {data['data']['location']['country']}")
            print(f"查询时间: {data['data']['query_time']:.3f}s")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 单个IP查询测试失败: {e}")
    
    # 测试批量IP查询
    try:
        print("\n5. 测试批量IP查询...")
        batch_data = {
            "ips": ["8.8.8.8", "1.1.1.1", "114.114.114.114"],
            "batch_size": 10
        }
        response = requests.post(
            f"{base_url}/api/query-batch",
            json=batch_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"批量查询成功: {data['data']['total']} 个IP")
            print(f"成功数量: {data['data']['success_count']}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 批量IP查询测试失败: {e}")
    
    # 测试统计信息
    try:
        print("\n6. 测试统计信息...")
        response = requests.get(f"{base_url}/api/stats")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"总请求数: {data['data']['performance']['total_requests']}")
            print(f"平均响应时间: {data['data']['performance']['avg_response_time']:.3f}s")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 统计信息测试失败: {e}")
    
    print("\n✅ FastAPI API测试完成!")

if __name__ == "__main__":
    test_fastapi_api()
