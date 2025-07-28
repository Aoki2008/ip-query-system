#!/usr/bin/env python3
"""
测试导入导出功能的脚本
"""

import requests
import json
import time

def test_batch_query_and_export():
    """测试批量查询功能，为导出功能提供数据"""
    print("🧪 测试批量查询功能...")
    
    test_ips = ["8.8.8.8", "114.114.114.114", "1.1.1.1", "208.67.222.222", "9.9.9.9"]
    
    try:
        payload = {"ips": test_ips}
        response = requests.post(
            "http://localhost:5000/api/query-batch",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 批量查询成功: {data.get('total', 0)}个IP")
            
            # 显示查询结果
            results = data.get('results', [])
            print("\n查询结果:")
            for result in results:
                ip = result.get('ip', '未知')
                country = result.get('country', '未知')
                city = result.get('city', '未知')
                isp = result.get('isp', '未知')
                print(f"  {ip}: {country} - {city} ({isp})")
            
            return True
        else:
            print(f"❌ 批量查询失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 批量查询异常: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("🔍 测试API端点...")
    
    # 测试健康检查
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API健康检查通过")
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False
    
    # 测试单个IP查询
    try:
        response = requests.get("http://localhost:5000/api/query-ip?ip=8.8.8.8", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 单个IP查询成功: {data.get('country', '未知')}")
        else:
            print(f"❌ 单个IP查询失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 单个IP查询异常: {e}")
    
    return True

def check_frontend_resources():
    """检查前端资源"""
    print("🎨 检查前端资源...")
    
    resources = [
        ("主页", "http://localhost:3000/"),
        ("CSS样式", "http://localhost:3000/css/style.css"),
        ("JavaScript", "http://localhost:3000/js/script.js"),
    ]
    
    for name, url in resources:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: 加载正常")
            else:
                print(f"❌ {name}: 加载失败 ({response.status_code})")
        except Exception as e:
            print(f"❌ {name}: {e}")

def main():
    """主测试函数"""
    print("🚀 开始导入导出功能测试...")
    print("=" * 60)
    
    # 检查API服务
    if not test_api_endpoints():
        print("\n❌ API服务测试失败")
        return
    
    # 检查前端资源
    check_frontend_resources()
    
    # 测试批量查询
    if test_batch_query_and_export():
        print("\n✅ 批量查询功能正常，可以测试导出功能")
    else:
        print("\n❌ 批量查询功能异常")
    
    print("\n" + "=" * 60)
    print("📋 测试说明:")
    print("1. 打开浏览器访问: http://localhost:3000")
    print("2. 切换到'批量查询'标签页")
    print("3. 测试导入功能:")
    print("   - 点击'导入文件'按钮，选择 test_ips.csv 或 test_ips.txt")
    print("   - 或者拖拽文件到拖拽区域")
    print("4. 点击'批量查询'按钮执行查询")
    print("5. 查询完成后测试导出功能:")
    print("   - 点击'导出CSV'按钮")
    print("   - 点击'导出JSON'按钮") 
    print("   - 点击'导出Excel'按钮")
    print("6. 检查下载的文件内容是否正确")
    
    print("\n🎉 功能测试准备完成!")

if __name__ == "__main__":
    main()
