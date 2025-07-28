#!/usr/bin/env python3
"""
优化功能验证脚本
测试所有新增的高级功能
"""
import requests
import json
import time
import asyncio
import concurrent.futures
from typing import List, Dict

# API配置
SYNC_API_BASE = "http://localhost:5000/api"
ASYNC_API_BASE = "http://localhost:5001/api"

class OptimizationTester:
    """优化功能测试器"""
    
    def __init__(self):
        self.results = {}
    
    def test_redis_cache(self):
        """测试Redis缓存功能"""
        print("🔍 测试Redis缓存功能...")
        
        try:
            # 测试缓存统计
            response = requests.get(f"{SYNC_API_BASE}/cache/stats")
            if response.status_code == 200:
                data = response.json()
                cache_type = data.get('data', {}).get('cache_type', 'unknown')
                print(f"   缓存类型: {cache_type}")
                
                # 测试IP查询缓存
                ip = "8.8.8.8"
                
                # 第一次查询（应该缓存）
                start_time = time.time()
                response1 = requests.get(f"{SYNC_API_BASE}/query-ip?ip={ip}")
                first_time = time.time() - start_time
                
                # 第二次查询（应该从缓存获取）
                start_time = time.time()
                response2 = requests.get(f"{SYNC_API_BASE}/query-ip?ip={ip}")
                second_time = time.time() - start_time
                
                print(f"   第一次查询: {first_time:.3f}s")
                print(f"   第二次查询: {second_time:.3f}s")
                
                cache_effective = second_time < first_time * 0.8
                print(f"   缓存效果: {'✅ 有效' if cache_effective else '⚠️ 可能无效'}")
                
                self.results['redis_cache'] = {
                    'status': 'success',
                    'cache_type': cache_type,
                    'cache_effective': cache_effective
                }
                return True
            else:
                print(f"   ❌ 缓存统计API失败: {response.status_code}")
                self.results['redis_cache'] = {'status': 'failed', 'error': 'API failed'}
                return False
                
        except Exception as e:
            print(f"   ❌ Redis缓存测试失败: {e}")
            self.results['redis_cache'] = {'status': 'error', 'error': str(e)}
            return False
    
    def test_async_batch_query(self):
        """测试异步批量查询"""
        print("🔍 测试异步批量查询...")
        
        try:
            # 准备测试数据
            test_ips = ['8.8.8.8', '1.1.1.1', '114.114.114.114', '208.67.222.222']
            
            # 测试异步批量查询
            start_time = time.time()
            response = requests.post(f"{ASYNC_API_BASE}/query-batch",
                                   json={'ips': test_ips},
                                   params={'batch_size': 2})
            async_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    results = data.get('data', {}).get('results', [])
                    success_count = data.get('data', {}).get('success_count', 0)
                    
                    print(f"   异步查询时间: {async_time:.3f}s")
                    print(f"   查询结果: {len(results)}个")
                    print(f"   成功数量: {success_count}个")
                    print(f"   查询类型: {data.get('data', {}).get('query_type', 'unknown')}")
                    
                    # 比较同步查询性能
                    start_time = time.time()
                    sync_response = requests.post(f"{SYNC_API_BASE}/query-batch",
                                                json={'ips': test_ips})
                    sync_time = time.time() - start_time
                    
                    print(f"   同步查询时间: {sync_time:.3f}s")
                    
                    performance_improvement = (sync_time - async_time) / sync_time * 100
                    print(f"   性能提升: {performance_improvement:.1f}%")
                    
                    self.results['async_batch'] = {
                        'status': 'success',
                        'async_time': async_time,
                        'sync_time': sync_time,
                        'performance_improvement': performance_improvement,
                        'success_count': success_count
                    }
                    return True
                else:
                    print(f"   ❌ 异步查询失败: {data.get('message', 'Unknown error')}")
                    self.results['async_batch'] = {'status': 'failed', 'error': data.get('message')}
                    return False
            else:
                print(f"   ❌ 异步API请求失败: {response.status_code}")
                self.results['async_batch'] = {'status': 'failed', 'error': f'HTTP {response.status_code}'}
                return False
                
        except Exception as e:
            print(f"   ❌ 异步批量查询测试失败: {e}")
            self.results['async_batch'] = {'status': 'error', 'error': str(e)}
            return False
    
    def test_monitoring_system(self):
        """测试监控系统"""
        print("🔍 测试监控告警系统...")
        
        try:
            # 测试监控指标
            response = requests.get(f"{SYNC_API_BASE}/monitoring/metrics")
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('data', {}).get('metrics', {})
                print(f"   监控指标数量: {len(metrics)}")
                
                # 显示一些关键指标
                key_metrics = ['request_count', 'response_time', 'error_rate']
                for metric in key_metrics:
                    if metric in metrics:
                        stats = metrics[metric]
                        print(f"   {metric}: {stats}")
                
                # 测试告警信息
                alert_response = requests.get(f"{SYNC_API_BASE}/monitoring/alerts")
                if alert_response.status_code == 200:
                    alert_data = alert_response.json()
                    active_alerts = alert_data.get('data', {}).get('active_alerts', [])
                    alert_history = alert_data.get('data', {}).get('alert_history', [])
                    
                    print(f"   活跃告警: {len(active_alerts)}个")
                    print(f"   告警历史: {len(alert_history)}条")
                    
                    # 测试健康检查
                    health_response = requests.get(f"{SYNC_API_BASE}/monitoring/health")
                    if health_response.status_code == 200:
                        health_data = health_response.json()
                        health_results = health_data.get('data', {})
                        overall_healthy = health_results.get('overall', {}).get('healthy', False)
                        
                        print(f"   系统健康状态: {'✅ 健康' if overall_healthy else '❌ 异常'}")
                        
                        self.results['monitoring'] = {
                            'status': 'success',
                            'metrics_count': len(metrics),
                            'active_alerts': len(active_alerts),
                            'overall_healthy': overall_healthy
                        }
                        return True
                    else:
                        print(f"   ❌ 健康检查API失败: {health_response.status_code}")
                else:
                    print(f"   ❌ 告警API失败: {alert_response.status_code}")
            else:
                print(f"   ❌ 监控指标API失败: {response.status_code}")
            
            self.results['monitoring'] = {'status': 'failed', 'error': 'API failed'}
            return False
            
        except Exception as e:
            print(f"   ❌ 监控系统测试失败: {e}")
            self.results['monitoring'] = {'status': 'error', 'error': str(e)}
            return False
    
    def test_performance_comparison(self):
        """测试性能对比"""
        print("🔍 测试性能对比...")
        
        try:
            test_ips = ['8.8.8.8', '1.1.1.1', '114.114.114.114']
            
            # 测试同步API性能
            sync_times = []
            for _ in range(3):
                start_time = time.time()
                response = requests.post(f"{SYNC_API_BASE}/query-batch", json={'ips': test_ips})
                if response.status_code == 200:
                    sync_times.append(time.time() - start_time)
                time.sleep(0.5)
            
            # 测试异步API性能
            async_times = []
            for _ in range(3):
                start_time = time.time()
                response = requests.post(f"{ASYNC_API_BASE}/query-batch", json={'ips': test_ips})
                if response.status_code == 200:
                    async_times.append(time.time() - start_time)
                time.sleep(0.5)
            
            if sync_times and async_times:
                avg_sync = sum(sync_times) / len(sync_times)
                avg_async = sum(async_times) / len(async_times)
                
                print(f"   同步API平均时间: {avg_sync:.3f}s")
                print(f"   异步API平均时间: {avg_async:.3f}s")
                
                if avg_sync > 0:
                    improvement = (avg_sync - avg_async) / avg_sync * 100
                    print(f"   性能提升: {improvement:.1f}%")
                    
                    self.results['performance'] = {
                        'status': 'success',
                        'sync_avg': avg_sync,
                        'async_avg': avg_async,
                        'improvement': improvement
                    }
                    return True
            
            self.results['performance'] = {'status': 'failed', 'error': 'No valid measurements'}
            return False
            
        except Exception as e:
            print(f"   ❌ 性能对比测试失败: {e}")
            self.results['performance'] = {'status': 'error', 'error': str(e)}
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始优化功能验证...")
        print("=" * 60)
        
        tests = [
            ("Redis缓存集成", self.test_redis_cache),
            ("异步批量查询", self.test_async_batch_query),
            ("监控告警系统", self.test_monitoring_system),
            ("性能对比", self.test_performance_comparison),
        ]
        
        passed = 0
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            
            try:
                result = test_func()
                if result:
                    print(f"   结果: ✅ 通过")
                    passed += 1
                else:
                    print(f"   结果: ❌ 失败")
            except Exception as e:
                print(f"   结果: ❌ 异常 - {e}")
        
        print("\n" + "=" * 60)
        print("📊 优化功能验证结果汇总:")
        
        for test_name, _ in tests:
            test_key = test_name.replace("Redis缓存集成", "redis_cache").replace("异步批量查询", "async_batch").replace("监控告警系统", "monitoring").replace("性能对比", "performance")
            result = self.results.get(test_key, {})
            status = result.get('status', 'unknown')
            
            if status == 'success':
                print(f"   {test_name}: ✅ 成功")
            elif status == 'failed':
                print(f"   {test_name}: ❌ 失败")
            else:
                print(f"   {test_name}: ⚠️ 异常")
        
        print(f"\n🎯 总体结果: {passed}/{len(tests)} 个测试通过")
        
        if passed == len(tests):
            print("🎉 所有优化功能验证通过！")
        else:
            print("⚠️ 部分优化功能需要进一步检查")
        
        return passed == len(tests)

if __name__ == "__main__":
    tester = OptimizationTester()
    tester.run_all_tests()
