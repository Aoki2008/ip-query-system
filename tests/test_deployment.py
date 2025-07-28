"""
容器化部署测试脚本
测试所有服务的健康状态和API功能
"""
import requests
import time
import json
import sys
from typing import Dict, List, Tuple

class DeploymentTester:
    def __init__(self):
        self.base_urls = {
            'nginx': 'http://localhost',
            'frontend': 'http://localhost:8080',
            'fastapi': 'http://localhost:8000',
            'flask': 'http://localhost:5000',
            'nginx_status': 'http://localhost:8081',
            'api_docs': 'http://localhost:8082'
        }
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    def test_service_health(self, service: str, url: str) -> bool:
        """测试服务健康状态"""
        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test(f"{service} 健康检查", True, f"状态码: {response.status_code}")
                return True
            else:
                self.log_test(f"{service} 健康检查", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"{service} 健康检查", False, f"连接失败: {str(e)}")
            return False
    
    def test_api_endpoints(self, service: str, base_url: str) -> bool:
        """测试API端点"""
        endpoints = [
            ('根路径', '/'),
            ('API信息', '/api'),
            ('健康检查', '/health'),
            ('单个IP查询', '/api/query-ip?ip=8.8.8.8'),
            ('统计信息', '/api/stats')
        ]
        
        success_count = 0
        for name, endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    self.log_test(f"{service} {name}", True, f"状态码: {response.status_code}")
                    success_count += 1
                else:
                    self.log_test(f"{service} {name}", False, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_test(f"{service} {name}", False, f"请求失败: {str(e)}")
        
        return success_count == len(endpoints)
    
    def test_batch_query(self, service: str, base_url: str) -> bool:
        """测试批量查询"""
        try:
            data = {
                "ips": ["8.8.8.8", "1.1.1.1", "114.114.114.114"],
                "batch_size": 10
            }
            response = requests.post(
                f"{base_url}/api/query-batch",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data'):
                    self.log_test(f"{service} 批量查询", True, 
                                f"成功查询 {result['data'].get('success_count', 0)} 个IP")
                    return True
                else:
                    self.log_test(f"{service} 批量查询", False, "响应格式错误")
                    return False
            else:
                self.log_test(f"{service} 批量查询", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"{service} 批量查询", False, f"请求失败: {str(e)}")
            return False
    
    def test_frontend_access(self) -> bool:
        """测试前端访问"""
        try:
            response = requests.get(self.base_urls['frontend'], timeout=10)
            if response.status_code == 200 and 'html' in response.headers.get('content-type', ''):
                self.log_test("前端页面访问", True, "页面加载正常")
                return True
            else:
                self.log_test("前端页面访问", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("前端页面访问", False, f"连接失败: {str(e)}")
            return False
    
    def test_nginx_proxy(self) -> bool:
        """测试Nginx代理"""
        try:
            # 测试通过Nginx访问API
            response = requests.get(f"{self.base_urls['nginx']}/api/health", timeout=10)
            if response.status_code == 200:
                self.log_test("Nginx API代理", True, "代理工作正常")
                return True
            else:
                self.log_test("Nginx API代理", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Nginx API代理", False, f"连接失败: {str(e)}")
            return False
    
    def test_api_docs(self) -> bool:
        """测试API文档"""
        try:
            # 测试FastAPI文档
            response = requests.get(f"{self.base_urls['api_docs']}/docs", timeout=10)
            if response.status_code == 200:
                self.log_test("API文档访问", True, "Swagger UI可访问")
                return True
            else:
                self.log_test("API文档访问", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API文档访问", False, f"连接失败: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🚀 开始容器化部署测试...\n")
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        time.sleep(15)
        
        all_passed = True
        
        # 1. 健康检查测试
        print("\n📋 1. 服务健康检查")
        health_tests = [
            ('FastAPI', self.base_urls['fastapi']),
            ('Flask API', self.base_urls['flask']),
            ('前端', self.base_urls['frontend'])
        ]
        
        for service, url in health_tests:
            if not self.test_service_health(service, url):
                all_passed = False
        
        # 2. API功能测试
        print("\n📋 2. API功能测试")
        
        # FastAPI测试
        print("\n🔹 FastAPI测试")
        if not self.test_api_endpoints('FastAPI', self.base_urls['fastapi']):
            all_passed = False
        if not self.test_batch_query('FastAPI', self.base_urls['fastapi']):
            all_passed = False
        
        # Flask API测试
        print("\n🔹 Flask API测试")
        if not self.test_api_endpoints('Flask', self.base_urls['flask']):
            all_passed = False
        if not self.test_batch_query('Flask', self.base_urls['flask']):
            all_passed = False
        
        # 3. 前端测试
        print("\n📋 3. 前端测试")
        if not self.test_frontend_access():
            all_passed = False
        
        # 4. Nginx代理测试
        print("\n📋 4. Nginx代理测试")
        if not self.test_nginx_proxy():
            all_passed = False
        
        # 5. API文档测试
        print("\n📋 5. API文档测试")
        if not self.test_api_docs():
            all_passed = False
        
        # 测试结果汇总
        self.print_summary(all_passed)
        
        return all_passed
    
    def print_summary(self, all_passed: bool):
        """打印测试结果汇总"""
        print("\n" + "="*60)
        print("📊 测试结果汇总")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"总测试数: {total}")
        print(f"通过数: {passed}")
        print(f"失败数: {total - passed}")
        print(f"通过率: {passed/total*100:.1f}%")
        
        if all_passed:
            print("\n🎉 所有测试通过！容器化部署成功！")
            print("\n📍 服务访问地址:")
            print("   主入口: http://localhost")
            print("   前端: http://localhost:8080")
            print("   FastAPI: http://localhost:8000")
            print("   Flask API: http://localhost:5000")
            print("   API文档: http://localhost:8082/docs")
        else:
            print("\n❌ 部分测试失败，请检查服务状态")
            print("\n🔍 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['message']}")

def main():
    """主函数"""
    tester = DeploymentTester()
    success = tester.run_all_tests()
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
